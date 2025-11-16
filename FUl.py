from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from PIL import Image, ImageDraw, ImageFont
from ollama import Ollama
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
API_BASE = http://localhost:8080
HEADERS = {"Content-Type": "application/json"}
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def create_post(post_author: int, format_str: str) -> dict:
    url = f"{API_BASE}/api/post"
    data = {"post_author": post_author, "format": format_str}
    response = requests.post(url, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_post(post_id: str) -> dict:
    url = f"{API_BASE}/api/post/{post_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def set_main_text(post_id: str, main_text: str) -> dict:
    url = f"{API_BASE}/api/post/{post_id}/main_text"
    data = {"main_text": main_text}
    response = requests.put(url, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def generate_text(prompt: str) -> dict:
    url = f"{API_BASE}/api/tool/generate_text"
    data = {"prompt": prompt}
    response = requests.post(url, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def generate_image(prompt: str) -> dict:
    url = f"{API_BASE}/api/tool/generate_image"
    data = {"prompt": prompt}
    response = requests.post(url, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def add_layer_image(post_id: str, image_base64: str) -> dict:
    url = f"{API_BASE}/api/post/{post_id}/layer/image"
    data = {"image_base64": image_base64}
    response = requests.post(url, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def add_layer_text(post_id: str, text: str) -> dict:
    url = f"{API_BASE}/api/post/{post_id}/layer/text"
    data = {"text": text}
    response = requests.post(url, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def add_layer_rectangle(post_id: str, rectangle_data: dict) -> dict:
    """rectangle_data example: {'color': '#37','width': 512, 'height': 512}"""
    url = f"{API_BASE}/api/post/{post_id}/layer/rectangle"
    response = requests.post(url, json=rectangle_data, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def update_layer(post_id: str, layer_id: str, update_data: dict) -> dict:
    url = f"{API_BASE}/api/post/{post_id}/layer/{layer_id}"
    response = requests.put(url, json=update_data, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def delete_layer(post_id: str, layer_id: str) -> dict:
    url = f"{API_BASE}/api/post/{post_id}/layer/{layer_id}"
    response = requests.delete(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def publish_post(post_id: str) -> dict:
    url = f"{API_BASE}/api/post/{post_id}/publish"
    response = requests.post(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def render_post(post_id: str) -> bytes:

    url = f"{API_BASE}/api/post/{post_id}/render"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.content

#Словарь
available_functions = {
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
}

async def start_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info(f"{user.id} {user.full_name}")
    await update.message.reply_html(
    )

async def handle_message(update: Update, context: CallbackContext) -> None:

    user_id = update.message.from_user.id
    user_text = update.message.text
    chat_id = update.message.chat_id
    logger.info(f"[{user_id}] Получено сообщение: '{user_text}'")

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


                        tool_output = function_to_call(**function_args)

                        if function_name == 'render_post':
                            image_bytes = tool_output # render_post возвращает байты
                            logger.info(f"  Результат '{function_name}': ({len(image_bytes)}).")
                            await context.bot.send_photo(chat_id=chat_id, photo=InputFile(image_bytes), caption=f"отрендеренный пост {function_args.get('post_id', 'Unknown')}")
                        else:
                            logger.info(f"  Результат '{function_name}': {tool_output}")
                            await context.bot.send_message(chat_id=chat_id, text=f"Выполнено: {function_name}.\nРезультат: {json.dumps(tool_output, indent=2, ensure_ascii=False)}")
        else:
            text_response = response_message.get('content', 'Извините, я не могу обработать ваш запрос.')
            logger.info(f"Текстовый ответ модели: {text_response}")
            await context.bot.send_message(chat_id=chat_id, text=text_response)
#ГЛАВНАЯ ФУНКЦИЯ ДЛЯ ЗАПУСКА
def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

