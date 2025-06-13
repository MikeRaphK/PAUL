from requests.adapters import HTTPAdapter
from typing import Any, Tuple
from urllib3.util.retry import Retry

import os
import requests



def check_env_vars() -> Tuple[str, str]:
    """
    Loads and validates required environment variables.

    Returns:
        Tuple[str, str]: A tuple containing the GitHub token and OpenAI API key.

    Raises:
        ValueError: If either `GITHUB_TOKEN` or `OPENAI_API_KEY` is not set.
    """

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set.")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")
    
    return GITHUB_TOKEN, OPENAI_API_KEY



def request_with_retry(method: str, url: str, retries: int = 3, timeout: int = 5, **kwargs: Any) -> requests.Response:
    """
    Performs an HTTP request with retry and timeout logic.

    Args:
        method (str): The HTTP method to use (e.g., 'GET', 'POST', etc.).
        url (str): The URL to send the request to.
        retries (int, optional): Number of retry attempts. Defaults to 3.
        timeout (int, optional): Timeout for the request in seconds. Defaults to 5.
        **kwargs (Any): Additional keyword arguments to pass to requests.request(), such as headers, json, data, etc.

    Returns:
        requests.Response: The response object if the request succeeds.

    Raises:
        Exception: If the request fails after all retries.
    """
    retry_strategy = Retry(
        total=retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=[method]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        response = session.request(method=method, url=url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        msg = f"Request {method} error for {url}"
        if hasattr(e, 'response') and e.response is not None:
            msg += f": {e.response.status_code} {e.response.text}"
        raise Exception(msg) from e