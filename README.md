# VMStation Cluster Monitor Stack

Enterprise-grade monitoring and observability stack for Kubernetes clusters.

## Overview

This repository contains a complete monitoring stack deployment including:

- **Prometheus** - Metrics collection and time-series database
- **Grafana** - Visualization and dashboards
- **Loki** - Log aggregation
- **Promtail** - Log collection agent
- **Node Exporter** - System metrics
- **Kube-state-metrics** - Kubernetes object metrics
- **Blackbox Exporter** - HTTP/DNS/ICMP probes
- **IPMI Exporter** - Hardware monitoring

## Quick Start

### Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- 4GB+ RAM available for monitoring workloads
- 50GB+ persistent storage

### Deployment

Deploy the entire monitoring stack using Kustomize:

```bash
kubectl apply -k .
```

Or using Ansible:

```bash
cd ansible
ansible-playbook -i /srv/vmstation-org/cluster-setup/ansible/inventory/hosts.yml playbooks/deploy-monitoring-stack.yaml
```

### Access

After deployment, access the monitoring stack:

| Service    | URL                        | Default Credentials     |
|------------|----------------------------|-------------------------|
| Grafana    | http://\<node-ip\>:30300   | admin/admin (anonymous) |
| Prometheus | http://\<node-ip\>:30090   | N/A                     |
| Loki       | http://\<node-ip\>:31100   | N/A                     |


## Directory Structure

```
cluster-monitor-stack/
├── manifests/           # Kubernetes manifests
├── dashboards/          # Grafana dashboard JSON files
├── ansible/             # Ansible playbooks
├── scripts/             # Utility scripts
```

## Documentation

All detailed monitoring and troubleshooting documentation has been centralized in the [cluster-docs/components/](../cluster-docs/components/) directory. Please refer to that location for:
- Grafana dashboards
- Monitoring fixes
- Troubleshooting

This repository only contains the README and improvements/standards documentation.

## Components

### Prometheus
- StatefulSet deployment with persistent storage
- Enterprise security context (non-root)
- Config reloader sidecar for zero-downtime updates
- NetworkPolicy for controlled access
- Pre-configured alerting rules

### Grafana
- Pre-provisioned datasources (Prometheus, Loki)
- 8 enterprise-grade dashboards
- Anonymous read access enabled
- Dashboard provisioning via ConfigMap

### Loki
- StatefulSet with persistent storage
- Production-tuned ingestion limits
- 30-day log retention
- Compactor for storage optimization

### Promtail
- DaemonSet on all nodes
- Kubernetes pod log collection
- System log forwarding

### Exporters
- Node Exporter on all nodes
- Kube-state-metrics for K8s objects
- Blackbox Exporter for probes
- IPMI Exporter for hardware (optional)

## Dashboards

| Dashboard | Description |
|-----------|-------------|
| Kubernetes Cluster Overview | Cluster health at a glance |
| Node Metrics | Detailed system metrics |
| Prometheus Health | Monitor Prometheus itself |
| Loki Logs | Log aggregation and analysis |
| CoreDNS Performance | DNS metrics and health |
| Network Latency | HTTP/DNS probe monitoring |
| Syslog Infrastructure | Centralized syslog |
| IPMI Hardware | Physical server monitoring |

## Ansible Playbooks

| Playbook | Description |
|----------|-------------|
| `deploy-monitoring-stack.yaml` | Deploy complete stack |
| `fix-loki-config.yaml` | Fix Loki configuration issues |
| `remediate-monitoring.yaml` | Auto-remediate common issues |
| `update-grafana-dashboards.yaml` | Update Grafana dashboards |
| `backup-monitoring-data.yaml` | Backup monitoring data |
| `restore-monitoring-data.yaml` | Restore from backup |
| `configure-cross-cluster-monitoring.yaml` | Set up cross-cluster log forwarding |

### Quick Start with Ansible

```bash
cd ansible

# Install required Ansible collections
ansible-galaxy collection install -r requirements.yml

# Deploy monitoring stack
ansible-playbook -i /srv/vmstation-org/cluster-setup/ansible/inventory/hosts.yml playbooks/deploy-monitoring-stack.yaml

# Fix Loki configuration issues
ansible-playbook -i /srv/vmstation-org/cluster-setup/ansible/inventory/hosts.yml playbooks/fix-loki-config.yaml

# Remediate monitoring issues
ansible-playbook -i /srv/vmstation-org/cluster-setup/ansible/inventory/hosts.yml playbooks/remediate-monitoring.yaml

# Update Grafana dashboards
ansible-playbook -i /srv/vmstation-org/cluster-setup/ansible/inventory/hosts.yml playbooks/update-grafana-dashboards.yaml

# Backup monitoring data
ansible-playbook -i /srv/vmstation-org/cluster-setup/ansible/inventory/hosts.yml playbooks/backup-monitoring-data.yaml

# Restore monitoring data
ansible-playbook -i /srv/vmstation-org/cluster-setup/ansible/inventory/hosts.yml playbooks/restore-monitoring-data.yaml \
  -e "restore_from=/srv/backups/monitoring/YYYY-MM-DD-HHMM"
```

See [ansible/README.md](ansible/README.md) for detailed documentation.

## Configuration

### Customizing Prometheus Scrape Targets

Edit `manifests/prometheus/configmap.yaml` to add or modify scrape targets.

### Adjusting Resource Limits

Edit the respective deployment files in `manifests/*/deployment.yaml`.

### Adding Dashboards

1. Add JSON file to `dashboards/`
2. Redeploy: `kubectl apply -k .` (dashboards are synced onto the NFS-backed Grafana PVC)

## Troubleshooting

### Common Issues

- **Pods not starting**: Check PVC status and node resources
- **No data in Grafana**: Verify datasource configuration
- **Loki WAL errors**: Run `playbooks/fix-loki-config.yaml`

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed guidance.

### Health Checks

```bash
# Check all pods
kubectl get pods -n monitoring

# Prometheus health
curl http://<node-ip>:30090/-/healthy

# Loki health
curl http://<node-ip>:31100/ready

# Grafana health
curl http://<node-ip>:30300/api/health
```

## Documentation

- [Grafana Dashboards](docs/GRAFANA_DASHBOARDS.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- [Monitoring Fixes](docs/MONITORING_FIXES.md)
- [Improvements and Standards](IMPROVEMENTS_AND_STANDARDS.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.
