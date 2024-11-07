import re
from django.core.exceptions import ValidationError

def validate_username(value):
    # Регулярний вираз для перевірки, що username містить тільки латинські літери, цифри, . та _
    if not re.match(r'^[a-zA-Z0-9._]+$', value):
        raise ValidationError(
            'Username can only contain letters, digits, dots, and underscores.'
        )

def validate_no_spaces(value):
    if ' ' in value:
        raise ValidationError('This field cannot contain spaces.')

