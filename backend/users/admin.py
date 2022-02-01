from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('email', 'username',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
