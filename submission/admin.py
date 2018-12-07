import datetime
import pprint

from django.contrib import admin
from django.contrib.admin import SimpleListFilter

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
class SubmissionAdmin(admin.ModelAdmin):
    search_fields = ('data', 'meta',)
    readonly_fields = ('created', 'is_sent', 'form_url')
    list_display = ('action_name', 'form_url', 'created', 'is_sent')
    list_filter = (ActionFilter, 'form_url', 'created', 'is_sent')
    actions = ['download_csv']

    csv_excluded_fields = []
    csv_filename = 'form-submissions_{}.csv'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

    def download_csv(self, request, queryset):
        return core.helpers.generate_csv_response(
            queryset=queryset,
            filename=self.csv_filename,
            excluded_fields=self.csv_excluded_fields
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

    download_csv.short_description = (
        "Download CSV report for selected form submissions"
    )
    get_pretty_data.short_description = 'Data'
    get_pretty_meta.short_description = 'Meta'
