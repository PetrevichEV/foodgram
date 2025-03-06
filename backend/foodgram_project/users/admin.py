from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'avatar', 'is_active', 'is_superuser')
    list_display_links = ('username',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('is_active', 'is_superuser')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_display_links = ('user', 'author')
    list_filter = ('user__username',)

    def get_queryset(self, request):
        """Оптимизация запросов."""
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'author')
