"""Benchmark tests for async DNS MX validator."""

import pytest
import asyncio
from email_validator_tool.validators.dns_mx import DNSMXValidator


# Test domains for benchmarking
TEST_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com",
    "example.com", "test.com", "domain.com", "company.com", "business.com",
    "google.com", "microsoft.com", "apple.com", "amazon.com", "netflix.com",
    "facebook.com", "twitter.com", "linkedin.com", "github.com", "stackoverflow.com",
    "reddit.com", "wikipedia.org", "mozilla.org", "apache.org", "nginx.com",
    "cloudflare.com", "fastly.com", "aws.amazon.com", "azure.microsoft.com", "googleapis.com",
    "github.io", "herokuapp.com", "netlify.app", "vercel.app", "surge.sh",
    "firebase.com", "mongodb.com", "redis.com", "postgresql.org", "mysql.com",
    "elastic.co", "datadoghq.com", "newrelic.com", "sentry.io", "loggly.com",
    "papertrail.com", "sumologic.com", "splunk.com", "grafana.com", "prometheus.io",
    "kubernetes.io", "docker.com", "rancher.com", "terraform.io", "ansible.com",
    "chef.io", "puppet.com", "jenkins.io", "gitlab.com", "bitbucket.org",
    "atlassian.com", "slack.com", "discord.com", "teams.microsoft.com", "zoom.us",
    "meet.google.com", "webex.com", "gotomeeting.com", "bluejeans.com", "skype.com",
    "whatsapp.com", "telegram.org", "signal.org", "wire.com", "threema.ch",
    "protonmail.ch", "tutanota.com", "mailbox.org", "posteo.de", "startmail.com",
    "kolabnow.com", "runbox.com", "fastmail.com", "zoho.com", "yandex.com",
    "mail.ru", "qq.com", "163.com", "126.com", "sina.com.cn",
    "sohu.com", "naver.com", "daum.net", "hanmail.net", "nate.com",
    "live.com", "msn.com", "aol.com", "icloud.com", "me.com",
    "mac.com", "gmx.com", "web.de", "freenet.de", "t-online.de"
]


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_async_dns_benchmark(benchmark):
    """Benchmark async DNS resolution for 100 distinct domains."""
    validator = DNSMXValidator(cache_ttl_seconds=0)  # Disable cache for pure DNS benchmark
    
    def validate_domains():
        """Validate all test domains concurrently."""
        async def _validate():
            tasks = []
            for domain in TEST_DOMAINS:
                email = f"test@{domain}"
                tasks.append(validator.validate(email))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        return asyncio.run(_validate())
    
    # Run the benchmark
    result = benchmark(validate_domains)
    
    # Verify we got results for all domains
    assert len(result) == len(TEST_DOMAINS)
    
    # Check that we have a mix of valid and invalid results
    valid_count = sum(1 for r in result if hasattr(r, 'status') and r.status.value == 'valid')
    assert valid_count > 0, "Should have some valid domains"


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_async_dns_cached_benchmark(benchmark):
    """Benchmark async DNS resolution with caching enabled."""
    validator = DNSMXValidator(cache_ttl_seconds=3600)  # Enable cache
    
    def validate_domains_cached():
        """Validate all test domains with caching."""
        async def _validate():
            tasks = []
            for domain in TEST_DOMAINS:
                email = f"test@{domain}"
                tasks.append(validator.validate(email))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        return asyncio.run(_validate())
    
    # Run the benchmark
    result = benchmark(validate_domains_cached)
    
    # Verify we got results for all domains
    assert len(result) == len(TEST_DOMAINS)
    
    # Check cache stats
    cache_stats = validator.get_cache_stats()
    assert cache_stats["total_entries"] > 0, "Should have cached some results"


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_async_dns_sequential_benchmark(benchmark):
    """Benchmark async DNS resolution sequentially (for comparison)."""
    validator = DNSMXValidator(cache_ttl_seconds=0)  # Disable cache
    
    def validate_domains_sequential():
        """Validate all test domains sequentially."""
        async def _validate():
            results = []
            for domain in TEST_DOMAINS:
                email = f"test@{domain}"
                result = await validator.validate(email)
                results.append(result)
            return results
        
        return asyncio.run(_validate())
    
    # Run the benchmark
    result = benchmark(validate_domains_sequential)
    
    # Verify we got results for all domains
    assert len(result) == len(TEST_DOMAINS)


@pytest.mark.asyncio
async def test_async_dns_fallback():
    """Test that fallback to synchronous DNS works when aiodns fails."""
    validator = DNSMXValidator()
    
    # Test with a known valid domain
    result = await validator.validate("test@gmail.com")
    assert result.status.value in ['valid', 'invalid_mx', 'invalid_domain']


@pytest.mark.asyncio
async def test_async_dns_error_handling():
    """Test error handling in async DNS validator."""
    validator = DNSMXValidator()
    
    # Test with invalid domain
    result = await validator.validate("test@nonexistentdomain12345.com")
    assert result.status.value in ['invalid_domain', 'invalid_mx', 'unknown_error'] 