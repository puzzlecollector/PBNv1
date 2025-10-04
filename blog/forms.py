from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    username = forms.CharField(
        label="이름",
        max_length=50,
        widget=forms.TextInput(attrs={"placeholder": "닉네임 또는 이름"})
    )
    content = forms.CharField(
        label="내용",
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": "댓글 내용을 입력하세요"})
    )

    class Meta:
        model = Comment
        fields = ["username", "content"]
