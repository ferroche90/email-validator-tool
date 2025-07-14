import datetime
import time
from functools import lru_cache
from typing import Dict, Optional, Tuple

import dns.resolver

try:
    import whois  # python-whois package
except ImportError:  # pragma: no cover – library may be optional in some envs
    whois = None  # type: ignore

try:
    import requests  # for external API calls
except ImportError:
    requests = None


# Rate limiting for IP-API.com (45 requests per minute)
class IPAPIRateLimiter:
    def __init__(self):
        self.requests = []
        self.max_requests = 45
        self.window_seconds = 60

    def can_make_request(self) -> bool:
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < self.window_seconds]
        return len(self.requests) < self.max_requests

    def record_request(self):
        self.requests.append(time.time())


# Global rate limiter instance
_ip_api_limiter = IPAPIRateLimiter()


@lru_cache(maxsize=2000)
def _query_mx(domain: str) -> Tuple[Optional[str], bool]:
    """Return preferred MX record and whether at least one MX was found."""
    try:
        answers = dns.resolver.resolve(domain, "MX")
        if answers:
            # Pick the lowest preference record (preferred)
            mx_hosts = sorted(
                [(r.preference, str(r.exchange).rstrip(".")) for r in answers],
                key=lambda x: x[0],
            )
            return mx_hosts[0][1], True
    except Exception:
        pass
    return None, False


@lru_cache(maxsize=2000)
def _query_domain_creation(domain: str) -> Optional[datetime.datetime]:
    """Return the domain creation date using WHOIS (cached)."""
    if whois is None:
        return None
    try:
        w = whois.whois(domain)
        created = w.creation_date  # can be datetime or list
        if isinstance(created, list):
            created = created[0]
        return created  # type: ignore[arg-type]
    except Exception:
        return None


def _derive_smtp_provider(mx_record: Optional[str]) -> Optional[str]:
    if not mx_record:
        return None
    host = mx_record.lower()
    providers = {
        "google": ["google", "gmail"],
        "yahoo": ["yahoodns", "yahoo"],
        "microsoft": ["outlook", "hotmail", "office365", "microsoft"],
        "apple": ["icloud"],
    }
    for provider, keywords in providers.items():
        if any(kw in host for kw in keywords):
            return provider
    # fallback: second-level domain
    parts = host.split(".")
    if len(parts) >= 2:
        return parts[-2]
    return host


@lru_cache(maxsize=1000)
def _get_geo_data(domain: str) -> Dict[str, str]:
    """Get geographic data for a domain using IP geolocation via IP-API.com."""
    if requests is None:
        return {}

    # Check rate limiting
    if not _ip_api_limiter.can_make_request():
        return {}

    try:
        # First get the IP address of the domain
        ip = dns.resolver.resolve(domain, "A")[0].to_text()

        # Use IP-API.com with optimized fields parameter
        # Fields: status,country,regionName,city,zip
        # This reduces bandwidth and only gets what we need
        fields = "status,country,regionName,city,zip"
        url = f"http://ip-api.com/json/{ip}?fields={fields}"

        response = requests.get(url, timeout=10)
        _ip_api_limiter.record_request()

        # Check rate limit headers
        reset_time = response.headers.get("X-Ttl", "0")

        if response.status_code == 429:  # Rate limited
            print(f"IP-API.com rate limit exceeded. Reset in {reset_time} seconds")
            return {}

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return {
                    "country": data.get("country", ""),
                    "region": data.get("regionName", ""),  # Use regionName for full region name
                    "city": data.get("city", ""),
                    "zipcode": data.get("zip", ""),
                }
            else:
                # API returned an error
                print(f"IP-API.com error for {domain}: {data.get('message', 'Unknown error')}")

    except dns.resolver.NXDOMAIN:
        # Domain doesn't exist
        pass
    except dns.resolver.NoAnswer:
        # No A record found
        pass
    except requests.exceptions.Timeout:
        print(f"IP-API.com timeout for {domain}")
    except requests.exceptions.RequestException as e:
        print(f"IP-API.com request error for {domain}: {e}")
    except Exception as e:
        print(f"Unexpected error getting geo data for {domain}: {e}")

    return {}


@lru_cache(maxsize=1000)
def _get_activity_data(domain: str) -> str:
    """Get activity data for a domain (simulated for now)."""
    # This could be enhanced with:
    # - Domain reputation databases
    # - Email activity APIs
    # - Social media presence
    # - Website analytics

    # For now, return a placeholder based on domain age
    created = _query_domain_creation(domain)
    if created:
        age_days = (datetime.datetime.utcnow() - created).days
        if age_days > 365:
            return "365+"  # Very active
        elif age_days > 180:
            return "180"  # Active
        elif age_days > 90:
            return "90"  # Somewhat active
        elif age_days > 30:
            return "30"  # Recently active
        else:
            return "30"  # New domain
    return ""


def get_domain_info(domain: str) -> dict:
    """Return a dict with comprehensive domain information including geo and activity data."""
    # Core domain data
    mx_record, mx_found = _query_mx(domain)
    created = _query_domain_creation(domain)
    age_days: Optional[int] = None
    if created:
        age_days = (datetime.datetime.utcnow() - created).days

    # Enhanced data
    geo_data = _get_geo_data(domain)
    activity_data = _get_activity_data(domain)

    return {
        # Core fields
        "domain_age_days": str(age_days) if age_days is not None else "",
        "mx_record": mx_record or "",
        "mx_found": mx_found,
        "smtp_provider": _derive_smtp_provider(mx_record) or "",
        # Activity data
        "active_in_days": activity_data,
        # Geographic data
        "country": geo_data.get("country", ""),
        "region": geo_data.get("region", ""),
        "city": geo_data.get("city", ""),
        "zipcode": geo_data.get("zipcode", ""),
    }
