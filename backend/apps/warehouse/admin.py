from django.contrib import admin

from .models import (
    RawAdjustment,
    RawClaim,
    RawClaimServiceLine,
    RawDenialCode,
    RawDiagnosisCategory,
    RawEligibility,
    RawMember,
    RawPayer,
    RawPayment,
    RawProcedureCategory,
    RawProvider,
)


@admin.register(RawMember)
class RawMemberAdmin(admin.ModelAdmin):
    list_display = ("member_id", "plan_type", "gender", "effective_date", "term_date")
    search_fields = ("member_id", "subscriber_id")
    list_filter = ("plan_type", "gender")


@admin.register(RawProvider)
class RawProviderAdmin(admin.ModelAdmin):
    list_display = ("provider_id", "provider_name", "specialty", "network_status")
    search_fields = ("provider_id", "provider_name")
    list_filter = ("specialty", "network_status")


@admin.register(RawPayer)
class RawPayerAdmin(admin.ModelAdmin):
    list_display = ("payer_id", "payer_name", "payer_type")
    list_filter = ("payer_type",)


@admin.register(RawClaim)
class RawClaimAdmin(admin.ModelAdmin):
    list_display = ("claim_id", "member", "provider", "payer", "claim_status", "billed_amount", "paid_amount")
    search_fields = ("claim_id",)
    list_filter = ("claim_status", "claim_type")


admin.site.register(RawClaimServiceLine)
admin.site.register(RawPayment)
admin.site.register(RawAdjustment)
admin.site.register(RawEligibility)
admin.site.register(RawDenialCode)
admin.site.register(RawDiagnosisCategory)
admin.site.register(RawProcedureCategory)
