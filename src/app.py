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
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Load environment variables from .env file
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Configure logging
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
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer_provider = trace.get_tracer_provider()

# Configure OTLP exporter - it will automatically use these environment variables:
# - OTEL_EXPORTER_OTLP_ENDPOINT
# - OTEL_EXPORTER_OTLP_HEADERS
otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if otel_endpoint:
    logger.info(f"Configuring OTLP exporter with endpoint: {otel_endpoint}")
    # The OTLPSpanExporter will automatically read OTEL_EXPORTER_OTLP_ENDPOINT
    # and OTEL_EXPORTER_OTLP_HEADERS from environment variables
    otlp_exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
else:
    logger.warning(
        "OTEL_EXPORTER_OTLP_ENDPOINT not configured. "
        "OpenTelemetry traces will not be exported. "
        "Please configure OTEL environment variables in your .env file."
    )

# Instrument Flask app
FlaskInstrumentor().instrument_app(app)

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
        logger.info(f"Generating hash for input of length {len(input_text)}")

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
