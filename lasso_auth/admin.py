# -*- coding: utf-8 -*-
from lasso.lasso_auth.models import *
from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    exclude = ('user_permissions', 'is_staff', 'is_superuser')
    list_display_links = list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'group', 'last_login', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')

admin.site.register(User, UserAdmin)
admin.site.register(Group)
