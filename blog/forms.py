from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Tag

class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите теги через запятую',
            'class': 'form-control',
        }),
        label='Теги:'
    )
    
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
            'image': forms.FileInput(attrs={'class': 'form-control',}),
        }
        labels = {
            'title': 'Заголовок поста:',
            'category': 'Категория:',
            'text': 'Текст поста:',
            'image': 'Изображение:'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем начальное значение для tags_input
        if self.instance and self.instance.pk:
            self.fields['tags_input'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])

    def clean_title(self):
        """Кастомная валидация заголовка"""
        title = self.cleaned_data['title'].strip()
        
        if len(title) > 50:
            raise ValidationError(
                'Превышена максимальная длина заголовка (50 символов). '
                f'Введено {len(title)} символов.'
            )
        return title

    def clean_tags_input(self):
        """Очистка и валидация тегов"""
        tags_input = self.cleaned_data.get('tags_input', '')
        if not tags_input:
            return []
        
        # Разделяем теги по запятой и очищаем от пробелов
        tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
        
        # Проверяем длину каждого тега
        for tag_name in tag_names:
            if len(tag_name) > 100:
                raise ValidationError(f'Тег "{tag_name}" слишком длинный (максимум 100 символов)')
        
        return tag_names

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # Очищаем текущие теги
            instance.tags.clear()
            
            # Добавляем новые теги
            tag_names = self.cleaned_data.get('tags_input', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={'name': tag_name}
                )
                instance.tags.add(tag)
            
            self.save_m2m()
        
        return instance
    

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