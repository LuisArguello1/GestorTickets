# views.py
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from .models import Company
from .forms import CompanyForm

class CompanyCreateView(CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/modal_form.html'
    success_url = reverse_lazy('company:company_list')

    def get(self, request, *args, **kwargs):
        if Company.objects.exists():
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.warning(request, 'Solo se permite crear una compañía.')
            return redirect('company:company_list')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Compañía "{self.object.name}" creada exitosamente.')
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': str(self.get_success_url())})
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la compañía. Verifique los datos.')
        return super().form_invalid(form)

class CompanyUpdateView(UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/modal_form.html'
    success_url = reverse_lazy('company:company_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Compañía "{self.object.name}" actualizada exitosamente.')
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': str(self.get_success_url())})
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar la compañía. Verifique los datos.')
        return super().form_invalid(form)


class CompanyListView(ListView):
    model = Company
    template_name = 'company/company_list.html'
    context_object_name = 'companies'
    paginate_by = 10  

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
         
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(ruc__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create_company'] = not Company.objects.exists()
        # Breadcrumbs
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('core:dashboard')},
            {'label': 'Compañías'}
        ]
        return context

class CompanyDetailView(DetailView):
    model = Company
    template_name = 'company/company_detail.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Breadcrumbs
        context['breadcrumb_list'] = [
            {'label': 'Dashboard', 'url': reverse_lazy('core:dashboard')},
            {'label': 'Compañías', 'url': reverse_lazy('company:company_list')},
            {'label': self.object.name}
        ]
        return context

class CompanyDeleteView(DeleteView):
    model = Company
    template_name = 'company/modal_delete.html'
    success_url = reverse_lazy('company:company_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        company_name = self.object.name
        self.object.delete()
        messages.success(self.request, f'Compañía "{company_name}" eliminada exitosamente.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': str(self.success_url)})
        return super().post(request, *args, **kwargs)
