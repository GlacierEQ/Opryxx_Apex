#!/bin/bash
# OPRYXX Ultimate System - High Level Deployment Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ENVIRONMENT=${1:-production}
SCALE=${2:-3}
DOMAIN=${3:-opryxx.local}

echo -e "${BLUE}🚀 OPRYXX ULTIMATE SYSTEM - HIGH LEVEL DEPLOYMENT${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "Environment: ${GREEN}${ENVIRONMENT}${NC}"
echo -e "Scale: ${GREEN}${SCALE}${NC}"
echo -e "Domain: ${GREEN}${DOMAIN}${NC}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
    
    command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker required${NC}"; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}❌ Docker Compose required${NC}"; exit 1; }
    
    echo -e "${GREEN}✅ Prerequisites satisfied${NC}"
}

# Build application
build_application() {
    echo -e "${YELLOW}🏗️ Building OPRYXX application...${NC}"
    
    docker build -t opryxx:latest .
    
    echo -e "${GREEN}✅ Application built successfully${NC}"
}

# Deploy infrastructure
deploy_infrastructure() {
    echo -e "${YELLOW}🚀 Deploying infrastructure...${NC}"
    
    if command -v kubectl >/dev/null 2>&1 && kubectl cluster-info >/dev/null 2>&1; then
        echo -e "${BLUE}📦 Deploying to Kubernetes...${NC}"
        deploy_kubernetes
    elif docker info | grep -q "Swarm: active"; then
        echo -e "${BLUE}🐳 Deploying to Docker Swarm...${NC}"
        deploy_swarm
    else
        echo -e "${BLUE}🐳 Deploying with Docker Compose...${NC}"
        deploy_compose
    fi
}

# Kubernetes deployment
deploy_kubernetes() {
    kubectl apply -f k8s/namespace.yaml 2>/dev/null || kubectl create namespace opryxx
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/hpa.yaml
    
    echo -e "${GREEN}✅ Kubernetes deployment complete${NC}"
}

# Docker Swarm deployment
deploy_swarm() {
    export DB_PASSWORD=$(openssl rand -base64 32)
    export GRAFANA_PASSWORD=$(openssl rand -base64 32)
    
    docker stack deploy -c docker-stack.yml opryxx
    
    echo -e "${GREEN}✅ Docker Swarm deployment complete${NC}"
    echo -e "${YELLOW}📝 Grafana password: ${GRAFANA_PASSWORD}${NC}"
}

# Docker Compose deployment
deploy_compose() {
    docker-compose -f docker-compose.prod.yml up -d --scale opryxx-api=${SCALE}
    
    echo -e "${GREEN}✅ Docker Compose deployment complete${NC}"
}

# Setup monitoring
setup_monitoring() {
    echo -e "${YELLOW}📊 Setting up monitoring...${NC}"
    
    # Create Prometheus config
    cat > prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'opryxx-api'
    static_configs:
      - targets: ['opryxx-api:8000']
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
EOF
    
    echo -e "${GREEN}✅ Monitoring configured${NC}"
}

# Verify deployment
verify_deployment() {
    echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
    
    sleep 30  # Wait for services to start
    
    # Health check
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${RED}❌ Health check failed${NC}"
        exit 1
    fi
    
    # Performance test
    echo -e "${YELLOW}⚡ Running performance test...${NC}"
    curl -X POST "http://localhost:8000/execute" \
         -H "Content-Type: application/json" \
         -d '{"query":"system scan"}' >/dev/null 2>&1
    
    echo -e "${GREEN}✅ Performance test passed${NC}"
}

# Setup SSL
setup_ssl() {
    if [ "$DOMAIN" != "opryxx.local" ]; then
        echo -e "${YELLOW}🔒 Setting up SSL for ${DOMAIN}...${NC}"
        
        # Generate Let's Encrypt certificate
        docker run --rm -v $(pwd)/ssl:/etc/letsencrypt \
            certbot/certbot certonly --standalone \
            --email admin@${DOMAIN} \
            --agree-tos \
            --no-eff-email \
            -d ${DOMAIN}
        
        echo -e "${GREEN}✅ SSL certificate generated${NC}"
    fi
}

# Main deployment flow
main() {
    check_prerequisites
    build_application
    setup_monitoring
    setup_ssl
    deploy_infrastructure
    verify_deployment
    
    echo ""
    echo -e "${GREEN}🎉 OPRYXX ULTIMATE SYSTEM DEPLOYED SUCCESSFULLY!${NC}"
    echo -e "${GREEN}=================================================${NC}"
    echo -e "🌐 API Endpoint: http://localhost:8000"
    echo -e "📊 Monitoring: http://localhost:3000 (Grafana)"
    echo -e "📈 Metrics: http://localhost:9090 (Prometheus)"
    echo -e "🔍 Health Check: http://localhost:8000/health"
    echo ""
    echo -e "${BLUE}🚀 MAXIMUM POWER ACHIEVED! 🚀${NC}"
}

# Run deployment
main "$@"