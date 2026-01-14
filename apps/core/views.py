from django.shortcuts import render
from django.http import HttpResponse
from apps.ticket.models import Ticket
from apps.company.models import Company
from datetime import date
import os


def dashboard(request):
    """
    Vista del dashboard principal.
    Muestra estadísticas básicas de tickets y compañías.
    """
    # Estadísticas
    total_tickets = Ticket.objects.count()
    total_companies = Company.objects.count()
    tickets_today = Ticket.objects.filter(date__date=date.today()).count()
    recent_tickets = Ticket.objects.select_related('company').order_by('-date')[:5]

    context = {
        'total_tickets': total_tickets,
        'total_companies': total_companies,
        'tickets_today': tickets_today,
        'recent_tickets': recent_tickets,
    }

    return render(request, 'layouts/dashboard.html', context)


def service_worker(request):
    """
    Vista para servir el Service Worker desde la raíz.
    """
    sw_path = os.path.join(os.path.dirname(__file__), '../../static/sw.js')
    try:
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
        response = HttpResponse(content, content_type='application/javascript')
        # Headers para Service Workers - permitir cache pero detectar cambios
        response['Cache-Control'] = 'public, max-age=0'
        response['Service-Worker-Allowed'] = '/'
        return response
    except FileNotFoundError:
        return HttpResponse('Service Worker not found', status=404)
