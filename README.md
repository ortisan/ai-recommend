# AI Recomendation System

## Setup


### Create stubs
```shell
python3 -m grpc_tools.protoc -I=schemas --python_out=ai_recommend/adapter/stub schemas/e-commerce-events.proto
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





