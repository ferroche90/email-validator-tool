import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Tuple

import aiodns
import dns.resolver
from email_validator_tool.core.models import ValidationResult, ValidationStatus
from loguru import logger


class DNSMXValidator:
    """Validator for DNS MX records with async resolution and caching support"""

    def __init__(self, cache_ttl_seconds: int = 3600):
        """
        Initialize DNS MX validator with async resolution and caching

        Args:
            cache_ttl_seconds: Time to live for cached results in seconds (default: 1 hour)
        """
        self.mx_cache: Dict[str, Tuple[ValidationResult, float]] = {}
        self.cache_ttl_seconds = cache_ttl_seconds
        self.resolver = None
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._init_resolver()
        logger.info(f"DNS MX Validator initialized with cache TTL: {cache_ttl_seconds} seconds")

    def _init_resolver(self):
        """Initialize the async DNS resolver with fallback support."""
        # If we are running inside the test-suite we always fall back to the
        # synchronous resolver so that monkey-patching ``dns.resolver.resolve``
        # in unit tests works as expected.
        import os

        if os.getenv("ENVIRONMENT") == "test":
            self.resolver = None
            logger.info("Test environment detected – using synchronous DNS resolver for determinism")
            return

        try:
            self.resolver = aiodns.DNSResolver()
            logger.info("Using aiodns for async DNS resolution")
        except Exception as e:
            logger.warning(f"aiodns not available, falling back to synchronous DNS: {e}")
            self.resolver = None

    async def _query_mx_async(self, domain: str) -> list:
        """Query MX records asynchronously using aiodns."""
        if self.resolver:
            try:
                mx_records = await self.resolver.query(domain, "MX")
                return [record.host for record in mx_records]
            except Exception as e:
                logger.debug(f"Async DNS query failed for {domain}, falling back to sync: {e}")
                return await self._query_mx_sync(domain)
        else:
            return await self._query_mx_sync(domain)

    async def _query_mx_sync(self, domain: str) -> list:
        """Query MX records synchronously using dnspython in executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self._query_mx_sync_internal, domain)

    def _query_mx_sync_internal(self, domain: str) -> list:
        """Internal synchronous MX query using dnspython."""
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            return [str(record.exchange) for record in mx_records]
        except dns.resolver.NXDOMAIN:
            raise
        except dns.resolver.NoAnswer:
            raise
        except Exception as e:
            logger.error(f"DNS query error for {domain}: {e}")
            raise

    def clear_cache(self) -> int:
        """
        Clear the DNS cache and return the number of entries removed

        Returns:
            Number of cache entries removed
        """
        cache_size = len(self.mx_cache)
        self.mx_cache.clear()
        logger.info(f"DNS cache cleared. Removed {cache_size} entries")
        return cache_size

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0

        for domain, (_, timestamp) in self.mx_cache.items():
            if current_time - timestamp < self.cache_ttl_seconds:
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            "total_entries": len(self.mx_cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_ttl_seconds": self.cache_ttl_seconds,
        }

    def _cleanup_expired_cache(self) -> int:
        """
        Remove expired entries from cache

        Returns:
            Number of expired entries removed
        """
        current_time = time.time()
        expired_domains = [
            domain
            for domain, (_, timestamp) in self.mx_cache.items()
            if current_time - timestamp >= self.cache_ttl_seconds
        ]

        for domain in expired_domains:
            del self.mx_cache[domain]

        if expired_domains:
            logger.debug(f"Cleaned up {len(expired_domains)} expired cache entries")

        return len(expired_domains)

    async def validate(self, email: str) -> ValidationResult:
        try:
            # Extract domain from email
            domain = email.split("@")[1]
            logger.debug(f"Checking MX records for domain: {domain}")

            # Check cache first
            if domain in self.mx_cache:
                cached_result, timestamp = self.mx_cache[domain]
                current_time = time.time()

                # Check if cache entry is still valid
                if current_time - timestamp < self.cache_ttl_seconds:
                    logger.debug(f"Using cached MX result for domain: {domain}")
                    # Return cached result but update the email field
                    return ValidationResult(
                        email=email,
                        status=cached_result.status,
                        details=cached_result.details,
                    )
                else:
                    # Remove expired cache entry
                    del self.mx_cache[domain]
                    logger.debug(f"Removed expired cache entry for domain: {domain}")

            # Perform async DNS query
            mx_records = await self._query_mx_async(domain)

            if mx_records:
                logger.info(f"Found {len(mx_records)} MX records for {domain}")
                result = ValidationResult(email=email, status=ValidationStatus.VALID)
                # Cache the successful result
                self.mx_cache[domain] = (result, time.time())
                return result

        except (dns.resolver.NXDOMAIN, aiodns.error.DNSError) as e:
            if "NXDOMAIN" in str(e) or isinstance(e, dns.resolver.NXDOMAIN):
                logger.warning(f"Domain {domain} does not exist")
                result = ValidationResult(
                    email=email,
                    status=ValidationStatus.INVALID_DOMAIN,
                    details=f"Domain {domain} does not exist",
                )
                # Cache the domain error result
                self.mx_cache[domain] = (result, time.time())
                return result

        except (dns.resolver.NoAnswer, aiodns.error.DNSError) as e:
            if "NoAnswer" in str(e) or isinstance(e, dns.resolver.NoAnswer):
                logger.warning(f"No MX records found for domain {domain}")
                result = ValidationResult(
                    email=email,
                    status=ValidationStatus.INVALID_MX,
                    details=f"No MX records found for domain {domain}",
                )
                # Cache the MX error result
                self.mx_cache[domain] = (result, time.time())
                return result

        except Exception as exc:
            logger.error(f"DNS error for {email}: {exc}")
            result = ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"DNS error: {str(exc)}",
            )
            # Cache the error result
            self.mx_cache[domain] = (result, time.time())
            return result

        finally:
            # Periodically cleanup expired cache entries (every 100 queries)
            if len(self.mx_cache) % 100 == 0:
                self._cleanup_expired_cache()

    def __del__(self):
        """Cleanup executor on deletion."""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False)
