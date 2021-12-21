from __future__ import annotations

from typing import Union

import pytest

from .helpers import read_content_metadata

# from pyquery import PyQuery as pq


TASKLIST_EXPECTATIONS: tuple[tuple[Union[dict, list], str], ...] = (
    ([], "disabled"),
    ({}, "disabled"),
    (["tasklist"], "default"),
    ({"tasklist": {}}, "default"),
    ({"tasklist": dict(enabled=True)}, "enabled"),
    ({"tasklist": dict(label=True)}, "label"),
)


@pytest.mark.parametrize("setting,key", TASKLIST_EXPECTATIONS)
def test_myst_tasklist(setting, key):
    content, meta = read_content_metadata("myst/tasklist.md", MYST_PLUGINS=setting)
    assert content == meta["expected"][key]


# def test_myst_admonitions():
#     content, meta = read_content_metadata("myst/admonitions.md", MYST_PLUGINS=["admonitions"])
#     print(content)
#     html = pq(content)
#     admonitions = html.find("div.admonition")
#     assert admonitions.length == 8
#     assert admonitions.find("p.admonition-title").length == 8

#     assert html.find("div.admonition.note").length == 4
#     assert html.find("div.admonition.important").length == 2
#     assert html.find("div.admonition.warning").length == 1
