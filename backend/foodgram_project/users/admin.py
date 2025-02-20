from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscription

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email',
                    'first_name', 'last_name', 'avatar')

    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('username',)
    list_display_links = ('username',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_display_links = ('id', 'user', 'author')
    search_fields = ('user__username', 'author__username')
