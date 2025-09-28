from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse
from django.utils import timezone

class Post(models.Model):
    class Category(models.TextChoices):
        FORTUNE = "fortune", "오늘의 운세"
        DREAM   = "dream",   "꿈 해몽"
        FREE    = "free",    "자유게시판"

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    is_hot = models.BooleanField(default=False)

    # 좋아요 카운터(빠르고 간단)
    like_count = models.PositiveIntegerField(default=0)

    @property
    def author_display(self):
        return "운영자"  # 원하는 표시명

    def get_absolute_url(self):
        return reverse("post_detail", args=[self.slug])

    def __str__(self):
        return f"[{self.category}] {self.title}"


class Comment(models.Model):
    """자유게시판 전용 댓글. username + content 만 저장"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    username = models.CharField(max_length=50)
    content = models.TextField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["post", "-created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.username} on {self.post}"
