from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InputFile
import requests
import json
import os
import logging
import time
from PIL import Image, ImageDraw, ImageFont
from ollama import Ollama

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# URL AI агента (замените на реальный URL)
AI_AGENT_URL = os.getenv("AI_AGENT_URL", "http://localhost:8080")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HEADERS = {"Content-Type": "application/json"}


# Функция для отправки запросов к AI агенту
def call_ai_agent(endpoint: str, data: dict, tg_id: int, response_type: str = 'json') -> any:
    """Универсальная функция для вызова AI агента"""

    # Специальный случай для /api/auth/init - прямой формат
    if endpoint == "/api/auth/init":
        url = f"{AI_AGENT_URL}{endpoint}"
        request_data = data  # Прямой формат без обертки
    else:
        # Обернутый формат для всех остальных endpoints
        url = f"{AI_AGENT_URL}{endpoint.split('/')[-1]}" if endpoint.startswith(
            '/api/') else f"{AI_AGENT_URL}{endpoint}"
        request_data = {
            "endpoint": endpoint,
            "data": data,
            "tg_id": tg_id,
            "timestamp": int(time.time())
        }

    logger.info(f"Отправка запроса к AI агенту: {url}")
    logger.info(f"Данные: {json.dumps(request_data, ensure_ascii=False)}")

    response = requests.post(url, json=request_data, headers=HEADERS)
    response.raise_for_status()

    if response_type == 'json':
        return response.json()
    else:  # 'bytes'
        return response.content


# Переписанные функции для работы с AI агентом
def init_user(tg_id: int, username: str) -> dict:
    """Инициализация пользователя - ПРЯМОЙ формат"""
    return call_ai_agent(
        endpoint="/api/auth/init",
        data={
            "tg_id": tg_id,
            "username": username
        },
        tg_id=tg_id
    )


def create_post(post_author: int, format_str: str) -> dict:
    """Создание поста - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint="/api/post",
        data={
            "post_author": post_author,
            "format": format_str
        },
        tg_id=post_author
    )


def get_post(post_id: str, tg_id: int) -> dict:
    """Получение поста - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint=f"/api/post/{post_id}",
        data={},
        tg_id=tg_id
    )


def set_main_text(post_id: str, main_text: str, tg_id: int) -> dict:
    """Установка основного текста - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint=f"/api/post/{post_id}/main_text",
        data={"main_text": main_text},
        tg_id=tg_id
    )


def generate_text(prompt: str, tg_id: int, nko_data: dict = None) -> dict:
    """Генерация текста - ОБЁРНУТЫЙ формат"""
    data = {"prompt": prompt}
    if nko_data:
        data["nko"] = nko_data

    return call_ai_agent(
        endpoint="/generate_text",
        data=data,
        tg_id=tg_id
    )


def generate_image(desc: str, tg_id: int, nko_data: dict = None, image_url: str = None, file_id: str = None) -> dict:
    """Генерация изображения - ОБЁРНУТЫЙ формат"""
    data = {"desc": desc}
    if nko_data:
        data["nko"] = nko_data
    if image_url:
        data["image_url"] = image_url
    if file_id:
        data["file_id"] = file_id

    return call_ai_agent(
        endpoint="/generate_image",
        data=data,
        tg_id=tg_id
    )


def add_layer_image(post_id: str, image_base64: str, tg_id: int) -> dict:
    """Добавление изображения как слоя - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint=f"/api/post/{post_id}/layer/image",
        data={"image_base64": image_base64},
        tg_id=tg_id
    )


def add_layer_text(post_id: str, text: str, tg_id: int) -> dict:
    """Добавление текста как слоя - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint=f"/api/post/{post_id}/layer/text",
        data={"text": text},
        tg_id=tg_id
    )


def add_layer_rectangle(post_id: str, rectangle_data: dict, tg_id: int) -> dict:
    """Добавление прямоугольника как слоя - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint=f"/api/post/{post_id}/layer/rectangle",
        data=rectangle_data,
        tg_id=tg_id
    )


def update_layer(post_id: str, layer_id: str, update_data: dict, tg_id: int) -> dict:
    """Обновление слоя - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint=f"/api/post/{post_id}/layer/{layer_id}",
        data=update_data,
        tg_id=tg_id
    )


def delete_layer(post_id: str, layer_id: str, tg_id: int) -> dict:
    """Удаление слоя - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint=f"/api/post/{post_id}/layer/{layer_id}",
        data={},
        tg_id=tg_id
    )


def publish_post(post_id: str, tg_id: int) -> dict:
    """Публикация поста - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint=f"/api/post/{post_id}/publish",
        data={},
        tg_id=tg_id
    )


def render_post(post_id: str, tg_id: int) -> bytes:
    """Рендер поста - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint=f"/api/post/{post_id}/render",
        data={},
        tg_id=tg_id,
        response_type='bytes'
    )


