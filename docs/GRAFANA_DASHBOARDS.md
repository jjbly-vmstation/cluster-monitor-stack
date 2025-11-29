# Grafana Dashboards Documentation

## Overview

This document describes the Grafana dashboards included in the VMStation monitoring stack and how to use them effectively.

## Available Dashboards

### Cluster Overview Dashboard
- **UID:** vmstation-k8s-overview
- **Purpose:** High-level cluster health at a glance
- **Key Metrics:**
  - Total nodes and pods
  - CPU and memory usage trends
  - Node status table

### Node Metrics Dashboard
- **UID:** node-metrics-detailed
- **Purpose:** Detailed system metrics per node
- **Key Metrics:**
  - CPU, memory, disk utilization
  - Network traffic
  - System load

### Prometheus Health Dashboard
- **UID:** prometheus-health
- **Purpose:** Monitor Prometheus itself
- **Key Metrics:**
  - Scrape targets status
  - Sample ingestion rate
  - TSDB storage metrics

### Loki Logs Dashboard
- **UID:** loki-logs
- **Purpose:** Log aggregation and analysis
- **Features:**
  - Namespace filtering
  - Log volume trends
  - Application log viewer

### CoreDNS Dashboard
- **UID:** coredns-performance
- **Purpose:** DNS performance monitoring
- **Key Metrics:**
  - Query rates by type
  - Response time percentiles
  - Cache hit ratio

### Network Latency Dashboard
- **UID:** network-dns-performance
- **Purpose:** Network and HTTP probe monitoring
- **Key Metrics:**
  - Probe success/failure
  - HTTP latency
  - DNS query time

### Syslog Dashboard
- **UID:** syslog-infrastructure
- **Purpose:** Centralized syslog monitoring
- **Key Metrics:**
  - Message rates
  - Severity distribution
  - Critical event logs

### IPMI Hardware Dashboard
- **UID:** ipmi-hardware
- **Purpose:** Physical server hardware monitoring
- **Key Metrics:**
  - Temperature sensors
  - Fan speeds
  - Power consumption

## Common Queries

### Prometheus (PromQL)

```promql
# CPU usage percentage
100 - (avg by (node) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage percentage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Pod count by namespace
sum by (namespace) (kube_pod_info)

# Disk usage percentage
(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100
```

### Loki (LogQL)

```logql
# All logs from monitoring namespace
{namespace="monitoring"}

# Error logs across all namespaces
{job=~".+"} |~ "(?i)error|exception|fatal"

# Logs from a specific pod
{pod="prometheus-0"}

# Log rate by namespace
sum by (namespace) (rate({job=~".+"}[1m]))
```

## Accessing Dashboards

1. Open Grafana at `http://<node-ip>:30300`
2. Navigate to Dashboards → Browse
3. Select the desired dashboard

## Customization

Dashboards can be customized:
- Edit panels in the Grafana UI
- Adjust time ranges and refresh intervals
- Add new panels as needed
- Changes are preserved if saved

## Troubleshooting

### "No Data" in Panels
1. Check that the datasource is configured correctly
2. Verify Prometheus/Loki is accessible
3. Extend the time range
4. Check if the required exporters are running

### Slow Dashboard Loading
1. Reduce the time range (use 1h instead of 24h)
2. Increase refresh interval (use 1m instead of 10s)
3. Simplify complex queries

### Dashboard Import Errors
1. Validate JSON syntax
2. Ensure schema version matches Grafana version
3. Check for duplicate UIDs
