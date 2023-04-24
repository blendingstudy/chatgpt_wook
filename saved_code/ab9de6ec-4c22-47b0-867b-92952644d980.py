import json

board = []  # 게시판 리스트 초기화

def post(title, content):
    """새로운 글을 작성합니다."""
    post = {
        'title': title,
        'content': content
    }
    board.append(post)
    save_board()

def get_posts():
    """게시판에 있는 모든 글을 가져옵니다."""
    return board

def get_post(title):
    """제목에 해당하는 글을 찾아서 가져옵니다."""
    for post in board:
        if post['title'] == title:
            return post
    return None

def delete_post(title):
    """제목에 해당하는 글을 삭제합니다."""
    for i, post in enumerate(board):
        if post['title'] == title:
            board.pop(i)
            save_board()
            return True
    return False

def save_board():
    """게시판을 JSON 파일에 저장합니다."""
    with open('board.json', 'w') as f:
        json.dump(board, f)

def load_board():
    """JSON 파일에서 게시판을 로드합니다."""
    try:
        with open('board.json', 'r') as f:
            global board
            board = json.load(f)
    except:
        board = []

load_board()  # 프로그램 시작 시 파일에서 게시판을 불러옵니다.