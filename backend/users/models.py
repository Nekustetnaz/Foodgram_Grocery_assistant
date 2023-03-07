from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

ROLE_CHOICES = (
    ('user', 'user'),
    ('admin', 'admin'),
)


class User(AbstractUser):
    username = models.CharField(
        'Username',
        db_index=True,
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Incorrect username'
        )]
    )
    email = models.EmailField(
        'Email',
        db_index=True,
        max_length=254,
        unique=True
    )
    first_name = models.CharField('First name', max_length=150)
    last_name = models.CharField('Last name', max_length=150)
    password = models.CharField('Password', max_length=150)
    role = models.CharField(
        'Role',
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
        default='user'
    )

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_admin(self):
        return self.role == 'admin'


class Subscription(models.Model):
    """User's subscriptions model."""
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    subscription = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription'
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.subscriber} subsribed for {self.subscription}.'
