# VMStation Grafana Dashboards

## Overview

This directory contains enterprise-grade Grafana dashboards for the VMStation monitoring stack. These dashboards provide comprehensive visibility into Kubernetes cluster health, application performance, and infrastructure metrics.

## Dashboards

### 1. VMStation Kubernetes Cluster Overview
**File:** `kubernetes-cluster-dashboard.json`  
**UID:** `vmstation-k8s-overview`

High-level cluster health monitoring with key metrics for nodes, pods, and resource utilization.

**Key Panels:**
- Total Nodes, Running Pods, Failed Pods
- Node CPU and Memory Usage
- Node Status Table

### 2. Node Metrics - Detailed System Monitoring
**File:** `node-dashboard.json`  
**UID:** `node-metrics-detailed`

Detailed system-level metrics for all cluster nodes.

**Key Panels:**
- CPU, Memory, Disk Usage by Node
- Network Traffic by Interface
- System Load Average

### 3. Prometheus Metrics & Health
**File:** `prometheus-dashboard.json`  
**UID:** `prometheus-health`

Monitor Prometheus server health and scrape target status.

**Key Panels:**
- Targets Up/Down Count
- Sample Ingestion Rate
- Query Duration
- Scrape Target Status Table

### 4. Network & DNS Performance
**File:** `network-latency-dashboard.json`  
**UID:** `network-dns-performance`

Monitor network connectivity and DNS resolution via Blackbox Exporter and CoreDNS.

**Key Panels:**
- HTTP Probe Success
- HTTP Latency
- DNS Query Time

### 5. Loki Logs & Aggregation
**File:** `loki-dashboard.json`  
**UID:** `loki-logs`

Enterprise-grade log aggregation with filtering and performance metrics.

**Key Panels:**
- Loki Service Status
- Log Volume by Namespace
- Filtered Log Views

### 6. Syslog Infrastructure Monitoring
**File:** `syslog-dashboard.json`  
**UID:** `syslog-infrastructure`

Monitor centralized syslog server for network devices and external systems.

**Key Panels:**
- Syslog Server Status
- Message Rates
- Critical and Error Logs

### 7. CoreDNS Performance & Health
**File:** `coredns-dashboard.json`  
**UID:** `coredns-performance`

Comprehensive DNS service monitoring with performance analytics.

**Key Panels:**
- CoreDNS Status
- Query Rate by DNS Type
- Response Time Percentiles

### 8. IPMI Hardware Monitoring
**File:** `ipmi-hardware-dashboard.json`  
**UID:** `ipmi-hardware`

Monitor physical server hardware sensors via IPMI/BMC.

**Key Panels:**
- Temperature Sensors
- Fan Speeds
- Power Consumption

## Dashboard Installation

Dashboards are automatically deployed via Grafana ConfigMap:

```bash
kubectl apply -k manifests/
```

## Manual Import

To manually import a dashboard:

1. Access Grafana at `http://<node-ip>:30300`
2. Navigate to Dashboards → Import
3. Upload the JSON file or paste the content
4. Select the Prometheus and Loki datasources
5. Click Import

## Datasources

Dashboards use two primary datasources:

- **Prometheus** (`prometheus.monitoring.svc.cluster.local:9090`)
- **Loki** (`loki.monitoring.svc.cluster.local:3100`)

## Version

- **Grafana Version:** 10.0.0
- **Schema Version:** 27
- **Last Updated:** November 2025
