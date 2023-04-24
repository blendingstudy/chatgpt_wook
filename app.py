from flask import Flask, request, jsonify, render_template, send_from_directory
from bs4 import BeautifulSoup
import json, openai, requests
from pathlib import Path
import uuid
import re
import os

#download_url = "https://naver.com/"
download_url = ""

app = Flask(__name__)

chat_log = []

CHAT_HISTORY_FILE = "chat_history.json"

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat_history(chat_log):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(chat_log, f)

with open("config.json", "r") as f:
    config = json.load(f)

openai.api_key = config["API_KEY"]
print( "apikey" ,  openai.api_key )

chat_log = load_chat_history()

@app.route('/')
def home():
    return render_template('index.html')

current_url = None

def search_title_in_url(url, search_title):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all('a', text=search_title)
        return [{"text": link.text, "href": link.get('href')} for link in links]
    except Exception as e:
        print(f"Error searching title in URL: {e}")
        return None
    
    
def find_links_with_partial_title(soup, partial_title):
    links = soup.find_all('a', string=lambda text: text and partial_title in text)
    return [{"text": link.text, "href": link['href']} for link in links if 'href' in link.attrs]

CODE_STORAGE_PATH = "saved_code"

def process_and_store_code_block(code_block: str) -> str:
    language_match = re.search(r"```(\w+)", code_block)
    if language_match:
        language = language_match.group(1).lower()
    else:
        language = "txt"

    extension = LANGUAGE_EXTENSIONS.get(language, "txt")
    code = re.search(r"```\w+\n([\s\S]*?)```", code_block).group(1).strip()
    file_name = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(CODE_STORAGE_PATH, file_name)
    
    with open(file_path, "w") as f:
        f.write(code)
    
    return file_name


Path(CODE_STORAGE_PATH).mkdir(parents=True, exist_ok=True)


LANGUAGE_EXTENSIONS = {
    "python": "py",
    "javascript": "js",
    "html": "html",
    "css": "css",
    "java": "java",
    "c": "c",
    "cpp": "cpp",
    "csharp": "cs",
    "php": "php",
    "ruby": "rb",
    "swift": "swift",
    "go": "go",
    "kotlin": "kt",
}


@app.route('/message', methods=['POST'])
def process_message():
    global chat_log
    global base_url
    data = request.get_json()
    user_message = data.get('message')

    if user_message:
        if user_message.startswith("!지정"):
            base_url = user_message[5:].strip()
            chat_log.append({"role": "user", "content": user_message})
            chat_log.append({"role": "assistant", "content": f"URL 지정: {base_url}"})
            save_chat_history(chat_log)
            return jsonify({"response": f"URL 지정: {base_url}"})

        if user_message.startswith("!검색"):
            search_title = user_message[5:].strip()
            if base_url:
                try:
                    response = requests.get(base_url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser")
                    matching_links = find_links_with_partial_title(soup, search_title)
                    if matching_links:
                        response_text = "검색 결과:\n" + "\n".join([f'{link["text"]}: {link["href"]}' for link in matching_links])
                    else:
                        response_text = "검색 결과가 없습니다."
                except Exception as e:
                    response_text = f"검색 중 오류가 발생했습니다: {e}"
            else:
                response_text = "기본 URL이 지정되지 않았습니다. !지정 명령으로 URL을 지정해주세요."

            chat_log.append({"role": "user", "content": user_message})
            chat_log.append({"role": "assistant", "content": response_text})
            save_chat_history(chat_log)
            return jsonify({"response": response_text})

        chat_log.append({"role": "user", "content": user_message})
        save_chat_history(chat_log)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_log
        )
        gpt_response = response["choices"][0]["message"]["content"]
        chat_log.append({"role": "assistant", "content": gpt_response})
        save_chat_history(chat_log)

        code_block_match = re.search(r"```\w+\n([\s\S]*?)```", gpt_response)
        if code_block_match:
            file_name = process_and_store_code_block(gpt_response)
            download_link = f"{download_url}download/{file_name}"
            gpt_response = gpt_response+ f"코드가 생성되었습니다. 다음 링크를 통해 다운로드하세요: {download_link}"
        
        chat_log.append({"role": "assistant", "content": gpt_response})
        save_chat_history(chat_log)

        return jsonify({"response": gpt_response})
    else:
        return jsonify({"error": "Invalid input"}), 400
    

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_from_directory(CODE_STORAGE_PATH, filename, as_attachment=True)
    
    
@app.route('/chat_history', methods=['GET'])
def get_chat_history():
    return jsonify(chat_log)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)