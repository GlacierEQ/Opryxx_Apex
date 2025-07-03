""
OPRYXX API - Main Application

Provides RESTful API endpoints for the OPRYXX system with JWT authentication.
"""
    title="OPRYXX API",
    description="API for OPRYXX Recovery and Optimization System",
    version="2.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    roles: list[str] = []

class UserInDB(UserBase):
    hashed_password: str

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token login, get an access token for future requests."""
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoints
@app.get("/users/me/", response_model=UserBase)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "2.0.0"}

# Example protected endpoint
@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Example protected route that requires authentication."""
    return {"message": f"Hello {current_user.username}", "roles": current_user.roles}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
