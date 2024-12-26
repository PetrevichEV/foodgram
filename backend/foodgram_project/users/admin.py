from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
    )

    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('username',)
    list_display_links = ('username',)

