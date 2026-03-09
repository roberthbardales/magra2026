from django import forms
from django.contrib.auth import authenticate
from .models import User


class UserRegisterForm(forms.ModelForm):

    password1 = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Contraseña',
                'class': 'form-control form-control-sm'
            }
        )
    )
    password2 = forms.CharField(
        label='Repetir Contraseña',  # corregido
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Repetir Contraseña',
                'class': 'form-control form-control-sm',
            }
        )
    )

    class Meta:
        model = User
        fields = (
            'email',
            'full_name',
            'occupation',
            'genero',
            'date_birth',
            'avatar',
        )
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'Correo Electronico ...',
                    'class': 'form-control'
                }
            ),
            'full_name': forms.TextInput(
                attrs={
                    'placeholder': 'Nombres ...',
                    'class': 'form-control'
                }
            ),
            'occupation': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'genero': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'date_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
            ),
            'avatar': forms.FileInput(
                attrs={
                    'accept': 'image/*'
                }
            ),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Las contraseñas no son iguales')
        return password2  # bug corregido: faltaba el return


class LoginForm(forms.Form):
    email = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Correo Electronico',
                'class': 'form-control mr-sm-2',
            }
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Contraseña',
                'class': 'form-control mr-sm-2',
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            if not authenticate(email=email, password=password):
                raise forms.ValidationError('Los datos de usuario no son correctos')

        return cleaned_data


class UpdatePasswordForm(forms.Form):

    password1 = forms.CharField(
        label='Contraseña Actual',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': ' ',
                'class': 'form-control mr-sm-2',
            }
        )
    )
    password2 = forms.CharField(
        label='Contraseña Nueva',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': ' ',
                'class': 'form-control mr-sm-2',
            }
        )
    )