# Monitoring Stack Ansible Automation

Automated deployment and management of the VMStation monitoring stack.

## Prerequisites

- Ansible 2.12+
- Python 3.8+
- Access to target Kubernetes cluster
- kubectl configured on target nodes

## Installation

Install required Ansible collections:

```bash
ansible-galaxy collection install -r requirements.yml
```

## Directory Structure

```
ansible/
├── ansible.cfg              # Ansible configuration
├── requirements.yml         # Required Ansible collections
├── inventory/
│   └── hosts.yml            # Inventory file
├── playbooks/
│   ├── deploy-monitoring-stack.yaml      # Full stack deployment
│   ├── fix-loki-config.yaml              # Loki configuration fixes
│   ├── remediate-monitoring.yaml         # Auto-remediation
│   ├── update-grafana-dashboards.yaml    # Dashboard updates
│   ├── backup-monitoring-data.yaml       # Data backup
│   ├── restore-monitoring-data.yaml      # Data restore
│   └── configure-cross-cluster-monitoring.yaml  # Cross-cluster setup
├── roles/
│   ├── prometheus/          # Prometheus deployment role
│   ├── grafana/             # Grafana deployment role
│   ├── loki/                # Loki deployment role
│   ├── promtail/            # Promtail deployment role
│   └── exporters/           # Exporters deployment role
└── files/
    └── dashboards -> ../../dashboards/   # Symlink to dashboards
```

## Playbooks

### Deploy Monitoring Stack

Deploy the complete monitoring stack:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy-monitoring-stack.yaml
```

### Fix Loki Configuration

Fix Loki configuration drift and permission issues:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/fix-loki-config.yaml
```

### Remediate Monitoring Issues

Auto-remediate common monitoring stack issues:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/remediate-monitoring.yaml
```

### Update Grafana Dashboards

Update Grafana dashboards from repository:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/update-grafana-dashboards.yaml
```

### Backup Monitoring Data

Backup Prometheus, Grafana, and Loki data:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/backup-monitoring-data.yaml
```

With custom backup directory:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/backup-monitoring-data.yaml \
  -e "backup_base_dir=/custom/backup/path"
```

### Restore Monitoring Data

Restore monitoring data from backup:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/restore-monitoring-data.yaml \
  -e "restore_from=/srv/backups/monitoring/2024-01-15-1430"
```

### Configure Cross-Cluster Monitoring

Set up monitoring agents on remote clusters:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/configure-cross-cluster-monitoring.yaml
```

## Roles

### prometheus

Deploys Prometheus with:
- RBAC configuration
- ConfigMap with scrape targets
- StatefulSet/Deployment
- Service with NodePort

### grafana

Deploys Grafana with:
- Datasource configuration
- Dashboard provisioning
- Deployment
- Service with NodePort

### loki

Deploys Loki with:
- Proper directory permissions
- ConfigMap configuration
- StatefulSet/Deployment
- Service with NodePort

### promtail

Deploys Promtail with:
- RBAC configuration
- ConfigMap with log collection config
- DaemonSet

### exporters

Deploys exporters:
- Node Exporter (DaemonSet)
- Kube-State-Metrics
- Blackbox Exporter
- IPMI Exporter (optional)

## Configuration

### Inventory Variables

Key variables in `inventory/hosts.yml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `monitoring_namespace` | Kubernetes namespace | `monitoring` |
| `prometheus_nodeport` | Prometheus NodePort | `30090` |
| `grafana_nodeport` | Grafana NodePort | `30300` |
| `loki_nodeport` | Loki NodePort | `31100` |

### Role Variables

Each role has default variables in `roles/<role>/defaults/main.yml` that can be overridden.

## Troubleshooting

### Pods in CrashLoopBackOff

Run the remediation playbook:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/remediate-monitoring.yaml
```

### Permission Errors

The playbooks automatically fix permissions, but you can manually verify:

```bash
ls -la /srv/monitoring_data/
```

### Check Logs

```bash
kubectl logs -n monitoring -l app=prometheus --tail=50
kubectl logs -n monitoring -l app=grafana --tail=50
kubectl logs -n monitoring -l app=loki --tail=50
```

## License

Apache License 2.0
