from django_filters.rest_framework import FilterSet

from article.models import Article


class ArticleFilters(FilterSet):
    """自定义过滤类"""

    class Meta:
        model = Article
        fields = ('title', 'body')