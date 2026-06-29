from django import forms
from django.contrib.auth.models import User
from .models import Review, Order


class ReviewForm(forms.ModelForm):
    """Form for creating product reviews"""
    rating = forms.IntegerField(
        widget=forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
        label='Рейтинг'
    )

    class Meta:
        model = Review
        fields = ['rating', 'title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок отзыва'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш отзыв',
                'rows': 5
            }),
        }


class OrderForm(forms.ModelForm):
    """Form for creating orders"""
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'zip_code', 'country']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 999-99-99'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Адрес доставки'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Город'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Почтовый индекс'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Страна'
            }),
        }


class SearchForm(forms.Form):
    """Form for product search"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control search-input',
            'placeholder': 'Поиск по названию...',
            'id': 'searchInput'
        })
    )


class FilterForm(forms.Form):
    """Form for filtering products"""
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Мин. цена'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Макс. цена'
        })
    )
    storage = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('64GB', '64GB'),
            ('128GB', '128GB'),
            ('256GB', '256GB'),
            ('512GB', '512GB'),
            ('1TB', '1TB'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    color = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('Black', 'Чёрный'),
            ('White', 'Белый'),
            ('Silver', 'Серебристый'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
