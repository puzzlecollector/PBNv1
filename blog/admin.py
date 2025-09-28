from django.contrib import admin

# Register your models here.
# board/admin.py
from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at", "like_count", "is_hot")
    list_filter  = ("category", "is_hot")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "username", "created_at", "ip")
    search_fields = ("username", "content")
