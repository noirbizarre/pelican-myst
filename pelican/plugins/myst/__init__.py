from pelican.plugins.signals import readers_init

from .reader import add_reader


def register():
    readers_init.connect(add_reader)
