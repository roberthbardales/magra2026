from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
#
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    # TIPO DE USUARIOS
    ADMINISTRADOR = '0'
    VENTAS = '1'
    ALMACEN = '2'
    GERENCIA = '3'
    # GENEROS
    VARON = 'M'
    MUJER = 'F'
    OTRO = 'O'
    #

    OCUPATION_CHOICES  = (
        (ADMINISTRADOR, 'Administrador'),
        (VENTAS, 'Ventas'),
        (ALMACEN, 'Almacen'),
        (GERENCIA, 'Gerencia'),
    )

    GENDER_CHOICES = (
        (VARON, 'Masculino'),
        (MUJER, 'Femenino'),
        (OTRO, 'Otros'),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField('Nombres', max_length=100)
    occupation  = models.CharField(
        'Ocupacion',
        max_length=1,
        choices=OCUPATION_CHOICES,
        blank=True
    )
    genero = models.CharField(
        'Genero',
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    date_birth = models.DateField(
        'Fecha de nacimiento',
        blank=True,
        null=True
    )
    avatar = models.ImageField(
        'Avatar',
        upload_to='avatars/',
        blank=True,
        null=True
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

        # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['full_name',]

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} ({self.email})"