def edit_text(text: str, tg_id: int) -> dict:
    """Редактирование текста - ОБЁРНУТЫЙ формат"""
    return call_ai_agent(
        endpoint="/edit_text",
        data={"text": text},
        tg_id=tg_id
    )


def content_plan(days: str, freq: str, tg_id: int, nko_data: dict = None) -> dict:
    """Создание контент-плана - ОБЁРНУТЫЙ формат"""
    data = {
        "days": days,
        "freq": freq
    }
    if nko_data:
        data["nko"] = nko_data

    return call_ai_agent(
        endpoint="/content_plan",
        data=data,
        tg_id=tg_id
    )


# Словарь доступных функций
available_functions = {
    'init_user': init_user,
    'create_post': create_post,
    'get_post': get_post,
    'set_main_text': set_main_text,
    'generate_text': generate_text,
    'generate_image': generate_image,
    'add_layer_image': add_layer_image,
    'add_layer_text': add_layer_text,
    'add_layer_rectangle': add_layer_rectangle,
    'update_layer': update_layer,
    'delete_layer': delete_layer,
    'publish_post': publish_post,
    'render_post': render_post,
    'edit_text': edit_text,
    'content_plan': content_plan,
}


async def start_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"{user.id} {user.full_name}")

    # Инициализация пользователя при старте
    try:
        init_user(tg_id=user.id, username=user.username or user.full_name)
        logger.info(f"Пользователь {user.id} инициализирован")
    except Exception as e:
        logger.error(f"Ошибка инициализации пользователя: {e}")

    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот для создания постов.",
    )


async def help_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /help"""
    await update.message.reply_text("Помощь по боту...")


async def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик текстовых сообщений"""
    user_id = update.message.from_user.id
    user_text = update.message.text
    chat_id = update.message.chat_id

    logger.info(f"[{user_id}] Получено сообщение: '{user_text}'")

    try:
        # Здесь должен быть код для вызова Ollama или другой AI модели
        # Временно заглушка для тестирования
        ollama_response = {
            'message': {
                'content': 'Это тестовый ответ. Реализуйте интеграцию с Ollama.',
                'tool_calls': []
            }
        }

        response_message = ollama_response.get('message', {})

        if response_message.get('tool_calls'):
            logger.info("Модель предложила вызвать функции.")
            for tool_call in response_message['tool_calls']:
                function_name = tool_call['function']['name']
                function_args = tool_call['function']['arguments']

                function_to_call = available_functions.get(function_name)

                if function_to_call:
                    logger.info(f"  Вызов: {function_name}({function_args})")
                    try:
                        # Добавляем tg_id в аргументы для всех функций, кроме init_user
                        if function_name != 'init_user' and 'tg_id' not in function_args:
                            function_args['tg_id'] = user_id
                            logger.info(f"    Добавлен tg_id: {user_id}")

                        if function_name == 'create_post' and 'post_author' not in function_args:
                            function_args['post_author'] = user_id
                            logger.info(f"    Добавлен post_author: {user_id}")

                        if function_name == 'add_layer_rectangle' and 'rectangle_data' not in function_args:
                            rect_data = {}
                            for key in ['color', 'width', 'height']:
                                if key in function_args:
                                    rect_data[key] = function_args.pop(key)
                            if rect_data:
                                function_args['rectangle_data'] = rect_data

                        # Вызываем функцию
                        tool_output = function_to_call(**function_args)

                        # Обрабатываем специальные случаи
                        if function_name == 'render_post':
                            image_bytes = tool_output  # render_post возвращает байты
                            logger.info(f"  Результат '{function_name}': ({len(image_bytes)} байт).")
                            await context.bot.send_photo(
                                chat_id=chat_id,
                                photo=InputFile(image_bytes),
                                caption=f"Отрендеренный пост {function_args.get('post_id', 'Unknown')}"
                            )
                        else:
                            logger.info(f"  Результат '{function_name}': {tool_output}")
                            await context.bot.send_message(
                                chat_id=chat_id,
                                text=f"Выполнено: {function_name}.\nРезультат: {json.dumps(tool_output, indent=2, ensure_ascii=False)}"
                            )
                    except Exception as e:
                        logger.error(f"Ошибка при вызове функции {function_name}: {e}")
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"Ошибка при выполнении {function_name}: {str(e)}"
                        )
        else:
            text_response = response_message.get('content', 'Извините, я не могу обработать ваш запрос.')
            logger.info(f"Текстовый ответ модели: {text_response}")
            await context.bot.send_message(chat_id=chat_id, text=text_response)

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Произошла ошибка при обработке запроса.")


# Главная функция для запуска
def main() -> None:
    """Запуск бота"""
    from telegram.ext import Application

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()