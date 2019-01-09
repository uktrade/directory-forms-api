import datetime
import pprint

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count

import core.helpers
from submission import constants, models


class ActionFilter(SimpleListFilter):
    title = 'action'
    parameter_name = 'action_name'

    def lookups(self, request, model_admin):
        return (
            (constants.ACTION_NAME_ZENDESK, 'Create Zendesk ticket'),
            (constants.ACTION_NAME_PARDOT, 'Submit to Pardot'),
            (constants.ACTION_NAME_EMAIL, 'Send via Email'),
            (constants.ACTION_NAME_GOV_NOTIFY, 'Send via Gov Notify'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            queryset = queryset.filter(meta__action_name=value)
        return queryset


@admin.register(models.Submission)
class SubmissionAdmin(core.helpers.DownloadCSVMixin, admin.ModelAdmin):
    search_fields = ('data', 'meta',)
    readonly_fields = ('client', 'created', 'is_sent', 'form_url')
    list_display = (
        'get_pretty_client',
        'form_url',
        'get_pretty_funnel',
        'action_name',
        'created',
        'is_sent',
        'sender'
    )
    list_filter = (
        'client',
        ActionFilter,
        'form_url',
        'created',
        'is_sent',
        'sender',
    )

    csv_filename = 'form-submissions_{timestamp}.csv'.format(
        timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            readonly_fields = self.readonly_fields
            return ('get_pretty_data', 'get_pretty_meta',) + readonly_fields
        return self.readonly_fields

    def get_exclude(self, request, obj=None):
        if obj:
            return ('data', 'meta', 'modified')
        return []

    def get_pretty_data(self, obj):
        return pprint.pformat(obj.data)

    def get_pretty_meta(self, obj):
        return pprint.pformat(obj.meta)

    def get_pretty_client(self, obj):
        return obj.client

    def get_pretty_funnel(self, obj):
        return ' > '.join(obj.funnel)

    get_pretty_data.short_description = 'Data'
    get_pretty_meta.short_description = 'Meta'
    get_pretty_client.short_description = 'Service'
    get_pretty_funnel.short_description = 'Funnel'


@admin.register(models.Sender)
class SenderAdmin(core.helpers.DownloadCSVMixin, admin.ModelAdmin):
    search_fields = ('email_address',)
    readonly_fields = ('created',)
    list_display = (
        'email_address',
        'is_whitelisted',
        'is_blacklisted',
        'get_submission_count',
    )
    list_filter = (
        'is_whitelisted',
        'is_blacklisted',
    )

    csv_filename = 'senders-{timestamp}.csv'.format(
        timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(submissions_count=Count('submissions'))
        return queryset

    def get_readonly_fields(self, request, obj=None):
        if obj:
            readonly_fields = self.readonly_fields
            return ('email_address',) + readonly_fields
        return self.readonly_fields

    def get_submission_count(self, obj):
        return obj.submissions_count

    get_submission_count.short_description = 'Submissions'
    get_submission_count.admin_order_field = 'submissions_count'
