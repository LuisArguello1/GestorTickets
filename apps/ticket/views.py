from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.forms import modelformset_factory
from .models import Ticket, TicketDetail
from .forms import TicketForm, TicketDetailForm, TicketDetailFormSet


class TicketListView(ListView):
    """
    Vista para listar tickets con filtros y búsqueda.
    """
    model = Ticket
    template_name = 'ticket/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10  # Paginación

    def get_queryset(self):
        queryset = super().get_queryset().select_related('company')
        # Filtros opcionales
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                client__icontains=search
            ) | queryset.filter(
                seller__icontains=search
            ) | queryset.filter(
                ci_ruc__icontains=search
            )
        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Ticket.objects.values_list('company', flat=True).distinct()
        return context


class TicketDetailView(DetailView):
    """
    Vista para ver detalles de un ticket específico.
    """
    model = Ticket
    template_name = 'ticket/ticket_detail.html'
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = self.object.details.all()  # Detalles del ticket
        return context