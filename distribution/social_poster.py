from __future__ import annotations
import logging
from pathlib import Path
import yaml

log = logging.getLogger(__name__)


def _load_config() -> dict:
    root = Path(__file__).parent.parent
    return yaml.safe_load((root / "config.yml").read_text(encoding="utf-8"))


def post_to_mastodon(title: str, hook: str, stream_url: str) -> bool:
    try:
        from mastodon import Mastodon
        config = _load_config()
        mastodon_cfg = config.get("mastodon", {})
        if not mastodon_cfg.get("access_token"):
            log.debug("Mastodon not configured — skipping social post.")
            return False
        m = Mastodon(
            access_token=mastodon_cfg["access_token"],
            api_base_url=mastodon_cfg.get("instance", "https://mastodon.social"),
        )
        status = f"Now on The Long View: {title}\n\n{hook}\n\n{stream_url} #radio #longview"
        result = m.status_post(status)
        log.info("Mastodon post published: %s", result.get("url", "(no url)"))
        return True
    except Exception as exc:
        log.warning("Mastodon post failed: %s", exc)
        return False
