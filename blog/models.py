from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Post(models.Model):
    class Category(models.TextChoices):
        FORTUNE = "fortune", "오늘의 운세"
        DREAM   = "dream",   "꿈 해몽"
        FREE    = "free",    "자유게시판"

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, allow_unicode=True, max_length=200)

    body = models.TextField()

    # 탭(보드) 구분용
    category = models.CharField(max_length=20, choices=Category.choices, db_index=True)

    # ✅ 관리자가 임의로 적는 라벨(선택)
    admin_category = models.CharField(
        "카테고리 라벨",
        max_length=40,
        blank=True,
        help_text="예: 경제, 암호화폐, 시황 등. 비워도 됩니다."
    )

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    is_hot = models.BooleanField(default=False)

    # 좋아요 카운터(비로그인)
    like_count = models.PositiveIntegerField(default=0)

    @property
    def author_display(self):
        return "운영자"

    def get_absolute_url(self):
        return reverse("post_detail", args=[self.slug])

        # (선택) 비워 두면 제목으로 자동 생성 + 유니크 보장
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)
            slug = base or "post"
            i = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"


class Comment(models.Model):
    """자유게시판 전용 댓글: username + content"""
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
