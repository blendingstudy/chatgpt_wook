import json

board = []  # �Խ��� ����Ʈ �ʱ�ȭ

def post(title, content):
    """���ο� ���� �ۼ��մϴ�."""
    post = {
        'title': title,
        'content': content
    }
    board.append(post)
    save_board()

def get_posts():
    """�Խ��ǿ� �ִ� ��� ���� �����ɴϴ�."""
    return board

def get_post(title):
    """���� �ش��ϴ� ���� ã�Ƽ� �����ɴϴ�."""
    for post in board:
        if post['title'] == title:
            return post
    return None

def delete_post(title):
    """���� �ش��ϴ� ���� �����մϴ�."""
    for i, post in enumerate(board):
        if post['title'] == title:
            board.pop(i)
            save_board()
            return True
    return False

def save_board():
    """�Խ����� JSON ���Ͽ� �����մϴ�."""
    with open('board.json', 'w') as f:
        json.dump(board, f)

def load_board():
    """JSON ���Ͽ��� �Խ����� �ε��մϴ�."""
    try:
        with open('board.json', 'r') as f:
            global board
            board = json.load(f)
    except:
        board = []

load_board()  # ���α׷� ���� �� ���Ͽ��� �Խ����� �ҷ��ɴϴ�.