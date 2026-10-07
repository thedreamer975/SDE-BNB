import logging
from typing import List
import httpx

logger = logging.getLogger(__name__)


def get_fallback_image(slug: str, width: int = 1400, height: int = 1000) -> str:
    """Fallback photo URL per PRD §17."""
    clean_slug = slug.replace(" ", "-").lower()
    return f"https://picsum.photos/seed/{clean_slug}/{width}/{height}"


def verify_image_url(url: str, slug: str = "stay", timeout_sec: float = 3.0) -> str:
    """
    Check if photo URL is reachable via HEAD request.
    If non-200 or connection error, returns fallback URL.
    """
    try:
        with httpx.Client(timeout=timeout_sec, follow_redirects=True) as client:
            resp = client.head(url)
            if resp.status_code == 200:
                return url
            # Some CDNs return 403 or 405 on HEAD, try quick ranged GET
            resp = client.get(url, headers={"Range": "bytes=0-100"})
            if resp.status_code in (200, 206):
                return url
    except Exception as e:
        logger.warning("Photo verification failed for %s: %s. Using fallback.", url, e)

    return get_fallback_image(slug)


def verify_listing_photos(photos: List[str], slug: str) -> List[str]:
    """Verify list of photo URLs for a listing."""
    verified = []
    for idx, p in enumerate(photos):
        v = verify_image_url(p, f"{slug}-{idx+1}")
        verified.append(v)
    return verified


if __name__ == "__main__":
    test_url = "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688"
    print("Verifying test URL:", verify_image_url(test_url, "test"))
