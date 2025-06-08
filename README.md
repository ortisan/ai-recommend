# AI Recommendation System

This project implements a recommendation system using AI techniques to provide personalized product recommendations based on user behavior. The system uses Kubernetes for orchestration, TiKV for storage, SurrealDB as the database, and Kafka for event streaming.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [Kubernetes Cluster](#kubernetes-cluster)
  - [Database Infrastructure](#database-infrastructure)
  - [SurrealDB Setup](#surrealdb-setup)
  - [Kafka Setup](#kafka-setup)
- [Services](#services)
- [Development](#development)

## Overview

The AI Recommendation System processes e-commerce events (such as product views, purchases, etc.) and uses this data to generate personalized product recommendations for users. The system architecture includes:

- Kubernetes for container orchestration
- TiKV for distributed key-value storage
- SurrealDB for database operations
- Kafka for event streaming
- Observability tools (Prometheus, Grafana, Jaeger, Loki)

## Prerequisites

- Docker and Docker Compose
- Kubernetes CLI (kubectl)
- Helm
- k3d or kind (for local Kubernetes cluster)
- Python 3.8+

## Setup

### Kubernetes Cluster

Create a local Kubernetes cluster using either k3d or kind:

```sh
kind create cluster --name k8s-ai-recommend

# Verify the cluster is running
kubectl cluster-info --context k8s-ai-recommend
```

To delete the cluster when you're done:

```sh
kind delete cluster --name k8s-ai-recommend
```

### Database Infrastructure

#### Install Custom Resource Definitions (CRDs) and TiDB Operator

1. Install the CRDs:

```sh
kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.6.1/manifests/crd.yaml
```

2. Install the TiDB Operator:

```sh
helm repo update
helm install \
    -n tidb-operator \
    --create-namespace \
    tidb-operator \
    pingcap/tidb-operator \
    --version v1.6.1 \
    -f database/tidb-operator/values.yaml

# Check if the TiDB Operator is running
kubectl get all -n tidb-operator
```

> **Note**: There might be issues with tidb-scheduler. The CRD is in version "kubescheduler.config.k8s.io/v1beta2". See related [issue](https://github.com/pingcap/tidb-operator/issues/5462).

To uninstall the TiDB Operator:

```sh
helm uninstall tidb-operator -n tidb-operator
```

#### Install TiKV Cluster

```sh
# Create namespace for TiKV
kubectl create ns tikv

# Apply the TiKV cluster configuration
# Note: This file contains older versions of images
kubectl apply -n tikv -f database/tidb-cluster/tidb-cluster.yaml

# Check if the TiKV cluster is running
kubectl get all -n tikv

# Check the TiDB cluster status
kubectl get -n tikv tidbcluster
```

kubectl apply -n tikv -f database/bastion/bastion.yaml





### SurrealDB Setup

#### Prepare TiKV for SurrealDB

Before deploying SurrealDB, you need to add a special key that SurrealDB uses to detect if it's running in [v2 mode](https://github.com/surrealdb/surrealdb/blob/main/crates/core/src/kvs/ds.rs#L540) (`{"!v": "\u0000\u0002"}`).

1. Add the key to the TiKV database:

```sh
kubectl apply -f database/tikv/tikv-put-surreal-v2-keys/pod.yaml
```

2. Verify the key was added correctly:

```sh
kubectl exec -ti tikv-get-keys -- cat output/tikv_keys.json
```

You should see output like:

```json
{
  "!v": "\u0000\u0002",
  ...
}
```

#### Install SurrealDB

1. Set the TiKV URL environment variable:

```sh 
export TIKV_URL=tikv://basic-pd.tikv:2379
```

2. Install SurrealDB using Helm:

```sh
helm repo add surrealdb https://helm.surrealdb.com
helm repo update
helm install --set surrealdb.path=$TIKV_URL --set surrealdb.unauthenticated=true --set image.tag=latest surrealdb-tikv surrealdb/surrealdb
```

3. Forward the SurrealDB port to access it locally:

```sh
kubectl port-forward svc/surrealdb-tikv 8000
```

#### Install SurrealDB CLI

```sh
brew install surrealdb/tap/surreal
```

#### Create a User in SurrealDB

1. Connect to SurrealDB:

```sh
surreal sql -e http://localhost:8000
```

2. Create a root user:

```sql
DEFINE USER root ON ROOT PASSWORD 'Password' ROLES OWNER;
```

3. Connect with the new user:

```sh
surreal sql -e http://localhost:8000 -u root -p 'Password' 
```

4. Verify the user:

```sql
INFO FOR ROOT
```

#### Visualize SurrealDB

You can use [Surrealist](https://surrealdb.com/surrealist?download) to visualize and interact with your SurrealDB database.

#### Uninstall CRDs (if needed)

```sh
kubectl get crd --no-headers | grep '^tidb' | awk '{print $1, $2}' | xargs -n2 kubectl delete
```

### Kafka Setup

#### Create Protocol Buffers Stubs

```sh
uv run python3 -m grpc_tools.protoc -I=schemas --python_out=ai_recommend/adapter/stub schemas/e-commerce-events.proto
```

#### Create Kafka Topics

```sh
docker-compose exec kafka kafka-topics --create --topic e-commerce-events --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1
```

#### Register Schema with Schema Registry

```sh
curl -X POST http://localhost:8081/subjects/e-commerce-events-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @- <<EOF
{
  "schemaType": "PROTOBUF",
  "schema": "$(cat schemas/e-commerce-events.proto | sed 's/"/\\"/g' | tr -d '\n')"
}
EOF
```

## Notebooks

```sh
uv run jupyter lab --notebook-dir notebooks
```


## Services

The following services are available in the system:

| Service Name    | URL                      | Description                       |
|-----------------|--------------------------|-----------------------------------|
| kafka-ui        | http://localhost:8080/   | Kafka UI for monitoring topics    |
| schema-registry | http://localhost:8081/   | Schema Registry for Kafka         |
| zookeeper       | http://localhost:8082/   | Zookeeper for Kafka coordination  |
| kafka           | http://localhost:9092/   | Kafka message broker              |
| grafana         | http://localhost:3000/   | Metrics visualization             |
| prometheus      | http://localhost:9090/   | Metrics collection                |
| jaeger          | http://localhost:16686/  | Distributed tracing               |
| loki            | http://localhost:3100/   | Log aggregation                   |

## Development

For development purposes, you can use the provided Docker Compose file to run the necessary services locally. The project includes producer and consumer components for processing e-commerce events.


## Observability



```shell
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
```


helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm install my-opentelemetry-operator open-telemetry/opentelemetry-operator \
  --set "manager.collectorImage.repository=otel/opentelemetry-collector-k8s" \
  --set admissionWebhooks.certManager.enabled=false \
  --set admissionWebhooks.autoGenerateCert.enabled=true



