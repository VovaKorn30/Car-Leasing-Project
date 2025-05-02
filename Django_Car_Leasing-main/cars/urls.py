from django.urls import path, include
from cars import views

app_name = 'cars'

urlpatterns = [
    # Маршрути для AI Chat
    path('gemini-chat/', views.gemini_chat, name='gemini_chat'),

    # Маршрути для каталога автомобілів
    path('', views.catalog, name='index'),
    path('page/<int:page>/', views.catalog, name='index'),
    path('search/', views.catalog, name='search'),

    # Маршрути для деталей автомобіля
    path('cars/', views.auto, name='auto'),
    path('cars/<str:car_code>/', views.auto, name='auto'),

    # Новий маршрут для отримання деталей пакету
    path('get-package-details/<int:package_id>/', views.package_details, name='package_details'),
]
