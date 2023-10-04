from django.db import models
from django.conf import settings

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    topic = models.CharField(max_length=255, default='전체')
    publish = models.CharField(max_length=1, default='Y')
    views = models.IntegerField(default=0)
    author_id = models.CharField(max_length=100, null=True, blank=True)
    # view_count = models.IntegerField()
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_articles')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # '..' 문자열이 포함된 content 필드를 변경
        self.content = self.content.replace('"..', '"')
        super().save(*args, **kwargs)



class ImageId(models.Model):
    pass

class TitleImageId(models.Model):
    pass

from django.db import models

class User(models.Model):
    username = models.CharField(max_length=64, verbose_name = '아이디')
    password = models.CharField(max_length=64, verbose_name = '비밀번호')
    email = models.EmailField(max_length=64, verbose_name = '이메일')
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name = '가입일자')

    class Meta:
        db_table = 'user'             
        ordering = ['-registered_at']
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
        
    def __str__(self):
        return self.username
    

    
class BGM(models.Model):
    title = models.CharField(max_length=50)
    singer = models.CharField(max_length=50)
    
class Comment(models.Model):
    article = models.ForeignKey(BlogPost,null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content
    
