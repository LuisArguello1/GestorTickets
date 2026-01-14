from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.forms import modelformset_factory
from django.db import transaction
from apps.ticket.models import Ticket, TicketDetail
from apps.ticket.forms import TicketForm, TicketDetailForm


class TicketListView(ListView):
    """
    Vista para listar tickets con filtros y búsqueda.
    """
    model = Ticket
    template_name = 'ticket/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('company')
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
        context['details'] = self.object.details.all()
        return context


class TicketCreateView(CreateView):
    """
    Vista para crear un ticket con detalles usando formsets.
    """
    model = Ticket
    form_class = TicketForm
    template_name = 'ticket/ticket_form.html'
    success_url = reverse_lazy('ticket:ticket_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        TicketDetailFormSet = modelformset_factory(
            TicketDetail,
            form=TicketDetailForm,
            extra=1,  # Una fila extra para agregar
            can_delete=True,  # Permitir eliminar
        )
        if self.request.POST:
            context['detail_formset'] = TicketDetailFormSet(
                self.request.POST,
                queryset=TicketDetail.objects.none()
            )
        else:
            context['detail_formset'] = TicketDetailFormSet(
                queryset=TicketDetail.objects.none()
            )

        # Modal de éxito
        if self.request.GET.get('success') and self.request.GET.get('ticket_id'):
            try:
                ticket = Ticket.objects.get(pk=self.request.GET['ticket_id'])
                context['show_modal'] = True
                context['created_ticket'] = ticket
            except Ticket.DoesNotExist:
                pass

        context['is_edit'] = False

        # Agregar compañía por defecto y su IVA
        from apps.company.models import Company
        company = Company.objects.first()
        if company:
            context['default_company'] = company
            context['iva_percentage'] = company.iva_percentage

        return context

    def form_valid(self, form):
        TicketDetailFormSet = modelformset_factory(
            TicketDetail,
            form=TicketDetailForm,
            extra=1,
            can_delete=True,
        )
        detail_formset = TicketDetailFormSet(
            self.request.POST,
            queryset=TicketDetail.objects.none()
        )
        
        with transaction.atomic():
            # Asignar compañía por defecto
            from apps.company.models import Company
            form.instance.company = Company.objects.first()
            # Copiar IVA de la compañía
            form.instance.iva_percentage = form.instance.company.iva_percentage
            self.object = form.save()

            if detail_formset.is_valid():
                # Guardar detalles
                details = detail_formset.save(commit=False)
                
                # Verificar que hay al menos un detalle
                if not details:
                    messages.error(self.request, 'Debe agregar al menos un producto al ticket.')
                    return self.form_invalid(form)
                
                for detail in details:
                    detail.ticket = self.object
                    detail.save()
                
                # Actualizar total
                self.object.update_total()
                messages.success(self.request, f'Ticket {self.object.document_number} creado exitosamente.')
                
                # Redirigir con parámetros para modal
                return redirect(f"{reverse('ticket:ticket_create')}?success=1&ticket_id={self.object.pk}")
            else:
                messages.error(self.request, 'Error en los detalles del ticket. Verifique los datos.')
                return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el ticket. Verifique los datos.')
        return super().form_invalid(form)


class TicketUpdateView(UpdateView):
    """
    Vista para editar un ticket existente con sus detalles.
    """
    model = Ticket
    form_class = TicketForm
    template_name = 'ticket/ticket_form.html'
    success_url = reverse_lazy('ticket:ticket_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        TicketDetailFormSet = modelformset_factory(
            TicketDetail,
            form=TicketDetailForm,
            extra=0,  # No extra en edición
            can_delete=True,
        )
        if self.request.POST:
            context['detail_formset'] = TicketDetailFormSet(
                self.request.POST,
                queryset=self.object.details.all()
            )
        else:
            context['detail_formset'] = TicketDetailFormSet(
                queryset=self.object.details.all()
            )
        context['is_edit'] = True
        context['default_company'] = self.object.company
        context['iva_percentage'] = self.object.iva_percentage
        return context

    def form_valid(self, form):
        TicketDetailFormSet = modelformset_factory(
            TicketDetail,
            form=TicketDetailForm,
            extra=0,
            can_delete=True,
        )
        detail_formset = TicketDetailFormSet(
            self.request.POST,
            queryset=self.object.details.all()
        )
        
        with transaction.atomic():
            self.object = form.save()

            if detail_formset.is_valid():
                # Eliminar detalles marcados para eliminación
                for deleted_form in detail_formset.deleted_forms:
                    if deleted_form.instance.pk:
                        deleted_form.instance.delete()
                
                # Guardar detalles actualizados y nuevos
                details = detail_formset.save(commit=False)
                
                # Verificar que hay al menos un detalle
                remaining_details = self.object.details.count()
                new_details = len([d for d in details if not d.pk])
                deleted_details = len(detail_formset.deleted_forms)
                
                if remaining_details - deleted_details + new_details <= 0:
                    messages.error(self.request, 'Debe mantener al menos un producto en el ticket.')
                    return self.form_invalid(form)
                
                for detail in details:
                    detail.ticket = self.object
                    detail.save()
                
                # Actualizar total
                self.object.update_total()
                messages.success(self.request, f'Ticket {self.object.document_number} actualizado exitosamente.')
                return redirect(self.success_url)
            else:
                messages.error(self.request, 'Error en los detalles del ticket. Verifique los datos.')
                return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el ticket. Verifique los datos.')
        return super().form_invalid(form)


class TicketDeleteView(DeleteView):
    """
    Vista para eliminar un ticket.
    """
    model = Ticket
    template_name = 'ticket/ticket_confirm_delete.html'
    success_url = reverse_lazy('ticket:ticket_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Ticket eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class TicketPrintView(DetailView):
    """
    Vista para imprimir ticket en diferentes formatos.
    """
    model = Ticket
    template_name = 'ticket/ticket_print.html'
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = self.object.details.all()
        context['size'] = self.request.GET.get('size', '80')  # 58, 80, A4
        return context