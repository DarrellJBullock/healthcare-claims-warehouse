from django.urls import path

from apps.warehouse import views

urlpatterns = [
    path("dashboard/summary/", views.DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("claims/", views.ClaimListView.as_view(), name="claim-list"),
    path("claims/<str:claim_id>/", views.ClaimDetailView.as_view(), name="claim-detail"),
    path("data-quality/results/", views.DataQualityResultsView.as_view(), name="data-quality-results"),
    path("data-quality/run/", views.DataQualityRunView.as_view(), name="data-quality-run"),
    path("exports/", views.ExportsView.as_view(), name="exports"),
]
