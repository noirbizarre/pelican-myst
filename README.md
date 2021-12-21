# Pelican Myst

A Pelican Myst reader parsing Markdown files using [Myst syntax](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html) with YAML frontmatter headers.

## Requirements

Pelican Myst works with Pelican 4+ and Python 3.9+

## Getting started

Install `pelican-myst` with pip:

```shell
pip install pelican-myst
```

And enable the plugin in you `pelicanconf.py` (or any configuration file you want to use):

```Python
PLUGINS = [
    '...',
    'myst',
    '...',
]
```

## Files format

Pelican Myst will only recognize files using `.md` extension.

Here an article example:

```markdown
---
title: My article title
date: 2017-01-04 13:10
modified: 2017-01-04 13:13
tags:
  - tag 1
  - tag 2
slug: my-article-slug
lang: en
category: A category
authors: Me
summary: Some summary
status: draft

custom:
  title: A custom metadata
  details: You can add any structured and typed YAML metadata

---

My article content

```
