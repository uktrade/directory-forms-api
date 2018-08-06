from django.contrib import admin
from django.contrib import messages

from client import models


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'identifier', 'is_active',)
    list_filter = ('created', 'is_active',)
    readonly_fields = ('identifier', 'access_key',)

    MESSAGE_CREATE = 'Client {obj.identifier} created. Key: {obj.access_key}'

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
