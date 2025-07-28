# Users API

A Rust-based API for user management using SurrealDB as the database.

## Description

This API provides endpoints for creating and retrieving user information.

## Features

- User creation
- User retrieval by ID
- Secure authentication

## Getting Started

### Running SurrealDB
```sh
docker run -p 8000:8000 surrealdb/surrealdb:latest start --log debug --user root --pass root
```

### Running the API
```sh
cargo run
```