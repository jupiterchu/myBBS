from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.db import transaction

from .models import *


def delete_violation_article(model_admin, request, queryset):
    """对违规文章进行删除，并扣除积分"""
    try:
        with transaction.atomic():
            for obj in queryset:
                author = UserProfile.objects.get(id=obj.author_id)
                obj.alive = False
                author.points -= 2
                author.save()
                obj.save()
            messages.add_message(request, messages.INFO, '用户人：%s，违规文章已经删除' % author)
    except Exception as e:
        messages.add_message(request, messages.INFO, '文章删除失败，请重试')


delete_violation_article.short_description = u'删除违规文章'

class ArticleAdmin(admin.ModelAdmin):
    actions = (delete_violation_article,)
    # list_display = ('')


ADDITIONAL_FIELDS = ((None, {'fields': ('profile','points')}),)

class UserProfileAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ADDITIONAL_FIELDS
    add_fieldsets = UserAdmin.fieldsets + ADDITIONAL_FIELDS

admin.site.register(Article, ArticleAdmin)
admin.site.register(UserProfile, UserProfileAdmin)