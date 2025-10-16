# Product Requirement Prompts

This file contains the requirements for your project. Fill out each section with relevant details before running `/init` in Claude Code. Claude will use this information to generate your initial project structure and implementation.

## Objective

```
# What is the main goal of this project? Be specific and concise.
Build a simple Flask application to return a SHA256 hash from a string provided by entering the string into a web form.

The web form should be simple and styled with Bootstrap CSS.

The application should be instrumented with OpenTelemetry to send data directly to Elastic Cloud.



```

## What

```
# Describe what the project should do in detail. List key features and functionality.
Locally running Flask app
The HTML served by the Flask app should use Twitter Bootstrap CSS
The Flask app will be instrumented with OpenTelemetry using in-process OTLP exporters for direct export to Elastic Cloud.



```

## Why

```
# Explain the business value and problem this solves.
To demonstrate the Elastic Serverless OTEL endpoint



```


## Success criteria

```
# Define measurable success metrics and acceptance criteria.
OTEL data from the app can be sent into an Elastic Serverless Observability cluster via the Elastic Cloud Managed OTLP Endpoint

I want to do a demo with these steps:

1. Show the Flask App running locally (demo mode without telemetry)
2. Create the Elastic Serverless Observability instance
3. Retrieve the three OpenTelemetry environment variables from Elastic Cloud UI:
   - OTEL_EXPORTER_OTLP_ENDPOINT
   - OTEL_EXPORTER_OTLP_HEADERS (includes the API key)
   - OTEL_RESOURCE_ATTRIBUTES
4. Copy .env.example to .env and paste the three values from Elastic Cloud
5. Restart the Flask app (now sending telemetry directly to Elastic Cloud)
6. Use the app a few times to generate observability data
7. See the traces, logs, and metrics in Elastic Cloud Observability

```

## Context (Optional)

```
# Add any additional context, constraints, or background information.
Creating the Elastic Cloud Serverless Observability instance is not in scope for this project



```

## Documentation and references (Optional)

```
### Elastic Cloud Managed OTLP Endpoint

This project uses the direct export pattern where OpenTelemetry data is sent directly from the application to Elastic Cloud without a separate collector.

Configuration is done via standard OpenTelemetry environment variables:
- OTEL_EXPORTER_OTLP_ENDPOINT: The Elastic Cloud OTLP endpoint URL
- OTEL_EXPORTER_OTLP_HEADERS: Authorization header with embedded API key
- OTEL_RESOURCE_ATTRIBUTES: Service metadata (optional but recommended)

These values are provided by Elastic Cloud when you navigate to:
Add data → Application → OpenTelemetry → Managed OTLP Endpoint

Documentation:
https://www.elastic.co/docs/solutions/observability/get-started/quickstart-elastic-cloud-otel-endpoint
```

### Instrumenting the application with OpenTelemetry
```
The Flask application uses in-process OTLP exporters:
- OTLPSpanExporter for traces
- OTLPLogExporter for logs
- OTLPMetricExporter for metrics

All exporters automatically use the standard OTEL environment variables for configuration.

Documentation:
https://www.elastic.co/docs/solutions/observability/get-started/opentelemetry/quickstart/serverless/hosts_vms
https://opentelemetry.io/docs/instrumentation/python/
```