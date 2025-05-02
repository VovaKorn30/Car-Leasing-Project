import json
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

from leasing.models import ServicePackage
from .models import Car
from .utils import q_search

# 🔐 Твій реальний ключ встав тут
GEMINI_API_KEY = "тут_твій_ключ"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

@csrf_exempt
def gemini_chat(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            user_message = body.get('message', '')

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GEMINI_API_KEY}"
            }

            # Формат згідно офіційної документації Gemini
            data = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": user_message}]
                }]
            }

            response = requests.post(GEMINI_API_URL, headers=headers, json=data)

            print("Gemini API response:", response.status_code, response.text)  # для дебагу

            if response.status_code == 200:
                try:
                    gemini_reply = response.json()['candidates'][0]['content']['parts'][0]['text']
                    return JsonResponse({'reply': gemini_reply})
                except (KeyError, IndexError):
                    return JsonResponse({'reply': 'Помилка обробки відповіді Gemini API'}, status=500)
            else:
                return JsonResponse({
                    'reply': f'Помилка запиту до Gemini API: {response.status_code}',
                    'details': response.text
                }, status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Невірний формат JSON у тілі запиту'}, status=400)

        except Exception as e:
            return JsonResponse({'error': f'Виникла неочікувана помилка: {e}'}, status=500)

    return JsonResponse({'error': 'Метод запиту має бути POST'}, status=400)


def auto(request, car_code):
    try:
        car = Car.objects.get(code=car_code)
        service_packages = ServicePackage.objects.all()
        base_leasing = ServicePackage.objects.filter(name="Base Leasing").first()
        base_services_count = base_leasing.services.count() if base_leasing else 0

        for package in service_packages:
            package.base_services_count = base_services_count
            package.premium_services_count = (
                package.services.count() - base_services_count if package.name != "Base Leasing" else 0
            )

        context = {
            'car': car,
            'service_packages': service_packages
        }
        return render(request, 'auto.html', context)
    except Car.DoesNotExist:
        return JsonResponse({'error': 'Автомобіль не знайдено'}, status=404)


def catalog(request):
    order_by = request.GET.get('order_by', 'default')
    discount_filter = request.GET.get('discount', 'false') == 'true'
    query = request.GET.get('q', None)

    cars = Car.objects.all()

    if discount_filter:
        cars = cars.filter(discount__isnull=False, discount__gt=0)

    if order_by == 'price':
        cars = cars.order_by('price')
    elif order_by == '-price':
        cars = cars.order_by('-price')
    elif query:
        cars = q_search(query)

    paginator = Paginator(cars, 9)
    page = request.GET.get('page', 1)

    try:
        cars_page = paginator.page(page)
    except PageNotAnInteger:
        cars_page = paginator.page(1)
    except EmptyPage:
        cars_page = paginator.page(paginator.num_pages)

    context = {
        'cars': cars_page,
        'order_by': order_by,
        'discount_filter': discount_filter,
    }
    return render(request, 'catalog.html', context)


def search(request):
    query = request.GET.get('q', '')
    cars = Car.objects.filter(name__icontains=query) if query else Car.objects.all()
    context = {
        'cars': cars,
        'query': query,
    }
    return render(request, 'catalog.html', context)


# Новий маршрут для отримання деталей пакету
def package_details(request, package_id):
    try:
        # Отримуємо деталі пакету за ID
        package = ServicePackage.objects.get(id=package_id)

        # Формуємо відповідь
        package_data = {
            'id': package.id,
            'name': package.name,
            'description': package.description,  # якщо є поле опису
            'services': [service.name for service in package.services.all()],  # список послуг
        }

        return JsonResponse({'package': package_data})
    except ServicePackage.DoesNotExist:
        return JsonResponse({'error': 'Пакет не знайдено'}, status=404)
