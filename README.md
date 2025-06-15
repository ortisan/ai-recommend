# AI Recomendation System

## Setup

#### k8s

Create a cluster with k3d or kind:

```sh
# Use k3d if you prefer
k3d cluster create k8s-ai-recommend --servers 1 --agents 1 --port 9080:80@loadbalancer --port 9443:443@loadbalancer --api-port 6443 --k3s-arg "--disable=traefik@server:0"
# Use kind if you prefer
kind create cluster --name k8s-ai-recommend
# Use k3d or kind to create a cluster with the following command
kubectl cluster-info --context k8s-ai-recommend
```

Delete the cluster
```sh
k3d cluster delete k8s-ai-recommend
```

### Database Infrastructure

# Install CDR and tidb-operator

CDR
```sh
kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.6.1/manifests/crd.yaml
```

tidb-operator
```sh
helm repo update
helm install \
	-n tidb-operator \
  --create-namespace \
	tidb-operator \
	pingcap/tidb-operator \
	--version v1.6.1 \
	-f database/tidb-operator/values.yaml
	
# Check if the tidb-operator is running
k get all -n tidb-operator	
```

![Important]: I had problems with tidb-scheduler. The CDR is in version "kubescheduler.config.k8s.io/v1beta2". Related with [issue](https://github.com/pingcap/tidb-operator/issues/5462).

If you want to uninstall the tidb-operator, run the following command:
```sh
helm uninstall tidb-operator -n tidb-operator
```

Install TiKV Cluster
```sh
kubectl create ns tikv
## This file have older version of images
kubectl apply -n tikv -f database/tidb-cluster/tidb-cluster.yaml
# Check if the tikv cluster is running
k get all -n tikv
# Check if the tidb cluster is running
kubectl get -n tikv tidbcluster
```

### Deploy SurrealDB

Before deploying SurrealDB, you need to put the key that surrealdb use to detect if in the [v2](https://github.com/surrealdb/surrealdb/blob/main/crates/core/src/kvs/ds.rs#L540)({"!v": "\u0000\u0002"}) or not.

Run the following command to put the key in the tikv database:

```sh
kubectl apply -f database/tikv/tikv-put-surreal-v2-keys/pod.yaml
```

After that, check the file:

```sh
kubectl exec -ti tikv-get-keys -- cat output/tikv_keys.json
```

```json
{
  "!v": "\u0000\u0002",
  ...
 }
```

Install SurrealDB with Helm.

```sh 
export TIKV_URL=tikv://basic-pd.tikv:2379
```

```shell
helm repo add surrealdb https://helm.surrealdb.com
helm repo update
helm install --set surrealdb.path=$TIKV_URL --set surrealdb.unauthenticated=true --set image.tag=latest surrealdb-tikv surrealdb/surrealdb
```

```sh
kubectl port-forward svc/surrealdb-tikv 8000
```

Uninstall crd

```sh
kubectl get crd --no-headers | grep '^tidb' | awk '{print $1, $2}' | xargs -n2 kubectl delete
```

### Install SurrealDBCLi

Install Cli
```sh
brew install surrealdb/tap/surreal
```

### Create a user in SurrealDB
```sh
surreal sql -e http://localhost:8000
```
```sql
DEFINE USER root ON ROOT PASSWORD 'Password' ROLES OWNER;
```
```sh
surreal sql -e http://localhost:8000 -u root -p 'Password' 
```

```sql
INFO FOR ROOT
```

### Visualize SurrealDB

https://surrealdb.com/surrealist?download



### Create stubs
```shell
uv run python3 -m grpc_tools.protoc -I=schemas --python_out=ai_recommend/adapter/stub schemas/e-commerce-events.proto
```

### Create topics in Kafka
```sh
docker-compose exec kafka kafka-topics --create --topic e-commerce-events --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1
```

### Register on Schema Registry
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

## Services Table

| Service Name    |  Url Port               |
|-----------------|-------------------------|
| kafka-ui        |  http://localhost:8080/ |
| schema-registry |  http://localhost:8081/ |
| zookeeper       |  http://localhost:8082/ |
| kafka           |  http://localhost:9092/ |
| grafana         |  http://localhost:3000/ |
| prometheus      |  http://localhost:9090/ |
| jaeger          |  http://localhost:16686/ |
| loki            |  http://localhost:3100/ |

