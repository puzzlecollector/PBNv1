from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.db.models import F
from .models import Post, Comment
from .forms import CommentForm

def home(request):
    active_tab = request.GET.get("tab", "fortune")
    page = int(request.GET.get("page", 1))

    def q(category):
        return Post.objects.filter(category=category).order_by("-created_at")

    def paginate(qs):
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

    # 댓글: 자유게시판에만 허용
    comments_qs = post.comments.all().order_by("-created_at")
    cpage_num = int(request.GET.get("cpage", 1))
    comments_page = Paginator(comments_qs, 20).get_page(cpage_num)

    form = None
    if post.category == Post.Category.FREE:
        form = CommentForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                # 간단한 rate-limit: 동일 IP가 15초 내 연속 작성 방지
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
        "active_tab": post.category,
    })


@require_http_methods(["POST"])
def like_post(request, slug):
    """
    좋아요(비로그인): 단순 카운트 증가
    - CSRF 필요 (템플릿에서 토큰 전송)
    - 과도한 중복 방지: 쿠키 또는 세션으로 guard (아주 간단한 버전)
    """
    post = get_object_or_404(Post, slug=slug)

    # 쿠키 키
    cookie_key = f"liked_{post.slug}"
    if request.COOKIES.get(cookie_key) == "1":
        # 이미 좋아요 누른 경우: 현재 수만 반환
        return JsonResponse({"ok": True, "like_count": post.like_count, "duplicate": True})

    # 증가 (경쟁 상태 고려하여 F표현)
    Post.objects.filter(pk=post.pk).update(like_count=F("like_count") + 1)
    post.refresh_from_db(fields=["like_count"])

    resp = JsonResponse({"ok": True, "like_count": post.like_count})
    # 30일 유지
    resp.set_cookie(cookie_key, "1", max_age=60 * 60 * 24 * 30, samesite="Lax")
    return resp


def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
