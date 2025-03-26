"""Markdown filter for templates"""
from flask import Blueprint
import markdown
import bleach

# Allowed HTML tags and attributes for safety
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol',
    'p', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'br', 'hr'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'class'],
    'abbr': ['title'],
    'acronym': ['title'],
    'img': ['src', 'alt', 'title']
}


def markdown_filter(text):
    """Convert Markdown text to safe HTML."""
    if not text:
        return ""

    # Convert markdown to HTML
    html = markdown.markdown(
        text,
        extensions=['extra', 'nl2br', 'sane_lists']
    )

    # Sanitize HTML
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

    return clean_html


def setup_markdown_filter(app):
    """Register the markdown filter with the Flask app"""
    app.jinja_env.filters['markdown'] = markdown_filter