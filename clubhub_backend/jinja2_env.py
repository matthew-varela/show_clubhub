from pathlib import Path

from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from jinja2 import Environment


def url_for(endpoint: str, **values):
    """Mimic Flask's url_for inside Django/Jinja2 templates.

    Supports two common usages in existing templates:
      - url_for('static', filename='path') → returns STATIC_URL + path
      - url_for('route_name') → reverse(route_name)
    """
    if endpoint == 'static':
        filename = values.get('filename', '')
        return f"{settings.STATIC_URL}{filename}"
    try:
        return reverse(endpoint, kwargs=values)
    except Exception:
        # Fallback to root
        return '/'


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'url_for': url_for,
    })
    return env 