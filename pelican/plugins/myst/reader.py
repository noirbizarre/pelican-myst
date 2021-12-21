import collections
from functools import cached_property
import logging
import re
from typing import Any, MutableMapping, Optional, Sequence

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from markdown_it.utils import OptionsDict
from mdit_py_plugins.colon_fence import colon_fence_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.myst_blocks import myst_block_plugin
from mdit_py_plugins.myst_role import myst_role_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
import yaml

from pelican.readers import BaseReader
from pelican.utils import pelican_open

from .signals import myst_yaml_register

DELIMITER = "---"
BOUNDARY = re.compile(r"^{0}$".format(DELIMITER), re.MULTILINE)
STR_TAG = "tag:yaml.org,2002:str"

INTERNAL_LINK = re.compile(r"^%7B(\w+)%7D")

log = logging.getLogger(__name__)

PLUGINS = dict(
    tasklist=tasklists_plugin,
)


class HtmlRenderer(RendererHTML):
    """
    An altered MarkdownIt HTML rendered taking reader settings in account.
    """

    def fence(
        self,
        tokens: Sequence[Token],
        idx: int,
        options: OptionsDict,
        env: MutableMapping,
    ) -> str:
        highlighted = super().fence(tokens, idx, options, env)
        if env.get("pygments"):
            return "<div class=highlight>" + highlighted + "</div>\n"
        return highlighted


class MystCodeFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        """
        Wrap the ``source``, which is a generator yielding
        individual lines, in custom generators. See docstring
        for `format`. Can be overridden.
        """
        return source


class Myst(MarkdownIt):
    def __init__(self, **options):
        super().__init__("gfm-like", options_update=options, renderer_cls=HtmlRenderer)

    def normalizeLink(self, url: str) -> str:
        normalized = super().normalizeLink(url)
        return INTERNAL_LINK.sub(r"{\g<1>}", normalized)


class MystReader(BaseReader):
    """
    Reader for Myst Markdown files with YAML metadata
    """

    enabled = True
    file_extensions = ["md"]

    def read(self, source_path) -> tuple[str, dict[str, Any]]:
        self._source_path = source_path

        with pelican_open(source_path) as text:
            return self._parse(text)

    @cached_property
    def myst(self) -> Myst:
        myst = (
            Myst(highlight=self.highlight)
            .use(front_matter_plugin)
            .use(colon_fence_plugin)
            .use(myst_role_plugin)
            .use(myst_block_plugin)
        )
        enabled_plugins = self.settings.get("MYST_PLUGINS", [])
        if isinstance(enabled_plugins, (list, tuple)):
            for plugin in enabled_plugins:
                if plugin in PLUGINS:
                    myst.use(PLUGINS[plugin])
        if isinstance(enabled_plugins, dict):
            for plugin, kwargs in enabled_plugins.items():
                if plugin in PLUGINS:
                    myst.use(PLUGINS[plugin], **kwargs)
        return myst

    @property
    def myst_env(self) -> dict[str, Any]:
        return dict(pygments=self.use_pygments)

    def _parse(self, text) -> tuple[str, dict]:
        """
        Parse text with frontmatter, return metadata and content.
        If frontmatter is not found, returns an empty metadata dictionary and original text content.
        """
        # ensure unicode first
        text = str(text).strip()

        tokens = self.myst.parse(text, self.myst_env)
        if tokens[0].type == "front_matter":
            fm = tokens[0].content
            tokens = tokens[1:]
        else:
            fm = ""

        metadata = self._metadata(fm, tokens)
        content = self.myst.renderer.render(tokens, self.myst.options, self.myst_env)
        return content.strip(), metadata

    def _metadata(self, frontmatter: str, tokens: Sequence[Token]) -> dict:
        meta = yaml.load(frontmatter, Loader=self.loader_class)
        meta = meta if (isinstance(meta, dict)) else {}
        if "title" not in meta:
            if len(tokens) > 1 and tokens[0].type == "heading_open" and tokens[1].type == "inline":
                meta["title"] = tokens[1].content

        formatted_fields = self.settings["FORMATTED_FIELDS"]

        output = collections.OrderedDict()
        for name, value in meta.items():
            name = name.lower()
            if name in formatted_fields:
                rendered = self._render(value).strip()
                output[name] = self.process_metadata(name, rendered)
            else:
                output[name] = self.process_metadata(name, value)
        return output

    @property
    def use_pygments(self):
        return self.settings.get("MYST_PYGMENTS") is not None

    @property
    def pygments_options(self) -> dict:
        """Optionnal Pygments options"""
        options = self.settings.get("MYST_PYGMENTS", {})
        if isinstance(options, dict):
            return options
        return {}

    def highlight(self, content: str, lang: str, attrs: dict) -> Optional[str]:
        if self.use_pygments:
            try:
                lexer = get_lexer_by_name(lang)
            except ValueError:
                # no lexer found - use the text one instead of an exception
                lexer = TextLexer()

            formatter = MystCodeFormatter(**self.pygments_options)
            return highlight(content, lexer, formatter)
        return None

    def _render(self, text):
        """Render Myst with settings taken in account"""
        return self.myst.render(text, self.myst_env)

    def yaml_markdown_constructor(self, loader, node):
        """Allows to optionnaly parse Markdown in multiline literals"""
        value = loader.construct_scalar(node)
        return self._render(value).strip()

    def yaml_multiline_as_markdown_constructor(self, loader, node):
        """Allows to optionnaly parse Markdown in multiline literals"""
        value = loader.construct_scalar(node)
        return self._render(value).strip() if node.style == "|" else value

    @property
    def loader_class(self):
        class FrontmatterLoader(yaml.Loader):
            """
            Custom YAML Loader for frontmark

            - Mapping order is respected (wiht OrderedDict)
            """

            def construct_mapping(self, node, deep=False):
                """User OrderedDict as default for mappings"""
                return collections.OrderedDict(self.construct_pairs(node))

        FrontmatterLoader.add_constructor("!md", self.yaml_markdown_constructor)
        if self.settings.get("MYST_FRONTMATTER_PARSE_LITERAL", True):
            FrontmatterLoader.add_constructor(STR_TAG, self.yaml_multiline_as_markdown_constructor)
        for _, pair in myst_yaml_register.send(self):
            if not len(pair) == 2:
                log.warning("Ignoring YAML type (%s), expected a (tag, handler) tuple", pair)
                continue
            tag, constructor = pair
            FrontmatterLoader.add_constructor(tag, constructor)

        return FrontmatterLoader


def add_reader(readers):  # pragma: no cover
    for k in MystReader.file_extensions:
        readers.reader_classes[k] = MystReader
