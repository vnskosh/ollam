from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from ollama import Ollama
#скрипт

#API_BASE =
def start(update: Update, context: CallbackContext):
    import json
    import time
    import requests

    payload = {
        "endpoint": "/generate_text",
        "data": {
            "mode": "free",
            "idea": "новости",
            "nko": {
                "name": "Название НКО",
                "description": "Описание",
                "activities": "Деятельность",
                "style": "разговорный"
            }
        },
        "timestamp": int(time.time())
    }
 headers = {"Content-Type": "application/json"}

def create_post(post_author: int, format_str: str):
    url = f"{API_BASE}/api/post"
    data = {
        "post_author": post_author,
        "format": format_str
    }
    response = requests.post(url, json=data)
    return response.json()

def get_post(post_id: str):
    url = f"{API_BASE}/api/post/{post_id}"
    response = requests.get(url)
    return response.json()

def set_main_text(post_id: str, main_text: str):
    url = f"{API_BASE}/api/post/{post_id}/main_text"
    data = {"main_text": main_text}
    response = requests.put(url, json=data)
    return response.json()

def generate_text(prompt: str):
    url = f"{API_BASE}/api/tool/generate_text"
    data = {"prompt": prompt}
    response = requests.post(url, json=data)
    return response.json()

def generate_image(prompt: str):
    url = f"{API_BASE}/api/tool/generate_image"
    data = {"prompt": prompt}
    response = requests.post(url, json=data)
    return response.json()

def add_layer_image(post_id: str, image_base64: str):
    url = f"{API_BASE}/api/post/{post_id}/layer/image"
    data = {"image_base64": image_base64}
    response = requests.post(url, json=data)
    return response.json()

def add_layer_text(post_id: str, text: str):
    url = f"{API_BASE}/api/post/{post_id}/layer/text"
    data = {"text": text}
    response = requests.post(url, json=data)
    return response.json()

def add_layer_rectangle(post_id: str, rectangle_data: dict):
    """rectangle_data example: {'color': '#37','width': 512, 'height': 512}"""
    url = f"{API_BASE}/api/post/{post_id}/layer/rectangle"
    response = requests.post(url, json=rectangle_data)
    return response.json()

def update_layer(post_id: str, layer_id: str, update_data: dict):
    url = f"{API_BASE}/api/post/{post_id}/layer/{layer_id}"
    response = requests.put(url, json=update_data)
    return response.json()

def delete_layer(post_id: str, layer_id: str):
    url = f"{API_BASE}/api/post/{post_id}/layer/{layer_id}"
    response = requests.delete(url)
    return response.json()

def publish_post(post_id: str):
    url = f"{API_BASE}/api/post/{post_id}/publish"
    response = requests.post(url)
    return response.json()

def start(update: Update, context: CallbackContext):
    pass

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    if text.lower().startswith("/createpost"):
        format_str = "1:1"
        parts = text.split()
        if len(parts) > 1:
            if parts[1] in ["1:1", "512x512", "16:9"]:
                format_str = parts[1]
        result = create_post(post_author=user_id, format_str=format_str)

if text.lower().startswith("/createpost"):
    parts = text.split(None, 1)
    format_str = "1:1"
    if len(parts) > 1 and parts[1] in ["1:1", "512x512", "16:9"]:
        format_str = parts[1]
    result = create_post(post_author=user_id, format_str=format_str)

elif text.lower().startswith("/getpost"):
    parts = text.split(None, 1)
    if len(parts) > 1:
        post_id = parts[1]
        result = get_post(post_id)

elif text.lower().startswith("/setmaintext"):
    parts = text.split(None, 2)
    if len(parts) > 2:
        post_id = parts[1]
        main_text = parts[2]
        result = set_main_text(post_id, main_text)

elif text.lower().startswith("/gentext"):
    prompt = text[len("/gentext "):]
    result = generate_text(prompt)


ollama_client = Ollama()
ollama_response = ollama.chat(
    model='llama3',
    messages=[{'role': 'user', 'content': user_text}],
    tools=list(available_functions.values()),
)

if __name__ == "__main__":
    user_input = str(input())
    #available_functions = {}

    main(user_input, available_functions)

git init
git commit -m "Initial commit с кодом Ollama"
git remote add origin <https://github.com/vnskosh/ollam.git>
git push -u origin main    