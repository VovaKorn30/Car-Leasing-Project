from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import google.generativeai as genai
import json
import logging

logger = logging.getLogger(__name__)

# Глобальна змінна для моделі
gemini_model = None

def initialize_gemini():
    global gemini_model
    try:
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY не знайдено в settings.py")

        genai.configure(api_key=api_key)

        # Стабільна модель для тексту
        model_name = "models/gemini-1.5-pro-latest"
        gemini_model = genai.GenerativeModel(model_name)
        logger.info(f"✅ Ініціалізовано модель: {model_name}")
        return True

    except Exception as e:
        logger.error(f"❌ Помилка ініціалізації Gemini: {str(e)}")
        gemini_model = None
        return False

# Ініціалізація моделі при запуску
initialize_gemini()

@csrf_exempt
@require_http_methods(["GET", "POST"])
def chat_index(request):
    if request.method == 'GET':
        return render(request, 'chat/index.html')

    if not gemini_model:
        if not initialize_gemini():
            return JsonResponse({
                'error': 'AI сервіс недоступний. Спробуйте пізніше.',
                'status': 'service_unavailable'
            }, status=503)

    try:
        # Отримання повідомлення від користувача
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        user_message = data.get('message', '').strip()
        if not user_message:
            return JsonResponse({
                'error': 'Порожнє повідомлення',
                'status': 'bad_request'
            }, status=400)

        # Створення нової сесії чату
        chat_session = gemini_model.start_chat(history=[])
        response = chat_session.send_message(
            user_message,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2048,
            ),
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
        )

        if response.text:
            return JsonResponse({
                'user_message': user_message,
                'bot_reply': response.text,
                'status': 'success'
            })
        else:
            logger.warning(f"Пуста відповідь від Gemini. Відповідь: {response}")
            return JsonResponse({
                'error': 'Не вдалося отримати відповідь від AI',
                'status': 'no_response'
            }, status=500)

    except json.JSONDecodeError:
        logger.error("Невірний JSON у запиті")
        return JsonResponse({
            'error': 'Невірний формат запиту',
            'status': 'invalid_format'
        }, status=400)

    except Exception as e:
        logger.error(f"Помилка обробки запиту: {str(e)}")
        return JsonResponse({
            'error': 'Внутрішня помилка сервера',
            'status': 'server_error',
            'details': str(e)
        }, status=500)
