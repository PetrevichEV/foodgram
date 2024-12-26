import re

from django.core.exceptions import ValidationError

from api.constants import MIN_YEAR

def validate_slug(value):
    slug_regex = r'^[-a-zA-Z0-9_]+$'
    if not re.match(slug_regex, value):
        raise ValidationError('Слаг содержит недопустимый символ.')
