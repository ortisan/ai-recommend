FROM golang:1.24-alpine

WORKDIR /app

# Copy go.mod and go.sum files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy the source code
COPY main.go ./

# Build the application
RUN go build -o tikv-get-keys

# Run the application
CMD ["./tikv-get-keys"]