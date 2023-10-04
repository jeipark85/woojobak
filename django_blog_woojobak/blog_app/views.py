from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required

# 회원가입 0925
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages

from rest_framework import generics
from bs4 import BeautifulSoup

from .serializers import BlogPostSerializer
from .forms import CustomLoginForm, BlogPostForm

from .models import BlogPost

import openai  # GPT-3 라이브러리


# 로그인
def custom_login(request):
    if request.user.is_authenticated:
        return redirect("/")

    form = CustomLoginForm(data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")

    return render(request, "registration/login.html", {"form": form})

#회원가입
@csrf_exempt
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]

        # 중복 닉네임 확인
        if User.objects.filter(username=username).exists():
            messages.error(request, "이미 사용 중인 닉네임입니다.")
        elif password != confirm:
            messages.error(request, "비밀번호가 일치하지 않습니다.")
        else:
            # user 객체를 새로 생성
            user = User.objects.create_user(username=username, password=password)
            # 로그인
            login(request, user)
            return redirect("/")

    return render(request, "registration/signup.html")


# 포스트리스트
def post_list(request, topic=None):
    # 특정 주제로 필터링
    if topic:
        posts = BlogPost.objects.filter(topic=topic, publish="Y").order_by("-views")

    else:
        posts = BlogPost.objects.filter(publish="Y").order_by("-views")
    return render(request, "blog_app/post_list.html", {"posts": posts})


# 포스트 RESTful API뷰 생성
class BlogPostList(generics.ListCreateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer


# 포스트 업로드, 업데이트, 삭제
@login_required
def create_or_update_post(request, post_id=None):
    # 글수정 페이지의 경우
    if post_id:
        post = get_object_or_404(BlogPost, id=post_id)

    # 글쓰기 페이지의 경우, 임시저장한 글이 있는지 검색
    else:
        post = (
            BlogPost.objects.filter(author_id=request.user.username, publish="N")
            .order_by("-created_at")
            .first()
        )

    # 업로드/수정 버튼 눌렀을 떄
    if request.method == "POST":
        form = BlogPostForm(request.POST, instance=post)  # 폼 초기화
        if form.is_valid():
            post = form.save(commit=False)

            # 게시물 삭제
            if "delete-button" in request.POST:
                post.delete()
                return redirect("blog_app:post_list")

            if not form.cleaned_data.get("topic"):
                post.topic = "전체"

            # 임시저장 여부 설정
            if "temp-save-button" in request.POST:
                post.publish = "N"
            else:
                post.publish = "Y"

            # 글쓴이 설정
            post.author_id = request.user.username

            post.save()
            return redirect("blog_app:post_detail", post_id=post.id)  # 업로드/수정한 페이지로 리다이렉트

    # 수정할 게시물 정보를 가지고 있는 객체를 사용해 폼을 초기화함
    else:
        form = BlogPostForm(instance=post)

    template = "blog_app/write.html"
    context = {
        "form": form,
        "post": post,
        "edit_mode": post_id is not None,
        "MEDIA_URL": settings.MEDIA_URL,
    }  # edit_mode: 글 수정 모드여부

    return render(request, template, context)


# 포스트 상세보기, 조회수 증가, 관련글(이전/다음글, 추천글) 가져오기
def post_detail(request, post_id):
    # 포스트 id로 게시물 가져옴
    post = get_object_or_404(BlogPost, id=post_id)

    if request.method == "POST":
        # 요청에 삭제가 포함된경우
        if "delete-button" in request.POST:
            post.delete()
            return redirect("blog_app:post_list")

    # 조회수 증가 및 db에 저장
    post.views += 1
    post.save()

    # 이전/다음 게시물 가져옴
    previous_post = BlogPost.objects.filter(id__lt=post.id, publish="Y").order_by("-id").first()
    next_post = BlogPost.objects.filter(id__gt=post.id, publish="Y").order_by("id").first()

    # 같은 주제인 게시물들 중 최신 글 가져옴
    recommended_posts = (
        BlogPost.objects.filter(topic=post.topic, publish="Y")
        .exclude(id=post.id)
        .order_by("-created_at")[:2]
    )
    # 게시물 내용에서 첫번째 이미지(썸네일) 태그 추출
    for recommended_post in recommended_posts:
        soup = BeautifulSoup(recommended_post.content, "html.parser")
        image_tag = soup.find("img")
        recommended_post.image_tag = str(image_tag) if image_tag else ""

    context = {
        "post": post,
        "previous_post": previous_post,
        "next_post": next_post,
        "recommended_posts": recommended_posts,
        "MEDIA_URL": settings.MEDIA_URL,
    }

    return render(request, "blog_app/post.html", context)


# 이미지 업로드
class image_upload(View):
    # 사용자가 이미지 업로드 하는경우 실행
    def post(self, request):
        # file필드 사용해 요청에서 업로드한 파일 가져옴
        file = request.FILES["file"]

        # 저장 경로 생성
        filepath = "uploads/" + file.name

        # 파일 저장
        filename = default_storage.save(filepath, file)

        # 파일 URL 생성
        file_url = settings.MEDIA_URL + filename

        # 이미지 업로드 완료시 JSON 응답으로 이미지 파일의 url 반환
        return JsonResponse({"location": file_url})


# API_Key 추가 0925
API_KEY = getattr(settings, "OPENAI", "OPENAI")
# Chat gpt API 사용
openai.api_key = "API_KEY"


# 글 자동완성 기능
def autocomplete(request):
    if request.method == "POST":
        # 제목 필드값 가져옴
        prompt = request.POST.get("title")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
            # 반환된 응답에서 텍스트 추출해 변수에 저장
            message = response["choices"][0]["message"]["content"]
        except Exception as e:
            message = str(e)
        return JsonResponse({"message": message})
    return render(request, "autocomplete.html")


# 테스트용 페이지
def test_view(request):
    return render(request, "blog_app/test.html")
