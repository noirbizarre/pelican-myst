from pelican import Pelican
from pelican.plugins import myst

from .helpers import get_settings


def test_myst_plugin_not_enabled():
    settings = get_settings(PLUGINS=[])
    p = Pelican(settings)
    assert myst not in p.plugins


def test_myst_plugin_pelican_registeration():
    settings = get_settings(PLUGINS=["myst"])
    p = Pelican(settings)
    assert myst in p.plugins
