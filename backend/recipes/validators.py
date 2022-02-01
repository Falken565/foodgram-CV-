from rest_framework import validators


def cooking_time_amount_validator(value):
    if value <= 0:
        raise validators.ValidationError(
            (f'значение не может быть равно {value}')
        )
