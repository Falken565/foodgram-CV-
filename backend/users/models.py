from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=150,
        validators=[RegexValidator(
            r'^[\w.@+-]+\Z',
            (
                ('Имя может содержать латинские буквы, цифры и символы'),
                ('@, ., +, -, _')
            )
        )]
    )
    email = models.EmailField(
        unique=True, max_length=254,
        verbose_name='email address'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password', 'username']
