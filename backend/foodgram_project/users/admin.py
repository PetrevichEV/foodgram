from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email',
                    'first_name', 'last_name', 'avatar')

    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('username',)
    list_display_links = ('username',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_display_links = ('id', 'user', 'author')
    search_fields = ('user__username', 'author__username')
