# OPRYXX Authentication System

This module provides JWT-based authentication and role-based access control for the OPRYXX system.

## Features

- JWT-based authentication
- Role-based access control
- Password hashing with bcrypt
- Secure token generation and validation
- Integration with FastAPI

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements-auth.txt
   ```

2. Set up environment variables (recommended):
   ```bash
   # .env file
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## Usage

### 1. Protect a route with authentication:

```python
from fastapi import Depends
from core.auth import get_current_user

@app.get("/protected-route")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

### 2. Require specific role:

```python
from core.auth import require_role

@app.get("/admin-only")
async def admin_route(current_user: User = Depends(require_role("admin"))):
    return {"message": "Admin access granted"}
```

### 3. Get an access token:

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 4. Use the access token:

```bash
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Testing

Run the test suite:

```bash
pytest tests/test_auth.py -v
```

## Security Considerations

- Always use HTTPS in production
- Store secrets in environment variables or a secure vault
- Keep dependencies up to date
- Rotate the SECRET_KEY periodically
- Set appropriate token expiration times
- Implement rate limiting
- Use secure password policies

## API Endpoints

- `POST /token` - Get access token
- `GET /users/me/` - Get current user info
- `GET /protected` - Example protected route
- `GET /health` - Health check
