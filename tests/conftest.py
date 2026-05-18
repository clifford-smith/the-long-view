import pytest
from pathlib import Path
import yaml

_ROOT = Path(__file__).parent.parent


@pytest.fixture
def config():
    return yaml.safe_load((_ROOT / "config.yml").read_text(encoding="utf-8"))


@pytest.fixture
def tmp_segment_dir(tmp_path):
    (tmp_path / "segments").mkdir()
    return tmp_path
