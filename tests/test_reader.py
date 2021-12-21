from pyquery import PyQuery as pq

from pelican.plugins.myst.signals import myst_yaml_register
from pelican.utils import SafeDatetime

from .helpers import assert_dict_contains, read_content_metadata, read_file


def test_read_markdown_and_metadata():
    page = read_file("page.md")
    assert page
    assert page.title == "Some page"
    assert page.content == "<p>This is a simple markdown file</p>"


def test_typed_metadata():
    _, metadata = read_content_metadata("metadata.md")
    expected = {
        "title": "Metadata",
        "list": ["a", "b", "c"],
        "date": SafeDatetime(2017, 1, 6, 22, 24),
        "int": 42,
        "bool": False,
        "summary": "<p>a summary</p>",
    }
    assert_dict_contains(metadata, expected)


def test_markdown_only():
    content, metadata = read_content_metadata("markdown-only.md")
    assert metadata == {}
    assert content == "<p>Only markdown</p>"


def test_title_from_markdown():
    content, metadata = read_content_metadata("title-from-markdown.md")
    assert metadata == {"title": "Title"}
    assert content == "<h1>Title</h1>\n<p>There is no frontmatter title</p>"


def test_metadata_only():
    content, metadata = read_content_metadata("meta-only.md")
    assert metadata == {"title": "Meta only"}
    assert content == ""


def test_multiline_rendering():
    _, metadata = read_content_metadata("multiline.md")
    assert_dict_contains(
        metadata,
        {
            "rendered": "<p>This should be rendered</p>",
            "notrendered": "This shouldn't be rendered\n",
            "markdown": "<p>This should be rendered</p>",
        },
    )


def test_multiline_rendering_disabled():
    _, metadata = read_content_metadata("multiline.md", MYST_FRONTMATTER_PARSE_LITERAL=False)
    assert_dict_contains(
        metadata,
        {
            "rendered": "This should be rendered\n",
            "notrendered": "This shouldn't be rendered\n",
            "markdown": "<p>This should be rendered</p>",
        },
    )


def test_default_syntax_highlighting_html5():
    """Output standard pre>code block with language class by default"""
    content, _ = read_content_metadata("highlight.md")
    pre = pq(content)
    assert pre.length == 1
    assert pre.is_("pre")
    code = pre.children()
    assert code.length == 1
    assert code.is_("code")
    assert code.has_class("language-python")
    assert code.text() == "print('Hello Frontmark')"


def test_syntax_highlighting_pygments():
    """Output Pygments rendered div.highlight>code block"""
    content, _ = read_content_metadata("highlight.md", MYST_PYGMENTS=True)
    div = pq(content)
    assert div.length == 1
    assert div.is_("div")
    assert div.has_class("highlight")
    pre = div.children()
    assert pre.length == 1
    assert pre.is_("pre")
    code = pre.children()
    assert code.length == 1
    assert code.is_("code")
    assert code.has_class("language-python")
    assert code.children().is_("span")


def test_syntax_highlighting_pygments_options():
    """Pass MYST_PYGMENTS options to Pygments"""
    content, _ = read_content_metadata(
        "highlight.md",
        MYST_PYGMENTS={
            "linenos": "inline",
        },
    )
    assert pq(content).find(".linenos").length > 0


def test_syntax_highlighting_pygments_unknown_language():
    """Pygments should not fail on unkown language"""
    content, _ = read_content_metadata("highlight-unknown.md", MYST_PYGMENTS=True)
    div = pq(content)
    assert div.length == 1
    assert div.is_("div")
    assert div.has_class("highlight")
    pre = div.children()
    assert pre.length == 1
    assert pre.is_("pre")
    code = pre.children()
    assert code.length == 1
    assert code.is_("code")
    assert code.has_class("language-unknown")


def test_hr():
    content, _ = read_content_metadata("hr.md")
    assert "<hr/>" in content.replace(" ", "")


def test_links_in_anchors():
    content, _ = read_content_metadata("links.md")
    anchors = pq(content).find("a")
    expected = (
        "{filename}/article.md",
        "{attach}/file.pdf",
        "{index}",
        "{author}/author",
        "{category}/category",
        "{tag}/tag",
    )
    for a, expected in zip(anchors.items(), expected):
        assert a.attr.href == expected


def test_filename_in_images():
    content, _ = read_content_metadata("links.md")
    imgs = pq(content).find("img")
    expected = (
        "{filename}/image.png",
        "{attach}/image.png",
    )
    for img, expected in zip(imgs.items(), expected):
        assert img.attr.src == expected


def test_markdown_only_with_hr_start():
    content, metadata = read_content_metadata("hr-start.md")
    assert metadata == {}
    assert content.replace(" ", "") == "<hr/>\n<p>Starts</p>"


def register_custom_type(reader):
    return "!custom", lambda l, n: l.construct_scalar(n).upper()


def test_custom_types():
    with myst_yaml_register.connected_to(register_custom_type):
        _, metadata = read_content_metadata("types.md")
    assert metadata["custom"] == "TEST"


def test_wrong_custom_type_warn_only():
    with myst_yaml_register.connected_to(lambda r: "missing arg"):
        read_content_metadata("page.md")


def test_gfm_table():
    content, _ = read_content_metadata("gfm-table.md")
    assert content == "\n".join(
        (
            "<table>",
            "<thead>",
            "<tr>",
            "<th>header 1</th>",
            "<th>header 2</th>",
            "</tr>",
            "</thead>",
            "<tbody>",
            "<tr>",
            "<td>col 1</td>",
            "<td>col 2</td>",
            "</tr>",
            "</tbody>",
            "</table>",
        )
    )


def test_gfm_strikethrough():
    content, _ = read_content_metadata("gfm-strikethrough.md")
    content == "<p><s>striked</s></p>"
