# board/urls.py
from django.urls import path
from .views import home, post_detail, like_post

urlpatterns = [
    path("", home, name="home"),
    path("post/<slug:slug>/", post_detail, name="post_detail"),
    path("post/<slug:slug>/like/", like_post, name="like_post"),
]