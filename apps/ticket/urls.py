from django.urls import path
from apps.ticket.view.ticket_view import (
    TicketListView, TicketDetailView, TicketCreateView,
    TicketUpdateView, TicketDeleteView, TicketPrintView, TicketMassPrintView, export_tickets_excel
)

app_name = 'ticket'

urlpatterns = [
    path('', TicketListView.as_view(), name='ticket_list'),
    path('crear/', TicketCreateView.as_view(), name='ticket_create'),
    path('<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('<int:pk>/editar/', TicketUpdateView.as_view(), name='ticket_update'),
    path('<int:pk>/eliminar/', TicketDeleteView.as_view(), name='ticket_delete'),
    path('<int:pk>/imprimir/', TicketPrintView.as_view(), name='ticket_print'),
    path('imprimir-masa/', TicketMassPrintView.as_view(), name='ticket_mass_print'),
    path('exportar-excel/', export_tickets_excel, name='ticket_export_excel'),
]