import ipaddress
import os

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import generate_latest
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Local imports (added back after refactor)
from .database.database import create_db_and_tables

# Import the shared limiter instance
from .limiter import limiter
from .metrics import add_start_time_middleware, create_instrumentator

# Import API router after limiter is available to avoid circular imports
from .api.routes import router as api_router  # noqa: E402, isort: skip


app = FastAPI(title="Email Validator API")


# Initialize database tables
@app.on_event("startup")
async def startup_event():
    create_db_and_tables()


# Rate limiter setup (limiter is already created above)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add timing middleware
app.middleware("http")(add_start_time_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics_endpoint(request: Request):
    """Prometheus metrics endpoint with IP allowlist"""
    client_ip = request.client.host

    # FastAPI TestClient sends requests from the pseudo-host "testclient". Treat it as
    # coming from localhost so automated tests do not need to monkey-patch the request.
    if client_ip == "testclient":
        client_ip = "127.0.0.1"

    # Get allowlist from environment
    metrics_allowlist = os.getenv("METRICS_ALLOWLIST", "127.0.0.1,::1")
    if metrics_allowlist is None:
        metrics_allowlist = "127.0.0.1,::1"
    allowed_ips = [ip.strip() for ip in metrics_allowlist.split(",")]

    # Check if client IP is in allowlist
    is_allowed = False
    for allowed_ip in allowed_ips:
        try:
            if ipaddress.ip_address(client_ip) == ipaddress.ip_address(allowed_ip):
                is_allowed = True
                break
        except ValueError:
            # Skip invalid IP addresses in allowlist
            continue

    if not is_allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to metrics endpoint")

    # Return metrics
    instr = app.state.instrumentator
    if hasattr(instr, "generate_metrics"):
        return instr.generate_metrics()
    # Newer versions of the library expose metrics via prometheus_client registry
    return Response(generate_latest(), media_type="text/plain")


app.include_router(api_router, prefix="/api")

# Initialize Prometheus instrumentator
instrumentator = create_instrumentator()
instrumentator.instrument(app).expose(app, name="prometheus_metrics")
app.state.instrumentator = instrumentator
