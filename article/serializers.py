from django.contrib.auth.hashers import make_password
# from django.contrib.auth.models import User
from rest_framework import serializers

from article.models import Article, Tag, Comment, UserProfile


class ArticleAPISerializer(serializers.ModelSerializer):
    """文章序列"""

    class Meta:
        model = Article
        fields = ('url', 'id', 'title', 'author', 'body', 'created_date')
        # fields = '__all__'
        extra_kwargs = {
            'alive': {'read_only': True}
        }


class UserProfileAPISerializer(serializers.ModelSerializer):
    """用户序列"""
    # article = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='article-detail')
    article = ArticleAPISerializer(read_only=True, many=True)

    class Meta:
        model = UserProfile
        fields = ('url', 'id', 'username', 'password', 'email', 'profile', 'points', 'article')
        # fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'points': {'read_only': True},
        }

    def validate(self, attrs):
        """对密码进行加密"""
        attrs['password'] = make_password(attrs['password'])
        return attrs


class TagAPISerializer(serializers.ModelSerializer):
    """标签序列"""

    class Meta:
        model = Tag
        fields = "__all__"


class CommentAPISerializer(serializers.ModelSerializer):
    """评论序列"""

    class Meta:
        model = Comment
        fields = ('url', 'id', 'aid', 'author', 'content', 'created_date')


class ReplyAPISerializer(CommentAPISerializer):
    """回复序列"""

    class Meta:
        model = Comment
        fields = ('url', 'id', 'aid', 'author', 'be_mid', 'content', 'created_date')


class NotificationsAPISerializer(serializers.Serializer):
    """通知序列"""

    content = serializers.CharField()
    author = serializers.CharField()
    uid = serializers.IntegerField()

    class Meta:
        fields = ('content', 'author', 'uid')
