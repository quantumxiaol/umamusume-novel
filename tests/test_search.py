import asyncio
import sys
import os
import pytest

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from umamusume_web_crawler.web.search import google_search_urls
from umamusume_novel.config import config
from umamusume_web_crawler.config import config as crawler_config

# Apply local configuration to the library
crawler_config.apply_overrides(
    google_api_key=config.GOOGLE_API_KEY,
    google_cse_id=config.GOOGLE_CSE_ID,
    http_proxy=config.HTTP_PROXY,
    https_proxy=config.HTTPS_PROXY,
)

@pytest.mark.asyncio
async def test_google_search_integration():
    """
    Test Google Search integration via umamusume-web-crawler library.
    Requires GOOGLE_API_KEY and GOOGLE_CSE_ID to be set in .env.
    """
    if not config.GOOGLE_API_KEY or not config.GOOGLE_CSE_ID:
        pytest.skip("Google API credentials not found in config")
        
    query = "Special Week umamusume"
    try:
        results = google_search_urls(query, num=3)
        print(f"\nSearch Results for '{query}':")
        for res in results:
            print(f"- {res}")
            
        assert len(results) > 0
        assert "url" in results[0]
    except Exception as e:
        pytest.fail(f"Search failed: {e}")

if __name__ == "__main__":
    # Allow running directly
    try:
        asyncio.run(test_google_search_integration())
    except Exception as e:
        print(f"Test failed: {e}")
