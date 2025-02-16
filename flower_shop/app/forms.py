from django import forms
from django.contrib.auth.models import User
from .models import Order, Review


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Повторите пароль")

    class Meta:
        model = User
        fields = ('username', 'email')  # Укажите нужные поля

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Пароли не совпадают!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class OrderForm(forms.ModelForm):
    delivery_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
        required=True

    )

    data = {
        "delivery_address": "Тестовый адрес",
        "delivery_date": "2025-01-01",
        "phone_number": "1234567890"
    }

    class Meta:
        model = Order
        fields = ['delivery_address', 'phone_number', 'delivery_time', 'delivery_date']





class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-control'}),
        }
        labels = {
            'text': 'Ваш отзыв',
            'rating': 'Оценка',
        }