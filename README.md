# Prometheus MCP Server

A [Model Context Protocol][mcp] (MCP) server for Prometheus.

This provides access to your Prometheus metrics and queries through standardized MCP interfaces, allowing AI assistants to execute PromQL queries and analyze your metrics data across multiple Prometheus tenants.

<a href="https://glama.ai/mcp/servers/@pab1it0/prometheus-mcp-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@pab1it0/prometheus-mcp-server/badge" alt="Prometheus Server MCP server" />
</a>

[mcp]: https://modelcontextprotocol.io

## Features

- [x] Execute PromQL queries against Prometheus
- [x] **Multi-tenant support** - Query multiple Prometheus instances
- [x] Discover and explore metrics
  - [x] List available metrics
  - [x] Get metadata for specific metrics
  - [x] View instant query results
  - [x] View range query results with different step intervals
- [x] Authentication support
  - [x] Basic auth from environment variables
  - [x] Bearer token auth from environment variables
- [x] Docker containerization support
- [x] Cross-tenant queries
- [x] Provide interactive tools for AI assistants

The list of tools is configurable, so you can choose which tools you want to make available to the MCP client.
This is useful if you don't use certain functionality or if you don't want to take up too much of the context window.

## Usage

### Single Tenant Configuration (Backward Compatible)

1. Ensure your Prometheus server is accessible from the environment where you'll run this MCP server.

2. Configure the environment variables for your Prometheus server, either through a `.env` file or system environment variables:

```env
# Required: Prometheus configuration
PROMETHEUS_URL=http://your-prometheus-server:9090

# Optional: Authentication credentials (if needed)
# Choose one of the following authentication methods if required:

# For basic auth
PROMETHEUS_USERNAME=your_username
PROMETHEUS_PASSWORD=your_password

# For bearer token auth
PROMETHEUS_TOKEN=your_token

# Optional: For multi-tenant setups like Cortex, Mimir or Thanos
ORG_ID=your_organization_id
```

### Multi-Tenant Configuration

For multiple Prometheus instances or tenants, use the JSON configuration:

```env
# Multi-tenant configuration via JSON
PROMETHEUS_TENANTS='[
  {
    "name": "production",
    "url": "https://prometheus-prod.example.com",
    "username": "prod_user",
    "password": "prod_password",
    "org_id": "org-prod"
  },
  {
    "name": "staging",
    "url": "https://prometheus-staging.example.com",
    "token": "staging_bearer_token"
  },
  {
    "name": "development",
    "url": "http://localhost:9090"
  }
]'

# Optional: Set default tenant (defaults to first tenant if not specified)
PROMETHEUS_DEFAULT_TENANT=production
```

### MCP Client Configuration

3. Add the server configuration to your client configuration file. For example, for Claude Desktop:

#### Single Tenant

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "PROMETHEUS_URL",
        "ghcr.io/pab1it0/prometheus-mcp-server:latest"
      ],
      "env": {
        "PROMETHEUS_URL": "<url>"
      }
    }
  }
}
```

#### Multi-Tenant

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "PROMETHEUS_TENANTS",
        "-e",
        "PROMETHEUS_DEFAULT_TENANT",
        "ghcr.io/pab1it0/prometheus-mcp-server:latest"
      ],
      "env": {
        "PROMETHEUS_TENANTS": "[{\"name\":\"prod\",\"url\":\"https://prometheus.example.com\",\"token\":\"your_token\"}]",
        "PROMETHEUS_DEFAULT_TENANT": "prod"
      }
    }
  }
}
```

## Available Tools

| Tool                        | Category         | Description                                                                                      |
| --------------------------- | ---------------- | ------------------------------------------------------------------------------------------------ |
| `list_tenants`              | **Multi-Tenant** | List all configured Prometheus tenants                                                           |
| `execute_query`             | Query            | Execute a PromQL instant query against Prometheus (with optional tenant)                         |
| `execute_range_query`       | Query            | Execute a PromQL range query with start time, end time, and step interval (with optional tenant) |
| `execute_query_all_tenants` | **Multi-Tenant** | Execute a query across all configured tenants                                                    |
| `list_metrics`              | Discovery        | List all available metrics in Prometheus (with optional tenant)                                  |
| `get_metric_metadata`       | Discovery        | Get metadata for a specific metric (with optional tenant)                                        |
| `get_targets`               | Discovery        | Get information about all scrape targets (with optional tenant)                                  |

### Multi-Tenant Tool Examples

```python
# List all configured tenants
await list_tenants()

# Query specific tenant
await execute_query("up", tenant="production")

# Query default tenant (if no tenant specified)
await execute_query("up")

# Query all tenants at once
await execute_query_all_tenants("up")

# List metrics from staging environment
await list_metrics(tenant="staging")
```

## Development

Contributions are welcome! Please open an issue or submit a pull request if you have any suggestions or improvements.

This project uses [`uv`](https://github.com/astral-sh/uv) to manage dependencies. Install `uv` following the instructions for your platform:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

You can then create a virtual environment and install the dependencies with:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
uv pip install -e .
```

## Project Structure

The project has been organized with a `src` directory structure:

```
prometheus-mcp-server/
├── src/
│   └── prometheus_mcp_server/
│       ├── __init__.py      # Package initialization
│       ├── server.py        # MCP server implementation with multi-tenant support
│       ├── main.py          # Main application logic
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── .dockerignore            # Docker ignore file
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

### Testing

The project includes a comprehensive test suite that ensures functionality and helps prevent regressions.

Run the tests with pytest:

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run the tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

Tests are organized into:

- Configuration validation tests
- Server functionality tests
- Multi-tenant tests
- Error handling tests
- Main application tests

When adding new features, please also add corresponding tests.

## Configuration Examples

### Environment File (.env)

```env
# Single tenant
PROMETHEUS_URL=http://localhost:9090
PROMETHEUS_USERNAME=admin
PROMETHEUS_PASSWORD=secret

# Or multi-tenant
PROMETHEUS_TENANTS='[
  {
    "name": "local",
    "url": "http://localhost:9090",
    "username": "admin",
    "password": "secret"
  },
  {
    "name": "remote",
    "url": "https://prometheus.example.com",
    "token": "bearer_token_here",
    "org_id": "my-org"
  }
]'
PROMETHEUS_DEFAULT_TENANT=local
```

### Docker Compose

```yaml
version: "3.8"
services:
  prometheus-mcp:
    image: ghcr.io/pab1it0/prometheus-mcp-server:latest
    environment:
      PROMETHEUS_TENANTS: |
        [
          {
            "name": "prod",
            "url": "https://prometheus-prod.example.com",
            "token": "${PROD_TOKEN}"
          },
          {
            "name": "staging", 
            "url": "https://prometheus-staging.example.com",
            "username": "${STAGING_USER}",
            "password": "${STAGING_PASS}"
          }
        ]
      PROMETHEUS_DEFAULT_TENANT: prod
```

## Migration from Single to Multi-Tenant

Existing single-tenant configurations will continue to work without changes. The server automatically creates a tenant named "default" for backward compatibility.

To migrate to multi-tenant:

1. **Keep existing config** - Your current `PROMETHEUS_URL`, `PROMETHEUS_USERNAME`, etc. will work
2. **Add tenants gradually** - Use `PROMETHEUS_TENANTS` to add new tenants while keeping the old config
3. **Specify tenants in queries** - Add the optional `tenant` parameter to tool calls when needed

## License

MIT

---

[mcp]: https://modelcontextprotocol.io
