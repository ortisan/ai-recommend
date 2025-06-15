# TiKV Key Deletion Tool

This application connects to a TiKV database and deletes all keys.

## Prerequisites

- Docker
- Kubernetes cluster
- Access to a TiKV database

## Building the Docker Image

Build the Docker image with the following command:

```bash
docker build -t marceloorsa/tikv-delete-keys:latest .
docker push marceloorsa/tikv-delete-keys:latest
```

## Running in Kubernetes

1. Update the `pod.yaml` file if needed:
   - Change the `PD_ENDPOINTS` environment variable to point to your TiKV PD (Placement Driver) endpoints
   - By default, it's set to "127.0.0.1:2379"
   - For multiple endpoints, use a comma-separated list: "pd1:2379,pd2:2379,pd3:2379"

2. Apply the Pod configuration:

```bash
kubectl apply -f pod.yaml
```

3. Check the Pod status:

```bash
kubectl get pods
```

4. View the logs:

```bash
kubectl logs tikv-delete-keys
```

5. Once the Pod has completed running, you can copy the output file:

```bash
kubectl cp tikv-delete-keys:/app/output/tikv_keys.json ./tikv_keys.json
```

## Configuration

The application can be configured using environment variables:

- `PD_ENDPOINTS`: Comma-separated list of TiKV PD endpoints (default: "127.0.0.1:2379")
- `OUTPUT_DIR`: Directory where the output JSON file will be written (default: current directory)

## Notes

- The application will scan up to 10,000 keys by default
- The output file is named `tikv_keys.json`
