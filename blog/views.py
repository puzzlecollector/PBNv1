from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import F
from .models import Post, Comment
from .forms import CommentForm


def safe_int(value, default=1):
    try:
        v = int(value)
        return v if v >= 1 else 1
    except Exception:
        return default


def home(request):
    active_tab = request.GET.get("tab", "free")  # 기본값을 free로
    page = safe_int(request.GET.get("page", 1), 1)

    def q(category):
        return Post.objects.filter(category=category).order_by("-created_at")

    def paginate(qs):
        # get_page는 out-of-range/비정상 값도 안전하게 처리합니다.
        return Paginator(qs, 10).get_page(page)

    ctx = {
        "active_tab": active_tab,
        "page_obj_fortune": paginate(q("fortune")),
        "page_obj_dream":   paginate(q("dream")),
        "page_obj_free":    paginate(q("free")),
    }
    return render(request, "home.html", ctx)


@require_http_methods(["GET", "POST"])
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # 댓글: 자유게시판만 허용
    comments_qs = post.comments.all().order_by("-created_at")
    cpage_num = safe_int(request.GET.get("cpage", 1), 1)
    comments_page = Paginator(comments_qs, 20).get_page(cpage_num)

    form = None
    if post.category == Post.Category.FREE:
        form = CommentForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                # 아주 간단한 rate-limit: 동일 IP가 15초 내 연속 작성 방지
                ip = get_client_ip(request)
                recent = Comment.objects.filter(
                    ip=ip, created_at__gte=timezone.now() - timezone.timedelta(seconds=15)
                ).exists()
                if recent:
                    form.add_error(None, "조금 천천히 작성해주세요. 잠시 후 다시 시도해 주세요.")
                else:
                    cm = form.save(commit=False)
                    cm.post = post
                    cm.ip = ip
                    cm.save()
                    return redirect(f"{post.get_absolute_url()}#comments")

    return render(request, "post_detail.html", {
        "post": post,
        "comments_page": comments_page,
        "form": form,
        "allow_comments": post.category == Post.Category.FREE,
        "active_tab": post.category,  # 탭 하이라이트를 상세에서도 유지
    })


@require_http_methods(["POST"])
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    cookie_key = f"liked_{post.slug}"
    if request.COOKIES.get(cookie_key) == "1":
        return JsonResponse({"ok": True, "like_count": post.like_count, "duplicate": True})

    Post.objects.filter(pk=post.pk).update(like_count=F("like_count") + 1)
    post.refresh_from_db(fields=["like_count"])

    resp = JsonResponse({"ok": True, "like_count": post.like_count})
    resp.set_cookie(cookie_key, "1", max_age=60 * 60 * 24 * 30, samesite="Lax")
    return resp


def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
