from django import forms
from django.core.exceptions import ValidationError
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'text', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'максимальная длина 50 символов', 'class': 'form-control',
            }),
            'text': forms.Textarea(attrs={
                'rows': 3, 'class': 'form-control',
            }),
            'category': forms.Select(attrs={'class': 'form-control',}),
            'image': forms.FileInput(attrs={'class': 'form-control',})
        }
        labels = {
            'title': 'Заголовок поста:',
            'category': 'Категория:',
            'text': 'Текст поста:',
            'image': 'Изображение:'
        }

    def clean_title(self):
        """Кастомная валидация заголовка"""
        title = self.cleaned_data['title'].strip()
        
        if len(title) > 50:
            raise ValidationError(
                'Превышена максимальная длина заголовка (50 символов). '
                f'Введено {len(title)} символов.'
            )
        return title


    # title = forms.CharField(
    #     label='Заголовок поста:', 
    #     widget=forms.TextInput(attrs={
    #         'placeholder': 'максимальная длина 50 символов',
    #         'class': 'title-input'
    #     })
    # )
    
    # text = forms.CharField(
    #     label='Текст поста:',
    #     widget=forms.Textarea(attrs={
    #         'rows': 3 
    #     })
    # )
    
    # def clean_title(self):
    #     """Кастомная валидация заголовка"""
    #     title = self.cleaned_data['title'].strip()
        
    #     if len(title) > 50:
    #         raise ValidationError(
    #             'Превышена максимальная длина заголовка (50 символов). '
    #             f'Введено {len(title)} символов.'
    #         )
    #     return title