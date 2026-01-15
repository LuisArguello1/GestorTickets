from django.urls import path
from .views import (
    CompanyListView,
    CompanyDetailView,
    CompanyCreateView,
    CompanyUpdateView,
    CompanyDeleteView,
)

app_name = 'company'

urlpatterns = [
    path('', CompanyListView.as_view(), name='company_list'),
    path('<int:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    path('create/', CompanyCreateView.as_view(), name='company_create'),
    path('update/<int:pk>/', CompanyUpdateView.as_view(), name='company_update'),
    path('delete/<int:pk>/', CompanyDeleteView.as_view(), name='company_delete')
]
