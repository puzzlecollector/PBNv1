# blog/admin.py
from django import forms
from django.contrib import admin

try:
    from django_summernote.admin import SummernoteModelAdmin
    BaseAdmin = SummernoteModelAdmin
except Exception:
    BaseAdmin = admin.ModelAdmin

from .models import Post, Comment


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # "dream" 옵션 숨기기
        self.fields["category"].choices = [
            (value, label)
            for value, label in self.fields["category"].choices
            if value != "dream"
        ]
        # 새 글 기본값: 자유게시판
        if self.instance.pk is None:  # add form
            self.fields["category"].initial = "free"


@admin.register(Post)
class PostAdmin(BaseAdmin):
    form = PostAdminForm

    # Summernote 사용 시 본문에 에디터 적용
    if BaseAdmin.__name__ == "SummernoteModelAdmin":
        summernote_fields = ("body",)

    list_display = ("title", "category", "admin_category",
                    "created_at", "is_hot", "like_count")
    list_filter  = ("category", "is_hot", "admin_category", "created_at")
    search_fields = ("title", "body", "admin_category")

    # slug는 모델 save()에서 자동 생성하니 굳이 미리 채우지 않음
    prepopulated_fields = {}

    # (선택) like_count는 관리자가 직접 수정하지 않도록 읽기전용 처리
    readonly_fields = ("like_count",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "username", "created_at")
    search_fields = ("username", "content")
    list_filter = ("created_at",)