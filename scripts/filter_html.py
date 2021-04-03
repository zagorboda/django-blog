from django import template
from django.utils.safestring import mark_safe
import bleach
from bs4 import BeautifulSoup


register = template.Library()


@register.filter
def filter_html_input(text):
    valid_tags = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'tbody', 'tr', 'td', 'img', 'strong', 'em', 'u', 's',
                  'hr', 'p', 'a', 'span', 'ol', 'ul', 'li', 'pre', 'div', 'q', 'big', 'kbd', 'ins', 'small',
                  'code', 'var', 'del', 'cite', 'sup', 'sub')

    text = bleach.clean(
        text,
        tags=valid_tags,
        attributes={'*': ['style'], 'img': ['src', 'alt'], 'a': ['href', 'title']},
        styles=['color', 'width', 'height']
    )

    soup = BeautifulSoup(text, 'html.parser')
    images = soup.findAll('img')

    for image in images:
        src = image.get("src")
        if src is None or not src.startswith('http'):
            img_tag = str(image)[:-2] + str(image)[-1:]
            start_index = text.index(img_tag)
            end_index = start_index + len(img_tag)
            text = text[:start_index] + text[end_index:]

    return mark_safe(text)
