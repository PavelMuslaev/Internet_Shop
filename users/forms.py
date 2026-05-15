from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.html import strip_tags
from django.core.validators import RegexValidator

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Registration form for creating email-based users."""

    email = forms.EmailField(required=True, max_length=254, widget=forms.EmailInput(
        attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
               'placeholder': 'ЭЛ. ПОЧТА'}))
    first_name = forms.CharField(required=True, max_length=50, widget=forms.TextInput(
        attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
               'placeholder': 'ИМЯ'}))
    last_name = forms.CharField(required=True, max_length=50, widget=forms.TextInput(
        attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
               'placeholder': 'ФАМИЛИЯ'}))
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                   'placeholder': 'ПАРОЛЬ'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                   'placeholder': 'ПОВТОРИТЕ ПАРОЛЬ'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self) -> str:
        """Validate that the submitted email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже используется.')
        return email

    def save(self, commit: bool = True) -> Any:
        """Save a new custom user instance."""
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    """Authentication form that accepts an email in the username field."""

    username = forms.CharField(label="Эл. почта", widget=forms.TextInput(
        attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
               'placeholder': 'ЭЛ. ПОЧТА'}))
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                   'placeholder': 'ПАРОЛЬ'})
    )

    def clean(self) -> dict[str, Any]:
        """Authenticate the user by email and password."""
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Неверный email или пароль.')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('Этот аккаунт неактивен.')
        return self.cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    """Profile form for editing account and address details."""

    phone = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', "Введите корректный номер телефона.")],
        widget=forms.TextInput(
            attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                   'placeholder': 'ТЕЛЕФОН'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(
            attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                   'placeholder': 'ИМЯ'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(
            attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                   'placeholder': 'ФАМИЛИЯ'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                   'placeholder': 'ЭЛ. ПОЧТА'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'company',
                  'address1', 'address2', 'city', 'country',
                  'province', 'postal_code', 'phone')
        widgets = {
            'company': forms.TextInput(
                attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                   'placeholder': 'КОМПАНИЯ'}),
            'address1': forms.TextInput(
                attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                       'placeholder': 'АДРЕС, СТРОКА 1'}),
            'address2': forms.TextInput(
                attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                       'placeholder': 'АДРЕС, СТРОКА 2'}),
            'city': forms.TextInput(
                attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                       'placeholder': 'ГОРОД'}),
            'country': forms.TextInput(
                attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                       'placeholder': 'СТРАНА'}),
            'province': forms.TextInput(
                attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                       'placeholder': 'РЕГИОН'}),
            'postal_code': forms.TextInput(
                attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                       'placeholder': 'ПОЧТОВЫЙ ИНДЕКС'}),
        }

    def clean_email(self) -> str:
        """Validate that the email is not used by another account."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Этот email уже используется.')
        return email

    def clean(self) -> dict[str, Any]:
        """Preserve the current email and sanitize profile text fields."""
        cleaned_data = super().clean()
        if not cleaned_data.get('email'):
            cleaned_data['email'] = self.instance.email
        for field in ['company', 'address1', 'address2', 'city', 'country',
                      'province', 'postal_code', 'phone']:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])
        return cleaned_data
