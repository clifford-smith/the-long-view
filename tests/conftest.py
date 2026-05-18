import pytest
from pathlib import Path
import yaml


@pytest.fixture
def config():
    return yaml.safe_load(Path("config.yml").read_text())


@pytest.fixture
def tmp_segment_dir(tmp_path):
    (tmp_path / "segments").mkdir()
    return tmp_path
