from django.urls import path

from apps.compliance import views

urlpatterns = [
    path("compliance/summary/", views.ComplianceSummaryView.as_view(), name="compliance-summary"),
    path("audit-log/", views.AuditLogView.as_view(), name="audit-log"),
    path("audit-log/role-changed/", views.RoleChangedView.as_view(), name="role-changed"),
]
