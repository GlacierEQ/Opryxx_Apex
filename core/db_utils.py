""
Database utilities for query optimization and performance monitoring.
"""
import logging
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union, cast

from sqlalchemy import event, exc, orm
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from core.performance import PerformanceMonitor, monitor_performance
from core.caching import CacheManager, cached
from config.performance import performance_config

# Type variables
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize performance monitor
perf_monitor = PerformanceMonitor()

# Initialize cache
cache = CacheManager()

class QueryProfiler:
    """Database query profiler and optimizer."""
    
    def __init__(self):
        self.queries: List[Dict[str, Any]] = []
        self.slow_queries: List[Dict[str, Any]] = []
        self._enabled = True
        self._lock = threading.Lock()
    
    def record_query(
        self, 
        statement: str, 
        parameters: Optional[Dict[str, Any]] = None,
        duration: float = 0.0,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a database query."""
        if not self._enabled:
            return
            
        query_info = {
            'statement': statement,
            'parameters': parameters or {},
            'duration': duration,
            'timestamp': time.time(),
            'context': context or {}
        }
        
        with self._lock:
            self.queries.append(query_info)
            
            # Track slow queries
            if duration >= performance_config.SLOW_QUERY_THRESHOLD:
                self.slow_queries.append(query_info)
                logger.warning(
                    f"Slow query ({duration:.3f}s): {statement}",
                    extra={'query_info': query_info}
                )
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query statistics."""
        with self._lock:
            total_queries = len(self.queries)
            total_time = sum(q['duration'] for q in self.queries) if self.queries else 0
            avg_time = total_time / total_queries if total_queries > 0 else 0
            
            return {
                'total_queries': total_queries,
                'slow_queries': len(self.slow_queries),
                'total_time': total_time,
                'avg_time': avg_time,
                'slow_query_threshold': performance_config.SLOW_QUERY_THRESHOLD
            }
    
    def reset_stats(self) -> None:
        """Reset query statistics."""
        with self._lock:
            self.queries.clear()
            self.slow_queries.clear()
    
    def enable(self) -> None:
        """Enable query profiling."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable query profiling."""
        self._enabled = False


class DatabaseManager:
    """Enhanced database manager with query optimization and monitoring."""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
        self.profiler = QueryProfiler()
        self._setup_event_listeners()
    
    def _setup_event_listeners(self) -> None:
        """Set up SQLAlchemy event listeners."""
        @event.listens_for(Engine, 'before_cursor_execute')
        def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            conn.info.setdefault('query_start_time', []).append(time.time())
            conn.info.setdefault('query_context', []).append({
                'statement': statement,
                'parameters': parameters
            })
        
        @event.listens_for(Engine, 'after_cursor_execute')
        def after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany, *args
        ):
            total_time = time.time() - conn.info['query_start_time'].pop()
            query_context = conn.info['query_context'].pop()
            
            self.profiler.record_query(
                statement=statement,
                parameters=parameters,
                duration=total_time,
                context=query_context
            )
    
    @contextmanager
    def session_scope(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            session.close()
    
    def execute(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute a raw SQL query with parameters."""
        with self.engine.connect() as conn:
            result = conn.execute(query, params or {})
            return result
    
    def fetch_all(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch all rows from a query."""
        with self.engine.connect() as conn:
            result = conn.execute(query, params or {})
            return [dict(row) for row in result]
    
    def fetch_one(self, query: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Fetch a single row from a query."""
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None
    
    @monitor_performance("bulk_insert")
    def bulk_insert(self, model: Any, data: List[Dict]) -> List[Any]:
        """Bulk insert multiple records."""
        with self.session_scope() as session:
            objects = [model(**item) for item in data]
            session.bulk_save_objects(objects)
            session.flush()
            return objects
    
    def get_query_plan(self, query: str, params: Optional[Dict] = None) -> str:
        """Get the execution plan for a query."""
        explain_query = f"EXPLAIN ANALYZE {query}"
        with self.engine.connect() as conn:
            result = conn.execute(explain_query, params or {})
            return "\n".join(row[0] for row in result)
    
    def optimize_query(self, query: str) -> str:
        """Provide optimization suggestions for a query."""
        # This is a simplified example - in a real application, you might use
        # a query analyzer or provide more sophisticated suggestions
        query_lower = query.lower()
        suggestions = []
        
        if 'select *' in query_lower:
            suggestions.append("Avoid using SELECT * - specify only the columns you need")
            
        if 'like "%' in query_lower:
            suggestions.append("Leading wildcards in LIKE clauses prevent index usage")
            
        if 'order by' in query_lower and 'limit' not in query_lower:
            suggestions.append("Consider adding LIMIT to large result sets")
            
        return "\n".join(suggestions) if suggestions else "No optimization suggestions available"


def with_retry(
    max_retries: int = 3, 
    backoff_factor: float = 0.5,
    exceptions: tuple = (exc.OperationalError, exc.TimeoutError)
):
    ""
    Decorator for retrying database operations.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) reached for {func.__name__}",
                            exc_info=True
                        )
                        raise
                    
                    # Exponential backoff
                    sleep_time = (backoff_factor * (2 ** (retries - 1)))
                    logger.warning(
                        f"Retry {retries}/{max_retries} for {func.__name__} "
                        f"after error: {str(e)}. Retrying in {sleep_time:.2f}s..."
                    )
                    time.sleep(sleep_time)
        return cast(F, wrapper)
    return decorator


def query_to_string(statement, bind=None):
    """Convert a SQLAlchemy query to a string with parameters."""
    if isinstance(statement, orm.Query):
        if bind is None:
            bind = statement.session.get_bind()
        statement = statement.statement
    
    dialect = bind.dialect
    compiler = statement._compiler(dialect)
    
    class LiteralCompiler(compiler.__class__):
        def visit_bindparam(self, bindparam, *args, **kwargs):
            return "'%s'" % bindparam.value
    
    compiler = LiteralCompiler(dialect, statement)
    
    try:
        return compiler.process(statement)
    except Exception as e:
        return str(statement)


def setup_database_events(engine: Engine) -> None:
    """Set up database event listeners."""
    @event.listens_for(engine, 'engine_connect')
    def ping_connection(connection, branch):
        if branch:
            return
        
        # Check if connection is alive, if not, refresh it
        try:
            connection.scalar("SELECT 1")
        except exc.DBAPIError as err:
            if err.connection_invalidated:
                connection.scalar("SELECT 1")
            else:
                raise
    
    @event.listens_for(engine, 'before_execute', retval=True)
    def before_execute(conn, clauseelement, multiparams, params):
        # Add query hints or modify queries here
        return clauseelement, multiparams, params


# Initialize database manager
db_manager: Optional[DatabaseManager] = None

def init_db(engine: Engine) -> DatabaseManager:
    """Initialize the database manager."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager(engine)
        setup_database_events(engine)
    return db_manager

def get_db() -> DatabaseManager:
    """Get the database manager instance."""
    if db_manager is None:
        raise RuntimeError("Database manager not initialized. Call init_db() first.")
    return db_manager
