from django.urls import path

from apps.analytics import views

urlpatterns = [
    path("providers/performance/", views.ProviderPerformanceView.as_view(), name="provider-performance"),
    path("payers/performance/", views.PayerPerformanceView.as_view(), name="payer-performance"),
    path("members/utilization/", views.MemberUtilizationView.as_view(), name="member-utilization"),
    path("about/project/", views.AboutProjectView.as_view(), name="about-project"),
]
