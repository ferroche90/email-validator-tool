"""
Enhanced Data Sources for Domain Information

This module provides examples of how to integrate with external APIs and databases
to enrich domain information with real geo, activity, and personal data.

To use these enhancements, modify the corresponding functions in domain_info.py
and replace the placeholder implementations.
"""

import os
from typing import Dict

import requests


class DataSourceConfig:
    """Configuration for external data sources."""

    # Free tier limits and API keys
    IPAPI_FREE_LIMIT = 1000  # requests per day
    CLEARBIT_FREE_LIMIT = 100  # requests per month
    LINKEDIN_FREE_LIMIT = 50  # requests per day

    # API Keys (set via environment variables)
    CLEARBIT_API_KEY = os.getenv("CLEARBIT_API_KEY")
    LINKEDIN_API_KEY = os.getenv("LINKEDIN_API_KEY")
    HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")


def get_company_data_from_clearbit(domain: str) -> Dict[str, str]:
    """
    Get company information from Clearbit API.
    Requires: pip install clearbit
    """
    if not DataSourceConfig.CLEARBIT_API_KEY:
        return {}

    try:
        import clearbit

        clearbit.key = DataSourceConfig.CLEARBIT_API_KEY

        company = clearbit.Company.find(domain=domain)
        if company:
            return {
                "firstname": company.get("person", {}).get("name", {}).get("givenName", ""),
                "lastname": company.get("person", {}).get("name", {}).get("familyName", ""),
                "country": company.get("geo", {}).get("country", ""),
                "region": company.get("geo", {}).get("state", ""),
                "city": company.get("geo", {}).get("city", ""),
                "zipcode": company.get("geo", {}).get("postalCode", ""),
            }
    except Exception:
        pass
    return {}


def get_email_activity_from_hunter(domain: str) -> str:
    """
    Get email activity data from Hunter.io API.
    """
    if not DataSourceConfig.HUNTER_API_KEY:
        return ""

    try:
        response = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={"domain": domain, "api_key": DataSourceConfig.HUNTER_API_KEY, "limit": 1},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("data", {}).get("emails"):
                # Return activity based on email count
                email_count = len(data["data"]["emails"])
                if email_count > 100:
                    return "365+"
                elif email_count > 50:
                    return "180"
                elif email_count > 10:
                    return "90"
                else:
                    return "30"
    except Exception:
        pass
    return ""


def get_social_media_presence(domain: str) -> Dict[str, bool]:
    """
    Check social media presence for a domain.
    """
    social_platforms = {
        "linkedin": f"https://www.linkedin.com/company/{domain}",
        "twitter": f"https://twitter.com/{domain}",
        "facebook": f"https://www.facebook.com/{domain}",
        "instagram": f"https://www.instagram.com/{domain}",
    }

    presence = {}
    for platform, url in social_platforms.items():
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            presence[platform] = response.status_code == 200
        except Exception:
            presence[platform] = False

    return presence


def get_domain_reputation(domain: str) -> Dict[str, str]:
    """
    Get domain reputation from various sources.
    """
    reputation = {
        "spam_score": "",
        "reputation_score": "",
        "blacklist_status": "",
    }

    # Example: Check against Spamhaus
    try:
        response = requests.get(f"https://zen.spamhaus.org/api/v1/query/{domain}")
        if response.status_code == 200:
            data = response.json()
            if data.get("query", {}).get("status") == "listed":
                reputation["blacklist_status"] = "listed"
            else:
                reputation["blacklist_status"] = "clean"
    except Exception:
        pass

    return reputation


def get_website_analytics(domain: str) -> Dict[str, str]:
    """
    Get website analytics data (requires integration with analytics APIs).
    """
    # This would require integration with:
    # - Google Analytics API
    # - SimilarWeb API
    # - Alexa API
    # - SEMrush API

    return {
        "monthly_visitors": "",
        "page_rank": "",
        "bounce_rate": "",
        "avg_session_duration": "",
    }


# Example usage in domain_info.py:
"""
To integrate these enhanced data sources, modify the functions in domain_info.py:

1. Import the enhanced functions:
   from .enhanced_data_sources import (
       get_company_data_from_clearbit,
       get_email_activity_from_hunter,
       get_social_media_presence,
       get_domain_reputation,
       get_website_analytics
   )

2. Replace placeholder implementations:

   def _get_activity_data(domain: str) -> str:
       # Try Hunter.io first
       activity = get_email_activity_from_hunter(domain)
       if activity:
           return activity

       # Fallback to domain age logic
       return _get_activity_from_domain_age(domain)

   def _get_personal_data(domain: str) -> Dict[str, str]:
       # Get company data from Clearbit
       company_data = get_company_data_from_clearbit(domain)
       return {
           "firstname": company_data.get("firstname", ""),
           "lastname": company_data.get("lastname", ""),
           "gender": "",  # Not available from Clearbit
       }

   def _get_geo_data(domain: str) -> Dict[str, str]:
       # Try Clearbit first (more accurate for businesses)
       company_data = get_company_data_from_clearbit(domain)
       if company_data.get("country"):
           return {
               "country": company_data.get("country", ""),
               "region": company_data.get("region", ""),
               "city": company_data.get("city", ""),
               "zipcode": company_data.get("zipcode", ""),
           }

       # Fallback to IP geolocation
       return _get_geo_from_ip(domain)
"""


# Environment variable setup example:
"""
Add these to your .env file:

# External API Keys (optional - for enhanced data)
CLEARBIT_API_KEY=your_clearbit_api_key_here
HUNTER_API_KEY=your_hunter_api_key_here
LINKEDIN_API_KEY=your_linkedin_api_key_here

# Rate limiting configuration
IPAPI_FREE_LIMIT=1000
CLEARBIT_FREE_LIMIT=100
HUNTER_FREE_LIMIT=100
"""
