from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_fastapi_instrumentator.metrics import Info
import time
from typing import Callable
from fastapi import Request, Response


# Custom metrics
emails_validated_total = Counter(
    "emails_validated_total",
    "Total number of emails validated",
    ["status", "organization_id"]
)

smtp_connections_open = Gauge(
    "smtp_connections_open",
    "Number of open SMTP connections",
    ["domain"]
)

request_latency_seconds = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    ["endpoint", "method", "status_code"]
)

validation_batch_size = Histogram(
    "validation_batch_size",
    "Number of emails in validation batches",
    ["organization_id"]
)

# Custom metric functions
def emails_validated_counter(info: Info) -> None:
    """Increment email validation counter based on response data"""
    if info.response and hasattr(info.response, "body"):
        # This will be called by the instrumentator
        # We'll manually increment this in our validation endpoint
        pass


def smtp_connection_gauge(info: Info) -> None:
    """Track SMTP connections"""
    # This will be manually managed in SMTP validation
    pass


def request_latency_histogram(info: Info) -> None:
    """Record request latency"""
    if info.request and info.response:
        latency = time.time() - info.request.state.start_time
        request_latency_seconds.labels(
            endpoint=info.request.url.path,
            method=info.request.method,
            status_code=info.response.status_code
        ).observe(latency)


def validation_batch_size_histogram(info: Info) -> None:
    """Record validation batch sizes"""
    # This will be manually called in validation endpoint
    pass


# Middleware to add start time to request state
async def add_start_time_middleware(request: Request, call_next: Callable) -> Response:
    request.state.start_time = time.time()
    response = await call_next(request)
    return response


# Custom instrumentator configuration
def create_instrumentator() -> Instrumentator:
    """Create and configure Prometheus instrumentator"""
    instrumentator = Instrumentator(
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
    )
    
    # Add custom metrics
    instrumentator.add(emails_validated_counter)
    instrumentator.add(request_latency_histogram)
    
    # Add standard metrics
    instrumentator.add(metrics.request_size())
    instrumentator.add(metrics.response_size())
    instrumentator.add(metrics.latency())
    
    return instrumentator


# Utility functions for manual metric updates
def increment_emails_validated(status: str, organization_id: str = "unknown", count: int = 1):
    """Increment email validation counter"""
    emails_validated_total.labels(status=status, organization_id=organization_id).inc(count)


def set_smtp_connections(domain: str, count: int):
    """Set SMTP connections gauge"""
    smtp_connections_open.labels(domain=domain).set(count)


def record_batch_size(organization_id: str, batch_size: int):
    """Record validation batch size"""
    validation_batch_size.labels(organization_id=organization_id).observe(batch_size) 