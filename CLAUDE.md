# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask web application that generates SHA256 hashes from user input, instrumented with the Elastic Distribution of OpenTelemetry Collector (EDOT) to send observability data to Elastic Cloud Managed OTLP Endpoint.

## Architecture

### Application Components
- **Flask Web Application**: Simple web form (Bootstrap CSS) that accepts string input and returns SHA256 hash
- **OpenTelemetry Instrumentation**: Application is instrumented using EDOT to capture traces, logs, and metrics
- **OTLP Exporter**: Configured to send telemetry data to Elastic Cloud Managed OTLP Endpoint

### OpenTelemetry Configuration
The application uses the Elastic Distribution of OpenTelemetry Collector with:
- OTLP exporter configured to send data to Elastic Cloud endpoint
- Authorization via Elastic API key
- Configuration file: `otel.yml` (generated from template in `otel_samples/managed_otlp/logs_metrics_traces.yml`)

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

### Setting Up OTLP Exporter
Configure environment variables for Elastic Cloud connection:
```bash
ELASTIC_OTLP_ENDPOINT=<ELASTIC_OTLP_ENDPOINT>
ELASTIC_API_KEY=<ELASTIC_API_KEY>
```

### Generating otel.yml Configuration
```bash
cp ./otel_samples/managed_otlp/logs_metrics_traces.yml ./otel.yml
mkdir -p ./data/otelcol
sed -i "s#\${env:STORAGE_DIR}#${PWD}/data/otelcol#g" ./otel.yml
sed -i "s#\${env:ELASTIC_OTLP_ENDPOINT}#${ELASTIC_OTLP_ENDPOINT}#g" ./otel.yml
sed -i "s#\${env:ELASTIC_API_KEY}#${ELASTIC_API_KEY}#g" ./otel.yml
```

### Running the OTLP Collector
```bash
sudo ./otelcol --config otel.yml
```

### OTLP Exporter Configuration Format
The exporter in `otel.yml` should be configured as:
```yaml
exporters:
  otlp:
    endpoint: https://<motlp-endpoint>
    headers:
      Authorization: ApiKey <your-api-key>
```

## Demo Flow

The intended demonstration sequence:
1. Show the Flask app running locally
2. Create Elastic Serverless Observability instance (out of scope for this code)
3. Retrieve ELASTIC_OTLP_ENDPOINT and ELASTIC_API_KEY from Elastic Cloud
4. Configure OTLP shipper with the endpoint and API key
5. Use the app to generate hash requests (generates observability data)
6. View traces, logs, and metrics in Elastic Cloud Observability

## Key Documentation References

- Elastic Cloud Managed OTLP Endpoint: https://www.elastic.co/docs/solutions/observability/get-started/quickstart-elastic-cloud-otel-endpoint
- EDOT Instrumentation for Hosts/VMs: https://www.elastic.co/docs/solutions/observability/get-started/opentelemetry/quickstart/serverless/hosts_vms

## Project Structure Notes

- Application code will be in `src/`
- Tests will be in `tests/`
- OpenTelemetry configuration will be in `otel.yml` (generated from template)
- OTLP Collector data stored in `./data/otelcol/`
- Pre-commit hooks configured for security scanning (bandit, detect-secrets) and code formatting (black)
