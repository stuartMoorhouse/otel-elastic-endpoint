"""Flask application that generates SHA256 hashes from user input.

This application is instrumented with OpenTelemetry to send observability data
to Elastic Cloud via the Managed OTLP Endpoint.
"""

import hashlib
import logging
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from opentelemetry import trace, metrics
from opentelemetry._logs import set_logger_provider  # type: ignore[import-not-found]
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler  # type: ignore[import-not-found]
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor  # type: ignore[import-not-found]
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter  # type: ignore[import-not-found]
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor

# Load environment variables from .env file
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Configure logging (will be connected to OpenTelemetry below)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Parse OTEL_RESOURCE_ATTRIBUTES if provided, otherwise use defaults
resource_attributes = {"service.name": "flask-sha256-hasher"}
otel_resource_attrs = os.getenv("OTEL_RESOURCE_ATTRIBUTES")
if otel_resource_attrs:
    # Parse comma-separated key=value pairs
    for pair in otel_resource_attrs.split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            resource_attributes[key.strip()] = value.strip()

# Configure OpenTelemetry
resource = Resource.create(resource_attributes)

# Configure Trace Provider
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer_provider = trace.get_tracer_provider()

# Configure Logger Provider
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

# Configure OTLP exporters - they will automatically use these environment variables:
# - OTEL_EXPORTER_OTLP_ENDPOINT
# - OTEL_EXPORTER_OTLP_HEADERS
otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if otel_endpoint:
    logger.info(f"Configuring OTLP exporters with endpoint: {otel_endpoint}")

    # Configure trace exporter
    otlp_trace_exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(otlp_trace_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Configure log exporter
    otlp_log_exporter = OTLPLogExporter()
    log_processor = BatchLogRecordProcessor(otlp_log_exporter)
    logger_provider.add_log_record_processor(log_processor)

    # Attach OpenTelemetry handler to Python logging
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    # Configure metric exporter
    metric_exporter = OTLPMetricExporter()
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter, export_interval_millis=60000  # Export every 60 seconds
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
else:
    logger.warning(
        "OTEL_EXPORTER_OTLP_ENDPOINT not configured. "
        "OpenTelemetry traces and logs will not be exported. "
        "Please configure OTEL environment variables in your .env file."
    )

# Instrument Flask app (must be done after MeterProvider is configured)
FlaskInstrumentor().instrument_app(app)

# Instrument system/runtime metrics (CPU, memory, etc.)
# Only instrument if we have a configured endpoint
if otel_endpoint:
    SystemMetricsInstrumentor().instrument()

# Get tracer
tracer = trace.get_tracer(__name__)


@app.route("/")
def index():
    """Render the main page with the hash input form."""
    logger.info("Main page accessed")
    return render_template("index.html")


@app.route("/hash", methods=["POST"])
def generate_hash():
    """Generate SHA256 hash from user input.

    Returns:
        JSON response with the original input and generated hash.
    """
    with tracer.start_as_current_span("generate_hash") as span:
        # Get input from request
        data = request.get_json()
        input_text = data.get("text", "")

        span.set_attribute("input.length", len(input_text))
        masked_input = "*" * len(input_text)
        logger.info(f"Generating hash for input: {masked_input} (length: {len(input_text)})")

        # Generate SHA256 hash
        hash_object = hashlib.sha256(input_text.encode())
        hash_hex = hash_object.hexdigest()

        span.set_attribute("hash.algorithm", "SHA256")
        logger.info(f"Generated hash: {hash_hex[:16]}...")

        return jsonify({
            "input": input_text,
            "hash": hash_hex,
            "algorithm": "SHA256"
        })


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    logger.info("Starting Flask application on http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
