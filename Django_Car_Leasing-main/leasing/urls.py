from django.urls import path
from . import views

app_name = 'leasing'

urlpatterns = [
    path('legalentities/', views.legalentities, name='legalentities'),
    path('individuals/', views.individuals, name='individuals'),
    path('contracts/', views.view_contracts, name='view_contracts'),
    path('contract/<str:car_code>/', views.create_contract, name='create_contract'),
    path('services/', views.leasing_services, name='leasing_services'),
    path('get-package-details/<int:package_id>/', views.get_package_details, name='get_package_details'),

]
