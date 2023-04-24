import os
import json

# 게시판 파일명 설정
BOARD_FILENAME = 'board.json'

# 게시글 클래스
class Post:
    def __init__(self, title, content):
        self.title = title
        self.content = content

# 게시판 클래스
class Board:
    # 게시판 초기화
    def __init__(self):
        # 게시글 리스트를 갖는다
        self.posts = []

        # 게시판 파일 로드
        self.load()

    # 게시글 작성
    def write_post(self, title, content):
        # 게시글 추가
        self.posts.append(Post(title, content))

        # 게시판 파일 저장
        self.save()

    # 게시글 조회
    def read_posts(self):
        return self.posts

    # 게시글 삭제
    def delete_post(self, title):
        deleted = False

        for post in self.posts:
            if post.title == title:
                self.posts.remove(post)
                deleted = True
                break

        # 게시글이 삭제되었으면 게시판 파일 저장
        if deleted:
            self.save()

        return deleted

    # 게시판 파일 저장
    def save(self):
        with open(BOARD_FILENAME, 'w') as f:
            json.dump([post.__dict__ for post in self.posts], f)

    # 게시판 파일 로드
    def load(self):
        if os.path.exists(BOARD_FILENAME):
            with open(BOARD_FILENAME, 'r') as f:
                data = json.load(f)
                self.posts = [Post(**post_dict) for post_dict in data]