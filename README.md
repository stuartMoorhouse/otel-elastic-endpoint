# Flask SHA256 Hasher with OpenTelemetry

A Flask web application that generates SHA256 hashes from user input, instrumented with the Elastic Distribution of OpenTelemetry (EDOT) to send observability data to Elastic Cloud.

## Quick Start

```bash
# 1. Install dependencies
uv venv
uv pip install -e ".[dev]"

# 2. Configure Elastic Cloud credentials
cp .env.example .env
# Edit .env and paste the three values from Elastic Cloud UI

# 3. Run the application
python src/app.py
```

Visit `http://127.0.0.1:5000` and start generating hashes!

## Prerequisites

- Python 3.8 or higher
- uv package manager (or pip)
- An Elastic Cloud Observability instance

## Getting Configuration from Elastic Cloud

The application uses standard OpenTelemetry environment variables to connect to Elastic Cloud. You'll get all the values you need from a single location in the Elastic Cloud UI.

### Get the Three Configuration Values

1. Log in to your [Elastic Cloud Console](https://cloud.elastic.co/)
2. Navigate to your Observability deployment
3. Go to **Add data** → **Application** → **OpenTelemetry**
4. Select **Managed OTLP Endpoint** in the second step
5. Elastic will display three configuration values under "Configure the OpenTelemetry SDK":

   - **OTEL_EXPORTER_OTLP_ENDPOINT** - The endpoint URL
     - Example: `https://xxxxx.ingest.us-east-1.aws.elastic.cloud:443`

   - **OTEL_EXPORTER_OTLP_HEADERS** - Authorization header with embedded API key
     - Example: `Authorization=ApiKey base64-encoded-key`
     - Note: The API key is already included in this value - no separate API key needed!

   - **OTEL_RESOURCE_ATTRIBUTES** - Service metadata (optional but recommended)
     - Example: `service.name=my-app,service.version=1.0.0,deployment.environment=production`

6. Copy all three values - you'll paste them into your `.env` file in the next step

## Configuration

### 1. Create Configuration File

Copy the example environment file to create your configuration:

```bash
cp .env.example .env
```

### 2. Edit the .env File

Open the `.env` file in your project root directory and paste the three configuration values from Elastic Cloud:

```bash
# Paste the exact values from Elastic Cloud's "Configure the OpenTelemetry SDK" section

OTEL_EXPORTER_OTLP_ENDPOINT=https://xxxxx.ingest.us-east-1.aws.elastic.cloud:443
OTEL_EXPORTER_OTLP_HEADERS=Authorization=ApiKey xxxxx
OTEL_RESOURCE_ATTRIBUTES=service.name=flask-sha256-hasher,service.version=1.0.0,deployment.environment=production
```

**Important:**
- Paste the exact values from Elastic Cloud - do not modify them
- Do not add quotes around the values
- The API key is embedded in `OTEL_EXPORTER_OTLP_HEADERS` - you don't need a separate API key
- The `OTEL_RESOURCE_ATTRIBUTES` line is optional but recommended

**That's it!** These three environment variables are all the application needs to send data to Elastic Cloud.

## Installation

1. Create a virtual environment:
   ```bash
   uv venv
   ```

2. Install dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

## Running the Application

Start the Flask application:

```bash
python src/app.py
```

The application will be available at: `http://127.0.0.1:5000`

## Using the Application

1. Open your browser and navigate to `http://127.0.0.1:5000`
2. Enter text in the input field
3. Click "Generate Hash"
4. The SHA256 hash will be displayed

Every hash generation creates:
- **Traces** showing the request flow
- **Logs** with request details
- **Metrics** about the application performance

## Viewing Observability Data in Elastic Cloud

1. Log in to your Elastic Cloud Observability instance
2. Navigate to **Observability** > **APM** to view traces
3. Go to **Observability** > **Logs** to view application logs
4. Check **Observability** > **Metrics** for performance metrics

You should see data from the `flask-sha256-hasher` service.

## Demo Flow

This application is designed for demonstrating Elastic Cloud's Managed OTLP Endpoint:

1. **Show the Flask App** - Run the application and demonstrate the hash generation
2. **Create Elastic Serverless Observability instance** - Set up your Elastic Cloud deployment
3. **Get configuration values** - Copy the three OTEL environment variables from Elastic Cloud UI
4. **Configure the application** - Paste the values into `.env` file
5. **Generate observability data** - Use the app to create hashes (each request generates traces, logs, and metrics)
6. **View data in Elastic Cloud** - Show the observability data in your Elastic deployment

The configuration is intentionally simple - just three environment variables copied directly from Elastic Cloud UI. No complex setup, no separate collector installation required.

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black src/
```

### Linting

```bash
uv run ruff check src/
```

### Type Checking

```bash
uv run mypy src/
```

## Project Structure

```
otel-elastic-endpoint/
├── src/
│   ├── app.py              # Main Flask application
│   ├── templates/
│   │   └── index.html      # Web interface
│   └── __init__.py
├── .env                    # Your credentials (not in git)
├── .env.example            # Template for credentials
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Troubleshooting

**App starts but no data in Elastic Cloud:**
- Verify your `.env` file has the correct credentials
- Check that the OTLP endpoint is accessible
- Look for warning messages in the console when starting the app

**"OTEL_EXPORTER_OTLP_ENDPOINT not configured" warning:**
- Ensure you've created the `.env` file (not just `.env.example`)
- Verify the values are set correctly without quotes or extra spaces
- Make sure you copied all three values from Elastic Cloud's "Configure the OpenTelemetry SDK" section
- The values should start with:
  - `OTEL_EXPORTER_OTLP_ENDPOINT=https://...`
  - `OTEL_EXPORTER_OTLP_HEADERS=Authorization=ApiKey ...`
  - `OTEL_RESOURCE_ATTRIBUTES=service.name=...`

**Build errors during installation:**
- Make sure you have Python 3.8 or higher
- Try upgrading uv: `pip install --upgrade uv`

## References

- [Elastic Cloud Managed OTLP Endpoint](https://www.elastic.co/docs/solutions/observability/get-started/quickstart-elastic-cloud-otel-endpoint)
- [EDOT Instrumentation](https://www.elastic.co/docs/solutions/observability/get-started/opentelemetry/quickstart/serverless/hosts_vms)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
