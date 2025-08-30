from django.contrib import admin
from .models import Post, Category, Tag

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'text']
    actions = ['publish_selected', 'unpublish_selected']
    
    def publish_selected(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(
            request, 
            f'{updated} пост(ов) успешно опубликовано!',
            level='success'
        )
    
    publish_selected.short_description = "Опубликовать выбранные посты"
    
    def unpublish_selected(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(
            request, 
            f'{updated} пост(ов) снято с публикации!',
            level='success'
        )
    
    unpublish_selected.short_description = "Снять с публикации выбранные посты"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'posts_count']
    readonly_fields = ['slug']  # делаем slug только для чтения
    # prepopulated_fields убираем полностью
    
    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = 'Количество постов'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'posts_count']
    search_fields = ['name']
    readonly_fields = ['slug']  # также делаем slug только для чтения
    
    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = 'Количество постов'