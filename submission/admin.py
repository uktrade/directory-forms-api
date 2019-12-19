import datetime
import pprint

from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse

import core.helpers
from submission import constants, models, tasks


class FormUrlFilter(SimpleListFilter):
    title = 'form URL'
    parameter_name = 'form_url'
    common_urls = [
        '/contact/office-finder/*/',
        '/international/trade/suppliers/*/contact/',
        '/international/investment-support-directory/*/contact/',
        '/suppliers/*/contact/',
        '/investment-support-directory/*/contact/',
    ]

    def lookups(self, request, model_admin):
        queryset = models.Submission.objects.all()
        for url in self.common_urls:
            escaped = url.replace('/', r'\/').replace('*', '.+')
            queryset = queryset.exclude(form_url__iregex=f'{escaped}.*')
        lookups = list(queryset.values_list('form_url', flat=True))
        return [(item, item) for item in sorted(lookups + self.common_urls)]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            queryset = queryset.filter(form_url=value)
        return queryset


class ActionFilter(SimpleListFilter):
    title = 'action'
    parameter_name = 'action_name'

    def lookups(self, request, model_admin):
        return (
            (constants.ACTION_NAME_ZENDESK, 'Create Zendesk ticket'),
            (constants.ACTION_NAME_PARDOT, 'Submit to Pardot'),
            (constants.ACTION_NAME_EMAIL, 'Send via Email'),
            (
                constants.ACTION_NAME_GOV_NOTIFY_EMAIL,
                'Send Email via Gov Notify'
            ),
            (
                constants.ACTION_NAME_GOV_NOTIFY_LETTER,
                'Send letter via Gov Notify'
            ),
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
        FormUrlFilter,
        'created',
        'is_sent',
        'sender',
    )

    actions = core.helpers.DownloadCSVMixin.actions + ['retry']

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

    def retry(self, request, queryset):
        """Resend action that previously failed."""
        for item in queryset:
            if item.is_sent:
                messages.info(request, f'{item.pk} already sent. Skipped.')
            else:
                tasks.execute_for_submission(item)
                messages.success(request, f'{item.pk} send triggered.')
        return redirect(reverse('admin:submission_submission_changelist'))

    retry.short_description = "Retry sending this action."
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
        'blacklisted_reason',
        'get_submission_count',
    )
    list_filter = (
        'is_whitelisted',
        'is_blacklisted',
        'blacklisted_reason',
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
