from django.shortcuts import render
from apps.ticket.models import Ticket
from apps.company.models import Company


def dashboard(request):
    """
    Vista del dashboard principal.
    Muestra estadísticas básicas de tickets y compañías.
    """
    # Estadísticas
    total_tickets = Ticket.objects.count()
    total_companies = Company.objects.count()
    tickets_today = Ticket.objects.filter(date__date__gte=request.GET.get('date', None)).count() if request.GET.get('date') else 0
    recent_tickets = Ticket.objects.select_related('company').order_by('-date')[:5]

    context = {
        'total_tickets': total_tickets,
        'total_companies': total_companies,
        'tickets_today': tickets_today,
        'recent_tickets': recent_tickets,
    }

    return render(request, 'layouts/dashboard.html', context)
