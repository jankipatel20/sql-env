---
title: SQL Environment Server
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - sql
  - database
  - real-world
name: sql-env         
version: 0.1.0 
---

# SQL Task Environment

A real-world SQL task environment where an AI agent writes and optimizes 
SQL queries against a live SQLite database. The agent is given a natural 
language task and must produce the correct SQL query to solve it, with 
rewards based on query correctness, structure, and output quality.

## Quick Start

The simplest way to use the Sql Env environment is through the `SqlEnv` class:

```python
from sql_env import SqlAction, SqlEnv

try:
    # Create environment from Docker image
    sql_envenv = SqlEnv.from_docker_image("sql_env-env:latest")

    # Reset
    result = sql_envenv.reset()
    print(f"Reset: {result.observation.echoed_message}")

    # Send multiple messages
    messages = ["Hello, World!", "Testing echo", "Final message"]

    for msg in messages:
        result = sql_envenv.step(SqlAction(message=msg))
        print(f"Sent: '{msg}'")
        print(f"  â†’ Echoed: '{result.observation.echoed_message}'")
        print(f"  â†’ Length: {result.observation.message_length}")
        print(f"  â†’ Reward: {result.reward}")

finally:
    # Always clean up
    sql_envenv.close()
```

That's it! The `SqlEnv.from_docker_image()` method handles:
- Starting the Docker container
- Waiting for the server to be ready
- Connecting to the environment
- Container cleanup when you call `close()`

## Building the Docker Image

Before using the environment, you need to build the Docker image:

```bash
# From project root
docker docker build -t sql-env .
```

## Deploying to Hugging Face Spaces

You can easily deploy your OpenEnv environment to Hugging Face Spaces using the `openenv push` command:

```bash
# From the environment directory (where openenv.yaml is located)
openenv push

# Or specify options
openenv push --namespace my-org --private
```

The `openenv push` command will:
1. Validate that the directory is an OpenEnv environment (checks for `openenv.yaml`)
2. Prepare a custom build for Hugging Face Docker space (enables web interface)
3. Upload to Hugging Face (ensuring you're logged in)

### Prerequisites

- Authenticate with Hugging Face: The command will prompt for login if not already authenticated

### Options

- `--directory`, `-d`: Directory containing the OpenEnv environment (defaults to current directory)
- `--repo-id`, `-r`: Repository ID in format 'username/repo-name' (defaults to 'username/env-name' from openenv.yaml)
- `--base-image`, `-b`: Base Docker image to use (overrides Dockerfile FROM)
- `--private`: Deploy the space as private (default: public)

### Examples

```bash
# Push to your personal namespace (defaults to username/env-name from openenv.yaml)
openenv push

# Push to a specific repository
openenv push --repo-id my-org/my-env

# Push with a custom base image
openenv push --base-image ghcr.io/meta-pytorch/openenv-base:latest

# Push as a private space
openenv push --private

# Combine options
openenv push --repo-id my-org/my-env --base-image custom-base:latest --private
```

After deployment, your space will be available at:
`https://huggingface.co/spaces/<repo-id>`

The deployed space includes:
- **Web Interface** at `/web` - Interactive UI for exploring the environment
- **API Documentation** at `/docs` - Full OpenAPI/Swagger interface
- **Health Check** at `/health` - Container health monitoring
- **WebSocket** at `/ws` - Persistent session endpoint for low-latency interactions

## Environment Details

### Action
**SqlAction**: Contains a single field
- `query` (str) - The SQL query to execute against the database

### Observation
**SqlObservation**: Contains the query result and metadata
- `echoed_message` (str) - Human-readable summary of query result or error
- `message_length` (int) - Length of the query
- `metadata` (dict) - Contains query, columns, rows, rowcount, error, reward

### Reward
Reward is calculated based on query quality (max 1.0):
- Query runs without error: +0.3
- Query returns rows: +0.2
- Query uses JOIN: +0.2
- Query uses aggregation (COUNT, SUM, AVG, MAX, MIN): +0.2
- Query uses WHERE: +0.1
- Returned columns match task expected columns: up to +0.2 bonus

### Tasks
The environment includes 15 built-in tasks across three difficulty levels:
- **Easy** (tasks 01–05): Basic SELECT, WHERE, ORDER BY, COUNT
- **Medium** (tasks 06–10): JOINs, GROUP BY, subqueries
- **Hard** (tasks 11–15): HAVING, nested subqueries, multi-aggregation

## Advanced Usage

### Connecting to an Existing Server

If you already have a Sql Env environment server running, you can connect directly:

```python
from sql_env import SqlEnv

# Connect to existing server
sql_envenv = SqlEnv(base_url="<ENV_HTTP_URL_HERE>")

# Use as normal
result = sql_envenv.reset()
result = sql_envenv.step(SqlAction(message="Hello!"))
```

Note: When connecting to an existing server, `sql_envenv.close()` will NOT stop the server.

### Using the Context Manager

The client supports context manager usage for automatic connection management:

```python
from sql_env import SqlAction, SqlEnv

# Connect with context manager (auto-connects and closes)
with SqlEnv(base_url="http://localhost:8000") as env:
    result = env.reset()
    print(f"Reset: {result.observation.echoed_message}")
    # Multiple steps with low latency
    for msg in ["Hello", "World", "!"]:
        result = env.step(SqlAction(message=msg))
        print(f"Echoed: {result.observation.echoed_message}")
```

The client uses WebSocket connections for:
- **Lower latency**: No HTTP connection overhead per request
- **Persistent session**: Server maintains your environment state
- **Efficient for episodes**: Better for many sequential steps

### Concurrent WebSocket Sessions

The server supports multiple concurrent WebSocket connections. To enable this,
modify `server/app.py` to use factory mode:

```python
# In server/app.py - use factory mode for concurrent sessions
app = create_app(
    SqlEnvironment,  # Pass class, not instance
    SqlAction,
    SqlObservation,
    max_concurrent_envs=4,  # Allow 4 concurrent sessions
)
```

Then multiple clients can connect simultaneously:

```python
from sql_env import SqlAction, SqlEnv
from concurrent.futures import ThreadPoolExecutor

def run_episode(client_id: int):
    with SqlEnv(base_url="http://localhost:8000") as env:
        result = env.reset()
        for i in range(10):
            result = env.step(SqlAction(message=f"Client {client_id}, step {i}"))
        return client_id, result.observation.message_length

# Run 4 episodes concurrently
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(run_episode, range(4)))
```

## Development & Testing

### Direct Environment Testing

Test the environment logic directly without starting the HTTP server:

```bash
# From the server directory
python3 server/sql_env_environment.py
```

This verifies that:
- Environment resets correctly
- Step executes actions properly
- State tracking works
- Rewards are calculated correctly

### Running Locally

Run the server locally for development:

```bash
uvicorn server.app:app --reload
```

## Project Structure

```
## Project Structure

sql_env/
├── .dockerignore
├── __init__.py
├── README.md
├── openenv.yaml
├── pyproject.toml
├── uv.lock
├── client.py
├── models.py          # SqlAction, SqlObservation
├── tasks.py           # 15 built-in SQL tasks with difficulty levels
├── inference.py       # LLM agent loop (HuggingFace + OpenAI-compatible)
├── sql_env.db         # SQLite database (employees + departments)
└── server/
    ├── __init__.py
    ├── sql_env_environment.py  # Core environment + reward logic
    ├── app.py
└── Dockerfile
```

