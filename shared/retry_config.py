"""
Retry configuration for API calls to handle transient errors like rate limiting.

This module provides two types of retry configurations:

1. Decorator-based retries (using tenacity) for wrapping custom functions
2. HttpRetryOptions objects for Google ADK agent integration

Usage:
    # For Google ADK agents:
    model = Gemini(model="gemini-2.5-flash-lite", retry_options=api_retry_options)

    # For custom functions:
    @api_retry
    def my_api_call():
        ...
"""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging

try:
    from google.genai import types
    GOOGLE_ADK_AVAILABLE = True
except ImportError:
    GOOGLE_ADK_AVAILABLE = False
    types = None

# Configure logging
logger = logging.getLogger(__name__)


# Common exceptions to retry on
class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


class APIConnectionError(Exception):
    """Raised when there's a connection error to the API."""
    pass


class APITimeoutError(Exception):
    """Raised when API request times out."""
    pass


# Retry decorator for API calls with exponential backoff
def with_retry(
    max_attempts=5,
    min_wait=1,
    max_wait=60,
    multiplier=2,
):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (default: 5)
        min_wait: Minimum wait time between retries in seconds (default: 1)
        max_wait: Maximum wait time between retries in seconds (default: 60)
        multiplier: Exponential backoff multiplier (default: 2)

    Example:
        @with_retry(max_attempts=3, min_wait=2)
        def call_api():
            # Your API call here
            pass
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=multiplier,
            min=min_wait,
            max=max_wait,
        ),
        retry=retry_if_exception_type((
            RateLimitError,
            APIConnectionError,
            APITimeoutError,
            ConnectionError,
            TimeoutError,
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


# Standard API retry configuration for any LLM provider
api_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type((
        RateLimitError,
        APIConnectionError,
        APITimeoutError,
        ConnectionError,
        TimeoutError,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)


# Aggressive retry configuration for critical operations
aggressive_retry = retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=2, min=2, max=120),
    retry=retry_if_exception_type((
        RateLimitError,
        APIConnectionError,
        APITimeoutError,
        ConnectionError,
        TimeoutError,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)


# Conservative retry configuration for non-critical operations
conservative_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception_type((
        RateLimitError,
        APIConnectionError,
        APITimeoutError,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)


# ============================================================================
# Google ADK HttpRetryOptions Configurations
# ============================================================================
# These configurations are specifically for use with Google ADK agents.
# Use these when initializing models like: Gemini(model="...", retry_options=...)

if GOOGLE_ADK_AVAILABLE:
    # Standard retry options for most API calls
    api_retry_options = types.HttpRetryOptions(
        attempts=5,
        exp_base=2,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504]
    )

    # Aggressive retry options for critical operations
    aggressive_retry_options = types.HttpRetryOptions(
        attempts=10,
        exp_base=2,
        initial_delay=2,
        http_status_codes=[429, 500, 503, 504]
    )

    # Conservative retry options for non-critical operations
    conservative_retry_options = types.HttpRetryOptions(
        attempts=3,
        exp_base=2,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504]
    )
else:
    # Fallback if Google ADK is not installed
    api_retry_options = None
    aggressive_retry_options = None
    conservative_retry_options = None
