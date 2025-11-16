def __init__(self, message_text: str, user_id: int):
        self.message = type('Message', (object,), {
            'text': message_text,
            'from_user': type('User', (object,), {'id': user_id})
        })()

class CallbackContext:
    def __init__(self):
        self.bot = type('Bot', (object,), {
            'send_photo': self._mock_send_photo,
            'send_message': self._mock_send_message
        })()

    def _mock_send_photo(self, chat_id, photo, caption=None):

    def _mock_send_message(self, chat_id, text):
#API_BASE =
HEADERS = {"Content-Type": "application/json"}

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

#glossary:
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

def start(update: Update, context: CallbackContext):
    pass

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_text = update.message.text
    print(f"[{user_id}] Получено сообщение: '{user_text}'")

 ollama_response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': user_text}],
            tools=list(available_functions.values()),
        )
        response_message = ollama_response.get('message', {})

            for tool_call in response_message['tool_calls']:
                function_name = tool_call['function']['name']
                function_args = tool_call['function']['arguments'] #аргументы в виде словаря

                function_to_call = available_functions.get(function_name)

if function_name == 'create_post' and 'post_author' not in function_args:
    function_args['post_author'] = user_id
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
                            context.bot.send_photo(chat_id=update.message.from_user.id, photo=image_bytes, caption=f"  пост {function_args.get('post_id')}")
                        else:
                            print(f"  Результат '{function_name}': {tool_output}")
                            context.bot.send_message(chat_id=update.message.from_user.id, text=f"сделано: {function_name}.результат: {tool_output}")

class MockFunctionCall:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments # дляOllama это уже словарь

class MockToolCall:
    def __init__(self, function_call):
        self.function = function_call

class MockMessageOllama:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = [MockToolCall(MockFunctionCall(tc['function']['name'], tc['function']['arguments'])) for tc in tool_calls] if tool_calls else None # Ollama возвращетNone если нет tool_calls

class MockOllamaResponse:
    def __init__(self, message_content=None, tool_calls=None):
        self.message = MockMessageOllama(content=message_content, tool_calls=tool_calls).__dict__

    def get(self, key, default=None):
        if key == 'message':
            return self.message
        return default

def simulate_ollama_response(user_text: str):
    if "создай пост" in user_text.lower():
        format_str = "1:1"
        if "16:9" in user_text: format_str = "16:9"
        elif "512x512" in user_text: format_str = "512x512"
        return MockOllamaResponse(tool_calls=[{
            'function': {'name': 'create_post', 'arguments': {'post_author': 123, 'format_str': format_str}}
        }])
    elif "получи пост" in user_text.lower() and "id" in user_text.lower():
        parts = user_text.split("id ")
        post_id = parts[1].split()[0] if len(parts) > 1 else "some-default-id"
        return MockOllamaResponse(tool_calls=[{
            'function': {'name': 'get_post', 'arguments': {'post_id': post_id}}
        }])
    elif "рендери пост" in user_text.lower() and "id" in user_text.lower():
        parts = user_text.split("id ")
        post_id = parts[1].split()[0] if len(parts) > 1 else "some-default-id"
        return MockOllamaResponse(tool_calls=[{
            'function': {'name': 'render_post', 'arguments': {'post_id': post_id}}
        }])
    elif "сгенерируй текст" in user_text.lower():
        prompt = user_text.replace("сгенерируй текст о", "").strip()
        return MockOllamaResponse(tool_calls=[{
            'function': {
                'name': 'generate_text',
                'arguments': {'prompt': prompt}
            }
        }])
    elif "добавь прямоугольник" in user_text.lower() and "id" in user_text.lower():
        parts = user_text.split("id ")
        post_id = parts[1].split()[0] if len(parts) > 1 else "some-default-id"
        return MockOllamaResponse(tool_calls=[{
            'function': {
                'name': 'add_layer_rectangle',
                'arguments': {'post_id': post_id, 'rectangle_data': {'color': '#FF0000', 'width': 100, 'height': 200}}
            }
        }]))])



    test_context = CallbackContext()



