#!/bin/bash
set -e

echo "🚀 OPRYXX Deployment Script"

# Build and deploy
docker-compose -f docker-compose.deploy.yml build
docker-compose -f docker-compose.deploy.yml up -d

echo "✅ Deployment complete!"
echo "🌐 Application available at: http://localhost:8000"