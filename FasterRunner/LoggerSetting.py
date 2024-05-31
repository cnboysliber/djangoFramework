import os
import logging

from django.core.management.color import make_style
from django.utils.termcolors import PALETTES, DEFAULT_PALETTE

PALETTES[DEFAULT_PALETTE].update({
    'HTTP_INFO': {'opts': ('bold',), 'fg': 'green'}
})


class DjangoRequestColorsFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super(DjangoRequestColorsFormatter, self).__init__(*args, **kwargs)
        self.style = self.configure_style(make_style(os.environ.get('DJANGO_COLORS', '')))

    @staticmethod
    def configure_style(style):
        style.DEBUG = style.HTTP_NOT_MODIFIED
        style.INFO = style.HTTP_INFO
        style.WARNING = style.HTTP_NOT_FOUND
        style.ERROR = style.ERROR
        style.CRITICAL = style.HTTP_SERVER_ERROR

        return style

    def format(self, record):
        message = logging.Formatter.format(self, record)
        colorizer = getattr(self.style, record.levelname, self.style.HTTP_SUCCESS)
        return colorizer(message)


class DjangoColorsFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super(DjangoColorsFormatter, self).__init__(*args, **kwargs)
        self.style = self.configure_style(make_style(os.environ.get('DJANGO_COLORS', '')))

    @staticmethod
    def configure_style(style):
        style.DEBUG = style.HTTP_NOT_MODIFIED
        style.INFO = style.HTTP_REDIRECT
        style.WARNING = style.HTTP_NOT_FOUND
        style.ERROR = style.ERROR
        style.CRITICAL = style.HTTP_SERVER_ERROR
        return style

    def format(self, record):
        message = logging.Formatter.format(self, record)
        colorizer = getattr(self.style, record.levelname, self.style.HTTP_SUCCESS)
        return colorizer(message)
