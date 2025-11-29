# Monitoring Fixes Documentation

## Overview

This document details common monitoring stack issues encountered and their resolutions.

## Grafana Dashboard Templating Error

### Issue
Dashboard shows: `Error updating options: (intermediate value).map is not a function`

### Root Cause
Missing `templating` section in dashboard JSON.

### Solution
Ensure all dashboards include the `templating` section:
```json
{
  "schemaVersion": 27,
  "title": "Dashboard Name",
  "templating": {
    "list": []
  },
  "panels": [...]
}
```

## Loki Syslog Parse Errors

### Issue
Logs show: `JSONParserErr: Value looks like object, but can't find closing '}' symbol`

### Root Cause
Malformed JSON from upstream syslog sources.

### Solution
1. Existing Loki queries handle parse errors: `| json | __error__=""`
2. Fix upstream syslog-ng JSON configuration
3. Increase `log-msg-size()` if truncation occurs

### Monitoring Parse Errors
```promql
sum(rate({job="syslog"} | json | __error__!="" [5m]))
```

## Prometheus TSDB Corruption

### Issue
- Pod in CrashLoopBackOff
- Logs show: `out of sequence m-mapped chunk for series ref`

### Root Cause
On-disk chunk file corruption from unclean shutdown.

### Automatic Recovery
Prometheus automatically:
1. Detects corrupted mmap chunk files
2. Deletes corrupted chunks
3. Replays WAL to rebuild TSDB
4. Starts serving requests

### Prevention
Already implemented in manifests:
- Startup probe with 20 failures allowed (5 min to start)
- Graceful shutdown: 120s termination grace period
- WAL compression enabled
- Retention limits: 30d/4GB
- Resource limits: 4Gi memory

## Grafana Plugin Installation Failure

### Issue
Pod crashes with: `Get "https://grafana.com/api/plugins/repo/...": context deadline exceeded`

### Root Cause
Grafana can't reach grafana.com to download plugins.

### Solution
Remove the plugin installation environment variable:
```bash
kubectl set env deployment/grafana -n monitoring GF_INSTALL_PLUGINS-
```

## Loki WAL Permission Issues

### Issue
Loki fails to start with permission denied errors on WAL directory.

### Root Cause
Incorrect ownership on hostPath directories.

### Solution
Run the Loki fix playbook:
```bash
ansible-playbook -i inventory/hosts.yml playbooks/fix-loki-config.yaml
```

Or manually fix permissions:
```bash
chown -R 10001:10001 /srv/monitoring_data/loki
chmod -R 755 /srv/monitoring_data/loki
```

## Cross-Cluster Log Forwarding

### Issue
Logs from remote clusters not appearing in Loki.

### Root Cause
- Promtail not configured correctly
- Network connectivity issues
- Loki not accepting external connections

### Solution
1. Deploy Promtail with correct Loki URL:
   ```yaml
   clients:
     - url: http://<masternode-ip>:31100/loki/api/v1/push
   ```

2. Verify connectivity:
   ```bash
   curl -X POST "http://<masternode-ip>:31100/loki/api/v1/push" \
     -H "Content-Type: application/json" \
     -d '{"streams":[{"stream":{"job":"test"},"values":[["'$(date +%s)000000000'","test"]]}]}'
   ```

3. Check Loki is accessible on NodePort 31100

## Quick Deployment Commands

### Deploy Full Stack
```bash
kubectl apply -k manifests/
```

### Restart All Components
```bash
kubectl rollout restart statefulset/prometheus -n monitoring
kubectl rollout restart statefulset/loki -n monitoring
kubectl rollout restart deployment/grafana -n monitoring
```

### Check Health
```bash
# Prometheus
curl http://<node-ip>:30090/-/healthy

# Loki
curl http://<node-ip>:31100/ready

# Grafana
curl http://<node-ip>:30300/api/health
```

## References

- [Prometheus Troubleshooting](https://prometheus.io/docs/prometheus/latest/troubleshooting/)
- [Loki Troubleshooting](https://grafana.com/docs/loki/latest/operations/troubleshooting/)
- [Grafana Troubleshooting](https://grafana.com/docs/grafana/latest/troubleshooting/)
