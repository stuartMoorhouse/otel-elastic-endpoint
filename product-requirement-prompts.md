# Product Requirement Prompts

This file contains the requirements for your project. Fill out each section with relevant details before running `/init` in Claude Code. Claude will use this information to generate your initial project structure and implementation.

## Objective

```
# What is the main goal of this project? Be specific and concise.
Build a simple Flask application to return a SHA256 hash from a string provided by entering the string into a web form. 

The web form should be simple and styled with Bootstrap CSS. 

The application should be instrumented by the Elastic Otel Collector



```

## What

```
# Describe what the project should do in detail. List key features and functionality.
Locally running Flask app
The HTML served by the Flask app should use Twitter Bootstrap CSS
The Flask app will be instrumented via the Elastic OTEL Collector (EDOT).



```

## Why

```
# Explain the business value and problem this solves.
To demonstrate the Elastic Serverless OTEL endpoint



```


## Success criteria

```
# Define measurable success metrics and acceptance criteria.
OTEL data from the app can be send into an Elastic Serverless Observability cluster via the Elastic Cloud Managed OTLP Endpoint endpoint

I want to do a demo with these steps:

Show the Flask App
Create the Elastic Serverless Observability instance
Set up the Elastic Serverless Observability instance to receive data (
retrieve the values to fill in this config: 
ELASTIC_OTLP_ENDPOINT=<ELASTIC_OTLP_ENDPOINT> && \
ELASTIC_API_KEY=<ELASTIC_API_KEY> && \
cp ./otel_samples/managed_otlp/logs_metrics_traces.yml ./otel.yml && \
mkdir -p ./data/otelcol && \
sed -i "s#\${env:STORAGE_DIR}#${PWD}/data/otelcol#g" ./otel.yml && \
sed -i "s#\${env:ELASTIC_OTLP_ENDPOINT}#${ELASTIC_OTLP_ENDPOINT}#g" ./otel.yml && \
sed -i "s#\${env:ELASTIC_API_KEY}#${ELASTIC_API_KEY}#g" ./otel.yml
)
Configure the OTLP shipper to use the 
Elastic Cloud Managed OTLP Endpoint
Use the app a few time to generate data
See the Observability data in Elastic Cloud

```

## Context (Optional)

```
# Add any additional context, constraints, or background information.
Creating the Elastic Cloud Serverless Observability instance is not in scope for this project



```

## Documentation and references (Optional)

```
###
OLTP shipper: 

 Configure your OTLP shipper

The final step is to configure your Collector or SDK to use the Elastic Cloud Managed OTLP Endpoint endpoint and your Elastic API key to send data to Elastic Cloud.
OpenTelemetry Collector example

To send data to the Elastic Cloud Managed OTLP Endpoint from the Elastic Distribution of OpenTelemetry Collector or the contrib Collector, configure the otlp exporter:

exporters:
  otlp:
    endpoint: https://<motlp-endpoint>
    headers:
      Authorization: ApiKey <your-api-key>
		

Set the API key as an environment variable or directly in the configuration as shown in the example.

https://www.elastic.co/docs/solutions/observability/get-started/quickstart-elastic-cloud-otel-endpoint
```

### Instrumenting the application with EDOT
```
https://www.elastic.co/docs/solutions/observability/get-started/opentelemetry/quickstart/serverless/hosts_vms

ELASTIC_OTLP_ENDPOINT=<ELASTIC_OTLP_ENDPOINT> && \
ELASTIC_API_KEY=<ELASTIC_API_KEY> && \
cp ./otel_samples/managed_otlp/logs_metrics_traces.yml ./otel.yml && \
mkdir -p ./data/otelcol && \
sed -i "s#\${env:STORAGE_DIR}#${PWD}/data/otelcol#g" ./otel.yml && \
sed -i "s#\${env:ELASTIC_OTLP_ENDPOINT}#${ELASTIC_OTLP_ENDPOINT}#g" ./otel.yml && \
sed -i "s#\${env:ELASTIC_API_KEY}#${ELASTIC_API_KEY}#g" ./otel.yml

sudo ./otelcol --config otel.yml
```