from django.contrib import admin

from .models import AuditEvent, DataQualityResult


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("event_timestamp", "user_role", "action", "resource_type", "status")
    list_filter = ("action", "status", "user_role")
    search_fields = ("user_id", "resource_id")


@admin.register(DataQualityResult)
class DataQualityResultAdmin(admin.ModelAdmin):
    list_display = ("check_name", "table_name", "severity", "status", "failed_count", "created_at")
    list_filter = ("severity", "status", "table_name")
