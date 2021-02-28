from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from article import views

router = routers.DefaultRouter()
router.register('users', views.UserProfileAPIViewSet)
router.register('articles', views.ArticleAPIViewSet)
router.register('comment', views.CommentAPIViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('docs', include_docs_urls('BBS')),
]
