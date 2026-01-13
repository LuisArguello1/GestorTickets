from django.urls import path
from apps.ticket.view.ticket_view import TicketListView, TicketDetailView

app_name = 'ticket'

urlpatterns = [
    path('tickets/', TicketListView.as_view(), name='ticket_list'),
    path('create/<int:pk>/ticket', TicketDetailView.as_view(), name='ticket_detail'),
]