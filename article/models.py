from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    profile = models.CharField(max_length=250, verbose_name="个人简介")
    points = models.IntegerField(default=0, verbose_name='积分')

    class Meta:
        db_table = 'user'
        verbose_name = u'用户'
        verbose_name_plural = u'用户'
        # ordering = ('date_joined',)

    def __str__(self):
        return f"User <{self.username}>"


class Article(models.Model):
    """文章模型类"""
    title = models.CharField('标题', max_length=100, null=True)
    author = models.ForeignKey(UserProfile, related_name='article', on_delete=models.CASCADE, verbose_name='作者')
    body = models.TextField('正文', blank=False, default='')
    alive = models.BooleanField('是否有效', default=True)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'article'
        verbose_name = u'文章'
        verbose_name_plural = u'文章'

    def __str__(self):
        return f"Article <{self.title}>"


class Tag(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    class Meta:
        db_table = 'tag'
        verbose_name = u'标签'
        verbose_name_plural = u'标签'

    def __str__(self):
        return f"Tag <{self.name}>"


class Comment(models.Model):
    aid = models.ForeignKey(Article, related_name='aid', on_delete=models.CASCADE, verbose_name='评论的文章')
    author = models.ForeignKey(UserProfile, related_name='mid', on_delete=models.CASCADE, verbose_name='评论者')
    be_mid = models.IntegerField(default=0, verbose_name='被回复用户')
    root = models.IntegerField(default=0, verbose_name='根评论')
    parent = models.IntegerField(default=0, verbose_name='父评论')  # 可以根据它来知道被评论用户
    content = models.TextField(blank=False, verbose_name='评论内容')
    like = models.IntegerField(default=0, verbose_name='点赞数')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'comment'
        verbose_name = u'评论'
        verbose_name_plural = u'评论'

    def __str__(self):
        return f"Comment <{self.aid.title}>"
