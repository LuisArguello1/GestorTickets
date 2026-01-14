# views.py
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Company
from .forms import CompanyForm
from django.shortcuts import get_object_or_404
from django.db.models import Q




class CompanyCreateView(CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/modal_form.html'
    success_url = reverse_lazy('company:company_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': str(self.get_success_url())})
        return response

class CompanyUpdateView(UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/modal_form.html'
    success_url = reverse_lazy('company:company_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': str(self.get_success_url())})
        return response


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

class CompanyDeleteView(DeleteView):
    model = Company
    template_name = 'company/modal_delete.html'
    success_url = reverse_lazy('company:company_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': str(self.success_url)})
        return super().post(request, *args, **kwargs)
