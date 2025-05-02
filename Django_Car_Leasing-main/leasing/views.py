from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_GET
from .models import ServicePackage, LeasingContract
from .forms import LeasingContractForm
from django.contrib.auth.decorators import login_required
from cars.models import Car
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from datetime import datetime
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


def legalentities(request):
    return render(request, 'legalentities.html')


def individuals(request):
    return render(request, 'individuals.html')


@login_required
@csrf_protect
def create_contract(request, car_code):
    car = get_object_or_404(Car, code=car_code)
    service_packages = ServicePackage.objects.all()
    selected_package = None
    error_message = None
    car_part = (car.price / 100) * 2
    calculated_prices = []

    for package in service_packages:
        total_price = package.price * 12 + car_part
        calculated_prices.append({
            'package': package,
            'total_price': round(total_price, 2),
            'monthly_payment': round(total_price / 12, 2),
        })

    if request.method == 'POST':
        form = LeasingContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.user = request.user
            contract.car = car

            # Перевірка на накладання дат для цього авто
            overlapping = LeasingContract.objects.filter(
                car=car,
                start_date__lt=contract.start_date,
                end_date__gt=contract.end_date
            ).exclude(user=request.user)  # Ігноруємо контракти поточного користувача

            if overlapping.exists():
                error_message = _("Цей автомобіль вже заброньований на обраний період.")
            else:
                months = (contract.end_date - contract.start_date).days // 30
                contract.total_price = contract.service_package.price * months + car_part
                contract.monthly_payment = contract.total_price / months if months else 0
                contract.save()
                messages.success(request, _("Контракт успішно створено!"))
                return redirect('users:profile')  # Перенаправлення на профіль
    else:
        form = LeasingContractForm()

    package_id = request.GET.get('package')
    if package_id:
        selected_package = get_object_or_404(ServicePackage, id=package_id)
        form.fields['service_package'].initial = selected_package

    context = {
        'form': form,
        'car': car,
        'service_packages': service_packages,
        'selected_package': selected_package,
        'error_message': error_message,
        'calculated_prices': calculated_prices,
        'now': datetime.now()
    }
    return render(request, 'create_contract.html', context)


@login_required
def view_contracts(request):
    # Для перевірки прав доступу
    show_all = request.user.is_staff or request.user.is_superuser

    contracts = LeasingContract.objects.all() if show_all else LeasingContract.objects.filter(user=request.user)

    # Додаткові дані для шаблону
    contracts = contracts.select_related('car', 'user', 'service_package').order_by('-start_date')

    context = {
        'contracts': contracts,
        'page_title': _("Всі контракти лізингу"),
        'now': datetime.now(),
        'show_all': show_all
    }
    return render(request, 'contracts.html', context)


@login_required
def profile(request):
    # Для адмінів показуємо всі контракти
    show_all = request.user.is_staff or request.user.is_superuser

    contracts = LeasingContract.objects.all() if show_all else LeasingContract.objects.filter(user=request.user)

    # Оптимізація запитів до БД
    contracts = contracts.select_related('car', 'user', 'service_package').order_by('-start_date')

    context = {
        'contracts': contracts,
        'page_title': _("Особистий кабінет"),
        'now': datetime.now(),
        'show_all': show_all
    }
    return render(request, 'profile.html', context)


@require_GET
def get_package_details(request, package_id):
    try:
        package = ServicePackage.objects.get(id=package_id)
        data = {
            'id': package.id,
            'name': package.name,
            'price': float(package.price),
            'description': package.description,
            'services': [service.name for service in package.services.all()],
        }
        return JsonResponse(data)
    except ObjectDoesNotExist:
        return JsonResponse({'error': _("Пакет не знайдено")}, status=404)


def leasing_services(request):
    service_packages = ServicePackage.objects.prefetch_related('services').all()
    base_leasing = ServicePackage.objects.filter(name="Base Leasing").first()
    base_services_count = base_leasing.services.count() if base_leasing else 0

    for package in service_packages:
        package.base_services_count = base_services_count
        package.premium_services_count = package.services.count() - base_services_count \
            if package.name != "Base Leasing" else 0

    context = {
        'service_packages': service_packages,
        'page_title': _("Послуги лізингу")
    }
    return render(request, 'leasing_services.html', context)
