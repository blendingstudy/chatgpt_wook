# -*- coding: euc-kr -*-
import os
import openai
from flask import Flask, request, jsonify, render_template, send_from_directory
from bs4 import BeautifulSoup
import json, openai, requests
from pathlib import Path
import sqlite3
import re
import uuid

openai.api_key = "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"  
download_url = "http://127.0.0.1/"
app = Flask(__name__)
chatKey = "1"
chat_log = []
chat_list_log = []
DATABASE = "chat_history.db"

def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_list
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, chatName TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, chatKey INTEGER, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

def load_chat_list_history():
    create_table()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, chatName FROM chat_list")
    chat_list_log = [{"id": row[0], "chatName": row[1]} for row in c.fetchall()]
    conn.close()
    return chat_list_log

def load_chat_history(chatKey):
    create_table()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history where chatKey = " + chatKey)
    chat_log = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return chat_log

def save_chat_history(chatKey, role, content):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (chatKey, role, content) VALUES (?, ?, ?)", (chatKey, role, content))
    conn.commit()
    conn.close()

chat_log = load_chat_history("1")
chat_list_log = load_chat_list_history()

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

def process_and_store_code_block(code_block: str, chatKey: int, chatName: str, file_name: str) -> str:
    language_match = re.search(r"```(\w+)", code_block)
    if language_match:
        language = language_match.group(1).lower()
    else:
        language = "txt"

    extension = LANGUAGE_EXTENSIONS.get(language, "txt")
    if not file_name.endswith(f".{extension}"):
        file_name += f".{extension}"
    # 채팅목록에 맞는 폴더 없으면 생성하기
    createDirectory(CODE_STORAGE_PATH + "/" + str(chatKey) + "_" + chatName)
    file_path = os.path.join(CODE_STORAGE_PATH + "/" + str(chatKey) + "_" + chatName, file_name)
    
    with open(file_path, "w") as f:
        f.write(code_block)
    
    return file_name

def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")

def createProjectStructure(gpt_response):
    # gpt_response에 프로젝트 구조에 대한 답변이 포함돼있는지 확인
    print(gpt_response)
    structureTmp = gpt_response[gpt_response.find('```\n')+4:]
    structureContent = structureTmp[0:structureTmp.find('\n```')]
    if structureContent:
        print("구조 있다")
        print(structureContent)
    # - 폴더와 계층을 구별하는 방법
    # /로 끝나면 폴더로 간주
    # /로 끝나는데 왼쪽에 공백(탭) 또는 다른 특수문자 ( ㄴ..)가 있다면 하위계층 폴더로 간주.. 
    # 하위 > 하위 폴더는 \n ~ 폴더명/  앞까지의 길이로 몇레벨의 폴더인지 측정


def extract_filename(user_message: str, gpt_response: str, code_block:str, language: str) -> str:
    extensions_pattern = r'\.(?:py|js|html|ejs|css|java|c|cpp|cs|php|rb|swift|go|kt)'
    pattern = fr'\b(?:main|([a-zA-Z0-9-_]+)){extensions_pattern}\b'

    # 먼저 코드블럭 앞에서 파일 이름과 확장자를 추출합니다.
    before_code_block = gpt_response[0:gpt_response.find(code_block)]
    match = re.search(pattern, before_code_block[before_code_block.rfind("```"):])
    if match:
        return match.group()

    # 코드블럭 앞에서 찾지 못한 경우, 사용자 메시지에서 파일 이름과 확장자를 추출합니다.
    match = re.search(pattern, user_message)
    if match:
        return match.group()
    
    # 사용자 메시지에서 찾지 못한 경우, GPT 응답에서 파일 이름과 확장자를 추출합니다.
    match = re.search(pattern, gpt_response)
    if match:
        return match.group()
    
    # 파일 이름과 확장자를 찾지 못한 경우, 언어에 기반한 기본 이름과 확장자를 사용합니다.
    default_file_name = f"generated_code.{LANGUAGE_EXTENSIONS.get(language, 'txt')}"
    return default_file_name

