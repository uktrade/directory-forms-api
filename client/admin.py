from django.contrib import admin
from django.contrib import messages

from client import models


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'identifier', 'is_active',)
    list_filter = ('created', 'is_active',)
    readonly_fields = ('identifier',)

    MESSAGE_CREATE = 'Client {obj.identifier} created with key {obj.access_key}'

    def get_readonly_fields(self, request, obj):
        if obj:
            return self.readonly_fields + ('get_starred_access_key',)
        return self.readonly_fields

    def get_exclude(self, request, obj=None):
        if obj:
            return ('access_key',)
        return []

    def save_model(self, request, obj, form, change):
        if not change:
            message = self.MESSAGE_CREATE.format(obj=obj)
            self.message_user(request, message, messages.SUCCESS)
        return super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_starred_access_key(self, request, obj=None):
        return '*' * 64

    get_starred_access_key.short_description = 'Access key'
