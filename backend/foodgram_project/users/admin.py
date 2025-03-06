from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'avatar', 'is_active', 'is_superuser')
    list_filter = ('is_active', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_display_links = ('username',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_display_links = ('user', 'author')
    search_fields = ('user',)
    list_filter = ('user__username', 'author__username')

    def get_queryset(self, request):
        """Оптимизация запросов."""
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'author')
