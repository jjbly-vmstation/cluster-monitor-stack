# Monitoring Stack Troubleshooting Guide

## Common Issues and Solutions

### Prometheus Issues

#### Prometheus Pod Not Starting

**Symptoms:**
- Pod stuck in `Pending` or `CrashLoopBackOff`
- PVC not bound

**Solutions:**
1. Check PVC status:
   ```bash
   kubectl get pvc -n monitoring
   ```

2. Check for sufficient resources:
   ```bash
   kubectl describe node <node-name>
   ```

3. Check pod events:
   ```bash
   kubectl describe pod prometheus-0 -n monitoring
   ```

#### TSDB Corruption

**Symptoms:**
- Logs show "out of sequence m-mapped chunk"
- Pod restarts frequently

**Solution:**
Prometheus has automatic recovery. If issues persist:
```bash
# Delete corrupted data (last resort)
kubectl exec -n monitoring prometheus-0 -- rm -rf /prometheus/wal/*
kubectl delete pod prometheus-0 -n monitoring
```

#### High Memory Usage

**Solution:**
Adjust retention in prometheus configmap:
```yaml
--storage.tsdb.retention.time=15d
--storage.tsdb.retention.size=2GB
```

### Grafana Issues

#### Dashboard Shows "No Data"

**Causes:**
1. Datasource misconfigured
2. Prometheus not scraping targets
3. Time range too narrow

**Solutions:**
1. Test datasource: Configuration → Data Sources → Test
2. Check Prometheus targets: Status → Targets
3. Expand time range

#### Plugin Installation Fails

**Symptoms:**
- `context deadline exceeded` errors
- Pod in CrashLoopBackOff

**Solution:**
Remove the GF_INSTALL_PLUGINS environment variable if plugin download fails:
```bash
kubectl set env deployment/grafana -n monitoring GF_INSTALL_PLUGINS-
```

### Loki Issues

#### Logs Not Appearing

**Causes:**
1. Promtail not running
2. Loki not accepting connections
3. Wrong label selectors

**Solutions:**
1. Check Promtail pods:
   ```bash
   kubectl get pods -n monitoring -l app=promtail
   ```

2. Check Loki health:
   ```bash
   kubectl exec -n monitoring loki-0 -- curl -s localhost:3100/ready
   ```

3. Verify Promtail config is pointing to correct Loki URL

#### WAL Permission Errors

**Symptoms:**
- `permission denied` errors in Loki logs
- Pod fails to start

**Solution:**
Fix directory permissions:
```bash
ansible-playbook -i inventory/hosts.yml playbooks/fix-loki-config.yaml
```

### Node Exporter Issues

#### Missing Metrics

**Causes:**
1. Node exporter not running on all nodes
2. Firewall blocking port 9100

**Solutions:**
1. Check DaemonSet status:
   ```bash
   kubectl get daemonset node-exporter -n monitoring
   ```

2. Verify port is accessible:
   ```bash
   curl http://<node-ip>:9100/metrics
   ```

### General Debugging Commands

```bash
# Get all monitoring pods
kubectl get pods -n monitoring -o wide

# Get pod logs
kubectl logs -n monitoring <pod-name> --tail=100

# Get events
kubectl get events -n monitoring --sort-by='.lastTimestamp'

# Describe failing pod
kubectl describe pod -n monitoring <pod-name>

# Check resource usage
kubectl top pods -n monitoring

# Check ConfigMaps
kubectl get configmap -n monitoring

# Restart a deployment
kubectl rollout restart deployment/<name> -n monitoring

# Restart a StatefulSet
kubectl rollout restart statefulset/<name> -n monitoring
```

## Health Check Script

Create a quick health check:

```bash
#!/bin/bash
echo "=== Monitoring Stack Health Check ==="

echo -e "\n--- Pod Status ---"
kubectl get pods -n monitoring

echo -e "\n--- Prometheus Health ---"
curl -s http://localhost:30090/-/healthy && echo "OK" || echo "FAILED"

echo -e "\n--- Loki Health ---"
curl -s http://localhost:31100/ready && echo "OK" || echo "FAILED"

echo -e "\n--- Grafana Health ---"
curl -s http://localhost:30300/api/health | jq . || echo "FAILED"

echo -e "\n--- PVC Status ---"
kubectl get pvc -n monitoring
```

## Escalation

If issues persist:
1. Collect logs from all monitoring components
2. Check node resource availability
3. Review recent changes to manifests
4. Check network connectivity between components
