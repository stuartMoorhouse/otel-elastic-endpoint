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
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor

# Load environment variables from .env file
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Configure logging (will be connected to OpenTelemetry below)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure OpenTelemetry Resource with explicit telemetry SDK attributes
# These attributes help Elastic properly identify and display the service badges
# Note: Resource.create() automatically reads OTEL_RESOURCE_ATTRIBUTES from environment
# and merges it with any attributes we provide here
resource = Resource.create({
    SERVICE_NAME: "flask-sha256-hasher",
    SERVICE_VERSION: "1.0.0",
    ResourceAttributes.TELEMETRY_SDK_NAME: "opentelemetry",
    ResourceAttributes.TELEMETRY_SDK_LANGUAGE: "python",
})

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

    # Configure trace exporter with low-latency settings for demo
    otlp_trace_exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(
        otlp_trace_exporter,
        schedule_delay_millis=1000,  # Send every 1 second (default: 5000)
        max_export_batch_size=128,   # Smaller batches (default: 512)
    )
    tracer_provider.add_span_processor(span_processor)

    # Configure log exporter with low-latency settings for demo
    otlp_log_exporter = OTLPLogExporter()
    log_processor = BatchLogRecordProcessor(
        otlp_log_exporter,
        schedule_delay_millis=500,   # Send every 500ms (default: 1000)
        max_export_batch_size=128,   # Smaller batches (default: 512)
    )
    logger_provider.add_log_record_processor(log_processor)

    # Attach OpenTelemetry handler to Python logging
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    # Configure metric exporter with faster interval for demo
    metric_exporter = OTLPMetricExporter()
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter, export_interval_millis=10000  # Export every 10 seconds (default: 60000)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
else:
    logger.warning(
        "OTEL_EXPORTER_OTLP_ENDPOINT not configured. "
        "OpenTelemetry traces and logs will not be exported. "
        "Please configure OTEL environment variables in your .env file."
    )
    # Set up a no-op MeterProvider so Flask instrumentation works without errors
    meter_provider = MeterProvider(resource=resource)
    metrics.set_meter_provider(meter_provider)

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