def get_url_summary(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find("title")
        if title:
            return f"URL 요약: {title.string}"
        else:
            return "URL 요약: 제목을 찾을 수 없습니다."
    except Exception as e:
        print(f"Error getting URL summary: {e}")
        return "URL 요약: 요청 중 오류가 발생했습니다."

Path(CODE_STORAGE_PATH).mkdir(parents=True, exist_ok=True)

LANGUAGE_EXTENSIONS = {
    "python": "py",
    "javascript": "js",
    "html": "html",
    "ejs": "html",
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
    chatKey = data.get('chatKey')
    chatName = ""
    # chatKey가 없으면 newChat. 새로운chatKey 생성해야함
    if chatKey == None:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        # todo null일때 처리해주어야함
        c.execute("SELECT IFNULL(max(id), 0)+1 FROM chat_list")
        chatKey = c.fetchone()[0]
        chatName = user_message[0:10]
        if chatKey == 1:
            c.execute("UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'chat_list'")
            conn.commit()
            conn.close()
    else:
        # chatName가져오기
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT chatName FROM chat_list WHERE id = ?;",(chatKey,))
        chatName = c.fetchone()[0]
        conn.close()

    if user_message:
        if user_message.startswith("http://") or user_message.startswith("https://"):
            url_summary = get_url_summary(user_message)
            return jsonify({"response": url_summary})
        chat_log.append({"role": "user", "content": user_message})
        save_chat_history(chatKey, "user", user_message)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_log
        )
        gpt_response = response["choices"][0]["message"]["content"]
        chat_log.append({"role": "assistant", "content": gpt_response})
        save_chat_history(chatKey, "assistant", gpt_response)
        # 프로젝트 구조에 대한 답변일시 구조 생성
        createProjectStructure(gpt_response)
        code_block_matches = list(re.finditer(r"```\w+\n([\s\S]*?)```", gpt_response))
        download_links = []
        if code_block_matches:
            for match in code_block_matches:
                code_block = match.group(0)
                # 언어를 추출합니다.
                language_match = re.search(r"```(\w+)", code_block)
                if language_match:
                    language = language_match.group(1).lower()
                else:
                    # 기본 언어로 설정합니다.
                    language = "txt"
                file_name = extract_filename(user_message, gpt_response, code_block, language)
                stored_file_name = process_and_store_code_block(code_block, chatKey, chatName, file_name)
                download_link = f"{download_url}download/{stored_file_name}"
                download_links.append(download_link)

            gpt_response += "\n\n코드가 생성되었습니다. 다음 링크를 통해 다운로드하세요:"
            for link in download_links:
                gpt_response += f"\n{link}"

        return jsonify({"response": gpt_response, "chatKey" : chatKey})
    else:
        return jsonify({"error": "Invalid input"}), 400

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_from_directory(CODE_STORAGE_PATH, filename, as_attachment=True)

@app.route('/chat_list_history', methods=['GET'])
def get_chat_list_history():
    chat_list_log = load_chat_list_history()
    return jsonify(chat_list_log)

@app.route('/chat_history/<path:chatKey>', methods=['GET'])
def get_chat_history(chatKey):
    if chatKey != 'undefined':
        return jsonify(load_chat_history(chatKey))
    else:
        chat_log = load_chat_history("1")
        return jsonify(chat_log)

@app.route('/chat_list_delete/<path:chatKey>', methods=['GET'])
def chat_list_delete(chatKey):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM chat_list WHERE id = ?;",(chatKey,))
    c.execute("DELETE FROM chat_history WHERE chatKey = ?;",(chatKey,))
    conn.commit()
    conn.close()
    return "true"

@app.route('/chat_list_add/<path:chatKey>', methods=['GET'])
def chat_list_add(chatKey):
    # chatKey의 첫번째 답변이면 대화목록 생성
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    response = {}
    response["chatKey"] = chatKey
    c.execute("SELECT count() FROM chat_history where chatKey = ?; ", (chatKey,))
    row = c.fetchone();
    if row[0] == 2:
        response["addYn"] = "Y"
        c.execute("SELECT content FROM chat_history where chatKey = ? and role = 'user'; ", (chatKey,))
        chatName = c.fetchone()[0][0:10]
        conn.close()
        response["chatName"] = chatName
        # insert
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO chat_list (chatName) VALUES (?)", (chatName,))
        conn.commit()
        conn.close()
    else:
        response["addYn"] = "N" 
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)