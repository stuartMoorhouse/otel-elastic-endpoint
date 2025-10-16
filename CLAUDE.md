# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask web application that generates SHA256 hashes from user input, instrumented with OpenTelemetry to send observability data directly to Elastic Cloud Managed OTLP Endpoint using the direct export pattern.

## Architecture

### Application Components
- **Flask Web Application**: Simple web form (Bootstrap CSS) that accepts string input and returns SHA256 hash
- **OpenTelemetry Instrumentation**: Application is instrumented to capture traces, logs, and metrics
- **In-Process OTLP Exporters**: Direct export from the Flask application to Elastic Cloud (no separate collector required)

### OpenTelemetry Direct Export Pattern
The application uses in-process OTLP exporters:
- **OTLPSpanExporter**: Sends traces directly to Elastic Cloud
- **OTLPLogExporter**: Sends logs directly to Elastic Cloud
- **OTLPMetricExporter**: Sends metrics directly to Elastic Cloud
- **Configuration**: Uses standard OpenTelemetry environment variables (see Configuration section below)
- **No Collector**: Telemetry data flows directly from the Flask app to Elastic Cloud without a separate OpenTelemetry Collector process

## Development Commands

### Setup
```bash
# Create virtual environment
uv venv

# Install dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running the Application
```bash
# Run Flask app locally
python src/app.py
# or
flask run
```

### Testing & Quality
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src

# Format code
uv run black src/

# Check formatting
uv run black --check src/

# Lint code
uv run ruff check src/

# Type checking
uv run mypy src/

# Security scanning
uv run bandit -r src/
```

## OpenTelemetry Configuration

### Environment Variables
The application uses standard OpenTelemetry environment variables configured in the `.env` file. These values are provided by Elastic Cloud UI when you navigate to **Add data** → **Application** → **OpenTelemetry** → **Managed OTLP Endpoint**.

Copy `.env.example` to `.env` and configure the following three variables:

```bash
# The Elastic Cloud OTLP endpoint URL
OTEL_EXPORTER_OTLP_ENDPOINT=https://xxxxx.ingest.us-east-1.aws.elastic.cloud:443

# Authorization header with embedded API key
OTEL_EXPORTER_OTLP_HEADERS=Authorization=ApiKey xxxxx

# Service resource attributes (optional but recommended)
OTEL_RESOURCE_ATTRIBUTES=service.name=flask-sha256-hasher,service.version=1.0.0,deployment.environment=production
```

### How It Works
The application automatically configures OTLP exporters using these environment variables:
- **src/app.py:63-96**: Reads `OTEL_EXPORTER_OTLP_ENDPOINT` and configures exporters
- **In-process exporters**: `OTLPSpanExporter()`, `OTLPLogExporter()`, and `OTLPMetricExporter()` automatically use the environment variables
- **Direct export**: All telemetry data is sent directly from the Flask process to Elastic Cloud
- **Graceful degradation**: If environment variables are not set, the app runs without exporting telemetry (demo mode)

## Demo Flow

The intended demonstration sequence:
1. Show the Flask app running locally (demo mode without telemetry)
2. Create Elastic Serverless Observability instance (out of scope for this code)
3. Retrieve the three OpenTelemetry environment variables from Elastic Cloud UI:
   - `OTEL_EXPORTER_OTLP_ENDPOINT`
   - `OTEL_EXPORTER_OTLP_HEADERS`
   - `OTEL_RESOURCE_ATTRIBUTES`
4. Configure the application by pasting these values into the `.env` file
5. Restart the Flask app (now sending telemetry directly to Elastic Cloud)
6. Use the app to generate hash requests (generates observability data)
7. View traces, logs, and metrics in Elastic Cloud Observability

## Key Documentation References

- Elastic Cloud Managed OTLP Endpoint: https://www.elastic.co/docs/solutions/observability/get-started/quickstart-elastic-cloud-otel-endpoint
- EDOT Instrumentation for Hosts/VMs: https://www.elastic.co/docs/solutions/observability/get-started/opentelemetry/quickstart/serverless/hosts_vms

## Project Structure Notes

- Application code is in `src/` (main application in `src/app.py`)
- Tests are in `tests/`
- OpenTelemetry configuration is via environment variables in `.env` file
- Web UI templates are in `src/templates/`
- Pre-commit hooks configured for security scanning (bandit, detect-secrets) and code formatting (black)
- No separate collector process or configuration files needed
