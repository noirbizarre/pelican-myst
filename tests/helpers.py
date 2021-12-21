from pathlib import Path
from typing import Any

from pelican import readers
from pelican.plugins.myst.reader import MystReader
from pelican.settings import DEFAULT_CONFIG

TEST_DIR = Path(__file__).parent
DATA_PATH = TEST_DIR / "data"


def get_settings(**kwargs) -> dict[str, Any]:
    settings = DEFAULT_CONFIG.copy()
    for key, value in kwargs.items():
        settings[key] = value
    return settings


def read_content_metadata(path, **kwargs):
    r = MystReader(settings=get_settings(**kwargs))
    return r.read(DATA_PATH / path)


def read_file(path, **kwargs):
    r = readers.Readers(settings=get_settings(**kwargs))
    return r.read_file(base_path=DATA_PATH, path=path)


def assert_dict_contains(tested, expected):
    assert set(expected).issubset(set(tested)), "Some keys are missing"
    for key, value in expected.items():
        assert tested[key] == value
    # assert all(item in superset.items() for item in subset.items())
