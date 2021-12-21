---
title: Admonitions

---

```{note}
I'm a note
```

```{note} My note
I'm a note with a title
```

```{note} My **styled** note
I'm a note with a styled title
```

:::{important}
I'm important
:::

:::{admonition} This *is* also **Markdown**
:class: warning

This text is **standard** _Markdown_
:::

::::{important} Nesting
:::{note} Nested
This text is **standard** _Markdown_
:::
::::
