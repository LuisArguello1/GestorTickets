from django.urls import path
from . import views

app_name = 'ticket'

urlpatterns = [
    path('tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('create/<int:pk>/ticket', views.TicketDetailView.as_view(), name='ticket_detail'),
]