from .calibre_compat import browser, random_user_agent

def fetch_page(url: str, log, timeout: int, opener=None) -> str:
    """Fetch a URL and return the HTML text. Returns an empty string on failure.

    Pass ``opener`` to inject a mock for testing.
    """
    log.info(f"Fetch: {url}")
    br = opener or browser()
    br.addheaders = [('User-Agent', random_user_agent())]
    try:
        resp = br.open(url, timeout=timeout)
        return resp.read().decode('utf-8', 'ignore')
    except Exception as e:
        log.error(f"Fetch failed: {e}")
        return ''
