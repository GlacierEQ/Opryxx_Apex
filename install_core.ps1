# Install core dependencies in smaller batches to avoid disk space issues
Write-Host "Installing core dependencies..."
python -m pip install --upgrade pip

# Core runtime
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-multipart==0.0.6 python-jose[cryptography]==3.3.0

# Database
pip install sqlalchemy==2.0.23 psycopg2-binary==2.9.9 redis==5.0.1

# Utilities
pip install python-dotenv==1.0.0 pydantic-settings==2.1.0

Write-Host "Core installation complete!"
