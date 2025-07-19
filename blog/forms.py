from django import forms
from django.core.exceptions import ValidationError

class PostForm(forms.Form):
    title = forms.CharField(
        label='Заголовок поста:', 
        widget=forms.TextInput(attrs={
            'placeholder': 'максимальная длина 50 символов',
            'class': 'title-input'
        })
    )
    
    text = forms.CharField(
        label='Текст поста:',
        widget=forms.Textarea(attrs={
            'rows': 3 
        })
    )
    
    def clean_title(self):
        """Кастомная валидация заголовка"""
        title = self.cleaned_data['title'].strip()
        
        if len(title) > 50:
            raise ValidationError(
                'Превышена максимальная длина заголовка (50 символов). '
                f'Введено {len(title)} символов.'
            )
        return title