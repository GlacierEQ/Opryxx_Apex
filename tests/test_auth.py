""
Tests for the authentication system.
"""
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass123"
TEST_ROLES = ["user"]

# Fixtures
@pytest.fixture
def test_user():
    hashed_password = get_password_hash(TEST_PASSWORD)
    return User(
        username=TEST_USERNAME,
        hashed_password=hashed_password,
        roles=TEST_ROLES
    )

# Unit Tests
def test_password_hashing():
    """Test password hashing and verification."""
    password = "securepassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_authenticate_user_success(test_user):
    """Test successful user authentication."""
    """Test authentication with wrong password."""
    user = authenticate_user(TEST_USERNAME, "wrongpassword")
    assert user is None

def test_authenticate_nonexistent_user():
    """Test authentication with non-existent user."""
    user = authenticate_user("nonexistent", "password")
    assert user is None

# Integration Tests
def test_login_success():
    """Test successful login and token retrieval."""
        "/token",
        data={"username": "admin", "password": "admin123"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials."""
        "/token",
        data={"username": "wrong", "password": "wrong"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_protected_route_without_token():
    """Test accessing protected route without token."""
    response = client.get("/protected")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_protected_route_with_token():
    """Test accessing protected route with valid token."""
        "/token",
        data={"username": "admin", "password": "admin123"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    token = token_response.json()["access_token"]
    
    # Use the token to access protected route
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "Hello admin" in response.json()["message"]

# Run tests
if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main(["-v", "-s", __file__]))
