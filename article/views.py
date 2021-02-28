from django.http import QueryDict
from django_redis import get_redis_connection
from notifications.signals import notify
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from article.filter import ArticleFilters
from article.permissions import IsOwnerOrReadOnly
from article.serializers import *


class UserProfileAPIViewSet(viewsets.ModelViewSet):
    """
    允许用户查看的或编辑的用户 API 路径.
    """
    queryset = UserProfile.objects.all()  # .order_by('-date_joined')
    serializer_class = UserProfileAPISerializer
    permission_classes = [IsOwnerOrReadOnly, ]

    def create(self, request, *args, **kwargs):
        serializer = UserProfileAPISerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path='activities')
    def activities(self, request, *args, **kwargs):
        try:
            article = Article.objects.filter(author=request.user.id, alive=True)
            article_serializer = ArticleAPISerializer(article, context={'request': request}, many=True)
        except Article.DoesNotExist:
            article_serializer = ''

        try:
            comment = Comment.objects.filter(mid=request.user.id)
            comment_serializer = CommentAPISerializer(comment, context={'request': request}, many=True)
        except Comment.DoesNotExist:
            comment_serializer = ''
        result = {
            'article': article_serializer.data if article_serializer else '',
            'comment': comment_serializer.data if comment_serializer else '',
        }

        return Response(result)


def get_cache_counter(aid: int):
    """
    获取 redis 中文章的阅读数
    :param aid: 缓存文章 id
    :return: 文章阅读数
    """
    cache = get_redis_connection()
    counter_number = cache.get(aid)
    if counter_number is None:
        cache.set(aid, 1)
        counter_number = 1
    else:
        cache.incr(aid)
        counter_number = int(counter_number) + 1
    return counter_number


class ArticleAPIViewSet(viewsets.ReadOnlyModelViewSet):
    """
    允许用户查看的或编辑的文章 API 路径.
    """
    queryset = Article.objects.all().order_by('-created_date')
    serializer_class = ArticleAPISerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsOwnerOrReadOnly, ]

    filter_class = ArticleFilters
    search_fields = ['title', 'body']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        author = request.user
        author.points += 1
        author.save()
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """只能获取未删除的文章"""
        instance = self.get_object()
        if not instance.alive:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        result = {
            "code": 200,
            "msg": "成功获取文章信息",
            "data": serializer.data
        }
        num = get_cache_counter(kwargs['pk'])
        result['data'].update({'read': num})  # 添加文章阅读数
        return Response(result)

    @action(methods=['GET'], detail=True, url_path='delete', permission_classes=[IsAuthenticated, ])
    def delete(self, request, *args, **kwargs):
        """用户只能删除自己的文章"""
        try:
            if request.user != self.get_object().author:
                return Response(status=status.HTTP_404_NOT_FOUND)

            article = self.get_object()
            article.alive = False
            article.save()
            return Response(status.HTTP_200_OK)
        except Article.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=["GET"], detail=True, url_path='root_comments')
    def root_comments(self, request, pk, *args, **kwargs):
        """获取当前文章的所有评论"""
        queryset = Comment.objects.filter(aid=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CommentAPISerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentAPIViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentAPISerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        # 给评论用户增加 1 点积分
        user = request.user
        user.points += 1
        user.save()

        recipient = request.data['aid']
        recipient = UserProfile.objects.get(id=int(recipient))

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        comment_url = serializer.data['url']
        notify.send(user, recipient=recipient, verb=u'有人评论了你', description=comment_url)
        return Response(serializer.data)

    @action(methods=["POST"], detail=False, url_path='reply')
    def reply(self, request, *args, **kwargs):
        """回复评论"""
        bid = int(request.data['be_mid'])
        data = QueryDict(request.data.urlencode(), mutable=True)
        recipient = UserProfile.objects.get(id=int(bid))
        prefix = f'@{recipient.username} '
        data['content'] = prefix + request.data['content']

        serializer = ReplyAPISerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        comment_url = serializer.data['url']
        notify.send(request.user, recipient=recipient, verb=u'有人回复的你', description=comment_url)

        return Response(serializer.data)

    @action(methods=["GET"], detail=True, url_path='anchor_more_comments')
    def anchor_more_comments(self, request, pk, *args, **kwargs):
        """获取当前评论的所有回复"""
        # TODO
        queryset = self.get_queryset().filter(be_mid=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class NotificationsAPIViewSet(APIView):

    def get(self, request, *args, **kwargs):
        # TODO 从消息队列中获取信息
        pass
        # notify = None
        # serializer = NotificationsAPISerializer(data=notify, many=True)
        # serializer.is_valid()
        # return Response(serializer.data)
