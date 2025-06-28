"""Health check endpoints for the OPRYXX system."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import psutil
import platform
import socket
import time
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger('health')

router = APIRouter(tags=["System"])

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheckResult(BaseModel):
    name: str
    status: HealthStatus
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SystemHealth(BaseModel):
    status: HealthStatus
    version: str = "1.0.0"  # Should be populated from package version
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Dict[str, HealthCheckResult] = Field(default_factory=dict)
    system: Dict[str, Any] = Field(default_factory=dict)

async def get_system_info() -> Dict[str, Any]:
    """Collect basic system information."""
    return {
        "hostname": socket.gethostname(),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler(),
        },
        "cpu": {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "usage_percent": psutil.cpu_percent(interval=1, percpu=True),
        },
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent,
            "used": psutil.virtual_memory().used,
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent,
        },
    }

async def check_database() -> HealthCheckResult:
    """Check database connectivity."""
    start_time = time.time()
    try:
        # TODO: Replace with actual database connection check
        # Example: await database.execute("SELECT 1")
        time.sleep(0.1)  # Simulate database check
        return HealthCheckResult(
            name="database",
            status=HealthStatus.HEALTHY,
            details={"response_time_ms": round((time.time() - start_time) * 1000, 2)}
        )
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return HealthCheckResult(
            name="database",
            status=HealthStatus.UNHEALTHY,
            details={"error": str(e)}
        )

async def check_external_services() -> HealthCheckResult:
    """Check connectivity to external services."""
    # TODO: Add checks for actual external services
    return HealthCheckResult(
        name="external_services",
        status=HealthStatus.HEALTHY,
        details={"services_checked": 0}
    )

async def check_ai_models() -> HealthCheckResult:
    """Check status of AI models."""
    # TODO: Add checks for AI model availability
    return HealthCheckResult(
        name="ai_models",
        status=HealthStatus.HEALTHY,
        details={"models_checked": 0}
    )

@router.get("/health", response_model=SystemHealth, summary="System Health Check")
async def health_check() -> SystemHealth:
    """
    Perform a comprehensive health check of the system and its dependencies.
    
    Returns:
        SystemHealth: Detailed health status of the system and its components
    """
    start_time = time.time()
    
    # Run all health checks in parallel
    try:
        system_info, db_check, services_check, models_check = await asyncio.gather(
            get_system_info(),
            check_database(),
            check_external_services(),
            check_ai_models(),
        )
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")
    
    # Collect all check results
    checks = {
        db_check.name: db_check,
        services_check.name: services_check,
        models_check.name: models_check,
    }
    
    # Determine overall status
    status = HealthStatus.HEALTHY
    for check in checks.values():
        if check.status == HealthStatus.UNHEALTHY:
            status = HealthStatus.UNHEALTHY
            break
        elif check.status == HealthStatus.DEGRADED and status != HealthStatus.UNHEALTHY:
            status = HealthStatus.DEGRADED
    
    # Add response time
    response_time = (time.time() - start_time) * 1000  # Convert to ms
    logger.info(f"Health check completed in {response_time:.2f}ms")
    
    return SystemHealth(
        status=status,
        system=system_info,
        checks=checks,
    )

@router.get("/health/live", summary="Liveness Check")
async def liveness_check() -> Dict[str, str]:
    """
    Simple liveness check endpoint for container orchestration.
    
    Returns:
        dict: Simple status message
    """
    return {"status": "alive"}

@router.get("/health/ready", summary="Readiness Check")
async def readiness_check() -> Dict[str, str]:
    """
    Readiness check endpoint for container orchestration.
    
    Returns:
        dict: Status indicating if the service is ready to accept traffic
    """
    try:
        # Add any readiness checks here
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")
