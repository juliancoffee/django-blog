from django.contrib import admin

# Register your models here.
from .models import Comment, Post


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 2


class PostAdmin(admin.ModelAdmin):
    list_display = ["post_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["post_text"]
    fieldsets = [
        ("Post", {"fields": ["post_text"]}),
        ("Date information", {"fields": ["pub_date"]}),
    ]
    inlines = [CommentInline]


admin.site.register(Post, PostAdmin)
