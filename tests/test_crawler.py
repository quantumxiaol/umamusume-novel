import asyncio
import sys
import os
import pytest

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from umamusume_web_crawler.web.crawler import crawl_page
from umamusume_novel.config import config
from umamusume_web_crawler.config import config as crawler_config

# Apply local configuration to the library
crawler_config.apply_overrides(
    http_proxy=config.HTTP_PROXY,
    https_proxy=config.HTTPS_PROXY,
)

@pytest.mark.asyncio
async def test_crawler_integration():
    """
    Test generic crawler integration via umamusume-web-crawler library.
    """
    url = "https://wiki.biligame.com/umamusume/爱慕织姬"
    print(f"\nCrawling {url}...")
    
    try:
        # Note: crawl_page returns the markdown string directly
        result = await crawl_page(url)
        
        assert result is not None, "Crawler returned None"
        assert isinstance(result, str), "Crawler should return a string"
        assert len(result) > 100, "Crawled content is too short"
        
        print(f"Successfully crawled {len(result)} characters.")
        print("Snippet:", result[:200].replace("\n", " "))
        
    except Exception as e:
        pytest.fail(f"Crawler failed: {e}")

if __name__ == "__main__":
    # Allow running directly
    try:
        asyncio.run(test_crawler_integration())
    except Exception as e:
        print(f"Test failed: {e}")
