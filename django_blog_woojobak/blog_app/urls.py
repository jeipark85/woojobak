from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import image_upload


app_name = "blog_app"
urlpatterns = [
    path("login/", views.custom_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.post_list, name="post_list"),
    path("post_list/<str:topic>/", views.post_list, name="post_list_by_topic"),
    path("api/blog_posts/", views.BlogPostList.as_view(), name="blogpost-list"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("write/", views.create_or_update_post, name="create_or_update_post"),
    path("edit_post/<int:post_id>/", views.create_or_update_post, name="create_or_update_post"),
    path("image-upload/", image_upload.as_view(), name="image_upload"),
    path("autocomplete/", views.autocomplete, name="autocomplete"),
    path("test/", views.test_view, name="test_view"),
    # 회원가입 0925
    path("signup/", views.register, name="signup"),
    # 좋아요
    path('<int:blogpost_pk>/likes_list/', views.likes_list, name='likes_list'),
    path('<int:blogpost_pk>/likes_post/', views.likes_post, name='likes_post'),
    # 댓글
    path('<int:pk>/comments/', views.comments_create, name='comments_create'),
    path('<int:article_pk>/comments/<int:comment_pk>/delete/', views.comments_delete, name='comments_delete')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
