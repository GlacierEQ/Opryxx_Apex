"""
Tests for database utilities and query optimization.
"""
import pytest
import time
import sqlite3
from unittest.mock import patch, MagicMock, call
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.db_utils import (
    DatabaseManager,
    QueryProfiler,
    with_retry,
    query_to_string,
    setup_database_events
)

# Test models
Base = declarative_base()

class TestModel(Base):
    __tablename__ = 'test_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    value = Column(Integer)


@pytest.fixture
def sqlite_engine(tmp_path):
    """Create an in-memory SQLite database for testing."""
    db_path = tmp_path / "test.db"
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Add test data
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        for i in range(5):
            session.add(TestModel(name=f'test_{i}', value=i))
        session.commit()
    finally:
        session.close()
    
    yield engine
    
    # Cleanup
    engine.dispose()


@pytest.fixture
def db_manager(sqlite_engine):
    """Create a DatabaseManager instance for testing."""
    return DatabaseManager(sqlite_engine)


class TestQueryProfiler:
    """Test query profiling functionality."""
    
    def test_record_query(self):
        """Test recording a query."""
        profiler = QueryProfiler()
        
        # Record a query
        profiler.record_query(
            "SELECT * FROM test",
            {'param': 1},
            0.123,
            {'context': 'test'}
        )
        
        # Verify stats
        stats = profiler.get_query_stats()
        assert stats['total_queries'] == 1
        assert stats['slow_queries'] == 0  # Below default threshold
        
        # Record a slow query
        profiler.record_query(
            "SELECT * FROM test_slow",
            {},
            1.5,  # Above default threshold
            {}
        )
        
        stats = profiler.get_query_stats()
        assert stats['total_queries'] == 2
        assert stats['slow_queries'] == 1
    
    def test_reset_stats(self):
        """Test resetting statistics."""
        profiler = QueryProfiler()
        profiler.record_query("SELECT 1", {}, 0.1, {})
        
        stats = profiler.get_query_stats()
        assert stats['total_queries'] == 1
        
        profiler.reset_stats()
        
        stats = profiler.get_query_stats()
        assert stats['total_queries'] == 0
        assert stats['slow_queries'] == 0


class TestDatabaseManager:
    """Test DatabaseManager functionality."""
    
    def test_session_scope(self, db_manager):
        """Test session scope context manager."""
        with db_manager.session_scope() as session:
            result = session.query(TestModel).count()
            assert result == 5  # From fixture
    
    def test_execute(self, db_manager):
        """Test raw SQL execution."""
        result = db_manager.execute("SELECT COUNT(*) FROM test_table")
        assert result.scalar() == 5
    
    def test_fetch_all(self, db_manager):
        """Test fetching all rows."""
        rows = db_manager.fetch_all("SELECT * FROM test_table WHERE id < :id", {'id': 3})
        assert len(rows) == 2  # IDs 1 and 2
    
    def test_fetch_one(self, db_manager):
        """Test fetching a single row."""
        row = db_manager.fetch_one("SELECT * FROM test_table WHERE id = :id", {'id': 1})
        assert row is not None
        assert row['id'] == 1
    
    def test_bulk_insert(self, db_manager):
        """Test bulk insert operation."""
        data = [
            {'name': 'new_1', 'value': 10},
            {'name': 'new_2', 'value': 20},
        ]
        
        db_manager.bulk_insert(TestModel, data)
        
        # Verify insertion
        with db_manager.session_scope() as session:
            count = session.query(TestModel).filter(TestModel.name.in_(['new_1', 'new_2'])).count()
            assert count == 2
    
    def test_optimize_query(self, db_manager):
        """Test query optimization suggestions."""
        # Test with SELECT *
        suggestions = db_manager.optimize_query("SELECT * FROM test_table")
        assert "specify only the columns you need" in suggestions
        
        # Test with LIKE wildcard
        suggestions = db_manager.optimize_query("SELECT name FROM test_table WHERE name LIKE '%test%'")
        assert "Leading wildcards in LIKE clauses" in suggestions
        
        # Test with ORDER BY but no LIMIT
        suggestions = db_manager.optimize_query("SELECT id FROM test_table ORDER BY name")
        assert "consider adding LIMIT" in suggestions
        
        # Test with no suggestions
        suggestions = db_manager.optimize_query("SELECT id, name FROM test_table WHERE id = 1")
        assert suggestions == "No optimization suggestions available"


def test_with_retry_success():
    """Test retry decorator with successful operation."""
    mock_func = MagicMock(return_value="success")
    
    decorated = with_retry(max_retries=3)(mock_func)
    result = decorated()
    
    assert result == "success"
    mock_func.assert_called_once()


def test_with_retry_failure():
    """Test retry decorator with failing operation."""
    from sqlalchemy.exc import OperationalError
    
    mock_func = MagicMock()
    mock_func.side_effect = OperationalError("connection failed", {}, None)
    
    decorated = with_retry(max_retries=2)(mock_func)
    
    with pytest.raises(OperationalError):
        decorated()
    
    # Should have been called max_retries + 1 times (initial + retries)
    assert mock_func.call_count == 3


def test_query_to_string():
    """Test converting a query to a string."""
    from sqlalchemy import select, table, column
    
    # Test with raw SQL
    sql = "SELECT * FROM test WHERE id = :id"
    params = {'id': 1}
    
    result = query_to_string(sql, params)
    assert "SELECT * FROM test WHERE id = 1" in result
    
    # Test with SQLAlchemy select
    t = table('test', column('id'), column('name'))
    stmt = select(t.c.id, t.c.name).where(t.c.id == 1)
    
    result = query_to_string(stmt)
    assert "SELECT test.id, test.name \nFROM test" in result
    assert "test.id = 1" in result


def test_setup_database_events():
    """Test setting up database event listeners."""
    from sqlalchemy import create_engine, event
    
    engine = create_engine('sqlite:///:memory:')
    
    # Mock event listeners
    before_mock = MagicMock()
    after_mock = MagicMock()
    
    # Setup events
    setup_database_events(engine)
    
    # Add test listeners
    @event.listens_for(engine, 'before_cursor_execute')
    def before_cursor_execute(conn, cursor, statement, params, context, executemany):
        before_mock()
    
    @event.listens_for(engine, 'after_cursor_execute')
    def after_cursor_execute(conn, cursor, statement, params, context, executemany):
        after_mock()
    
    # Execute a query
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    
    # Verify listeners were called
    before_mock.assert_called_once()
    after_mock.assert_called_once()
