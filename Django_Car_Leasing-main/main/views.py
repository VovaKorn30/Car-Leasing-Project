import os

from django.core.checks import translation
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render
from django.shortcuts import redirect
from dotenv import find_dotenv, load_dotenv

from djangoProject import settings
from .models import Service

from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def index(request):
    context = {
        'title': 'Home - Главная',
        'content': _(
            "Лізинг разом з KornieievAuto — це ваш надійний шлях до нового автомобіля без зайвих клопотів. "
            "Ми пропонуємо гнучкі умови фінансування, мінімальний пакет документів та індивідуальний підхід до кожного клієнта. "
            "Обирайте комфорт, швидкість та безпеку разом з нами. "
            "Розпочніть свій шлях до власного авто вже сьогодні!"
        ),
        'image_path': 'deps/images/begin.png'
    }

    return render(request, 'main/index.html', context)





from django.utils.translation import activate
# views.py



def search(request):
    query = request.GET.get('q', '')
    services = Service.objects.filter(name__icontains=query) if query else Service.objects.all()
    context = {
        'services': services,
        'query': query,
    }
    return render(request, 'base.html', context)


def about(request):
    context = {
        'title': 'Home - О нас',
        'content': "О нас",
        'text_on_page': _("Цілі та області застосування веб-застосунку з надання послуг лізингу "
                          "авто можуть включати:1. Забезпечення зручності для клієнтів: Розробка "
                          "веб-застосунку дозволить клієнтам легко знаходити і оформляти угоди на "
                          "лізинг автомобілів, зменшуючи час і зусилля, необхідні для цього."
                          "2. Покращення доступності: Веб-застосунок може бути доступним для клієнтів "
                          "з будь-якого пристрою з Інтернет-підключенням, що робить послугу лізингу авто "
                          "більш доступною та зручною.3. Автоматизація процесів: Застосування веб-технологій "
                          "дозволяє автоматизувати багато аспектів управління лізинговими угодами, "
                          "включаючи розрахунок вартості, підписання документів та стеження за термінами "
                          "дії угод.4. Підвищення ефективності: Веб-застосунок може забезпечити ефективне "
                          "керування процесами лізингу, спрощуючи адміністративні завдання та зменшуючи "
                          "кількість помилок." )}

    return render(request, 'main/about.html', context)