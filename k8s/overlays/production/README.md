# OPRYXX Production Environment

This directory contains the Kubernetes manifests and configurations for deploying the OPRYXX application in a production environment.

## Directory Structure

```
k8s/overlays/production/
├── README.md                   # This file
├── configmap-patch.yaml        # Production-specific ConfigMap overrides
├── deployment-patch.yaml       # Production deployment configuration
├── hpa-patch.yaml              # Horizontal Pod Autoscaler configuration
├── kustomization.yaml          # Kustomize configuration for production
├── monitoring/                 # Monitoring and alerting configurations
│   ├── alertmanager-config.yaml # AlertManager configuration
│   ├── grafana-dashboard.yaml  # Grafana dashboard definitions
│   ├── kustomization.yaml      # Kustomize config for monitoring
│   ├── prometheus-rule-patch.yaml # Custom Prometheus alert rules
│   └── service-monitor-patch.yaml # ServiceMonitor configuration
├── pdb-patch.yaml             # Pod Disruption Budget configuration
├── secrets.env                # Template for production secrets (DO NOT COMMIT)
└── service-patch.yaml         # Production service configuration
```

## Prerequisites

1. Kubernetes cluster (v1.21+ recommended)
2. `kubectl` configured to communicate with your cluster
3. `kustomize` (v4.5.0+ recommended)
4. Access to the container registry where OPRYXX images are stored
5. Required secrets configured in your Kubernetes cluster

## Deployment

### 1. Configure Secrets

Create a `secrets.env` file in this directory with the following variables:

```env
# Database
DB_USER=opryxx_prod_user
DB_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_secure_redis_password

# Monitoring
SENTRY_DSN=your_sentry_dsn
NEW_RELIC_LICENSE_KEY=your_new_relic_key

# Alerting
SLACK_API_URL=https://hooks.slack.com/services/...
PAGERDUTY_ROUTING_KEY=your_pagerduty_key
OPSGENIE_API_KEY=your_opsgenie_key
```

**WARNING:** Never commit the `secrets.env` file to version control. It's included in `.gitignore` by default.

### 2. Set Environment Variables

Set the following environment variables or update them in your CI/CD pipeline:

```bash
export IMAGE_TAG=v1.0.0
# Optional: export IMAGE_DIGEST=sha256:...
export KUSTOMIZE_CHECKSUM=$(find . -type f -name "*.yaml" -o -name "*.env" | sort | xargs cat | sha256sum | awk '{print $1}')
```

### 3. Deploy with Kustomize

```bash
# Preview the resources that will be created
kustomize build .

# Apply the configuration to your cluster
kubectl apply -k .

# Or with kustomize
kustomize build . | kubectl apply -f -
```

## Monitoring and Observability

The production deployment includes comprehensive monitoring with:

- **Prometheus** for metrics collection
- **Grafana** for visualization
- **AlertManager** for alert routing and notifications

### Accessing Dashboards

1. **Grafana**:
   - URL: `https://grafana.your-domain.com`
   - Default credentials: `admin/admin` (change after first login)
   - Dashboards are automatically imported from the `grafana-dashboard.yaml` file

2. **Prometheus**:
   - URL: `https://prometheus.your-domain.com`
   - Use the PromQL query language to explore metrics

3. **AlertManager**:
   - URL: `https://alertmanager.your-domain.com`
   - View and manage active alerts

## Scaling

The deployment includes a Horizontal Pod Autoscaler (HPA) that automatically scales the application based on CPU and memory usage. You can adjust the scaling parameters in `hpa-patch.yaml`.

```yaml
spec:
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## Upgrading

To upgrade the application:

1. Update the `IMAGE_TAG` environment variable to the new version
2. Run the deployment command again:
   ```bash
   kubectl apply -k .
   ```

## Rollback

If you need to rollback to a previous version:

```bash
# Find the previous deployment revision
kubectl rollout history deployment/opryxx -n opryxx-production

# Rollback to a specific revision
kubectl rollout undo deployment/opryxx -n opryxx-production --to-revision=<revision-number>
```

## Maintenance

### Database Backups

Database backups are configured via a CronJob. The schedule and retention policy can be adjusted in the `backup` directory.

### Logs

Application logs can be accessed using:

```bash
# View logs for all pods in the namespace
kubectl logs -l app=opryxx -n opryxx-production --tail=100 -f

# View logs for a specific pod
kubectl logs <pod-name> -n opryxx-production
```

## Troubleshooting

### Common Issues

1. **Pods in CrashLoopBackOff**
   - Check logs: `kubectl logs <pod-name> -n opryxx-production --previous`
   - Verify environment variables and secrets
   - Check resource limits and requests

2. **Services Not Accessible**
   - Check service endpoints: `kubectl get endpoints <service-name> -n opryxx-production`
   - Verify network policies
   - Check ingress configuration

3. **High Resource Usage**
   - Check current resource usage: `kubectl top pods -n opryxx-production`
   - Review HPA status: `kubectl get hpa -n opryxx-production`
   - Adjust resource requests/limits if needed

## Security Considerations

- All secrets are stored as Kubernetes Secrets
- Network policies restrict pod-to-pod communication
- Pod security policies enforce security contexts
- Regular security scans are performed on container images

## Support

For issues not covered in this guide, please contact the DevOps team at devops@opryxx.com.
