# blog/urls.py
from django.urls import path
from .views import home, post_detail, like_post

urlpatterns = [
    path("", home, name="home"),
    path("post/<str:slug>/", post_detail, name="post_detail"),     # ← 변경
    path("post/<str:slug>/like/", like_post, name="like_post"),    # ← 변경
]
