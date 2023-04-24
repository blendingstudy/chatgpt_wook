import os
import json

# �Խ��� ���ϸ� ����
BOARD_FILENAME = 'board.json'

# �Խñ� Ŭ����
class Post:
    def __init__(self, title, content):
        self.title = title
        self.content = content

# �Խ��� Ŭ����
class Board:
    # �Խ��� �ʱ�ȭ
    def __init__(self):
        # �Խñ� ����Ʈ�� ���´�
        self.posts = []

        # �Խ��� ���� �ε�
        self.load()

    # �Խñ� �ۼ�
    def write_post(self, title, content):
        # �Խñ� �߰�
        self.posts.append(Post(title, content))

        # �Խ��� ���� ����
        self.save()

    # �Խñ� ��ȸ
    def read_posts(self):
        return self.posts

    # �Խñ� ����
    def delete_post(self, title):
        deleted = False

        for post in self.posts:
            if post.title == title:
                self.posts.remove(post)
                deleted = True
                break

        # �Խñ��� �����Ǿ����� �Խ��� ���� ����
        if deleted:
            self.save()

        return deleted

    # �Խ��� ���� ����
    def save(self):
        with open(BOARD_FILENAME, 'w') as f:
            json.dump([post.__dict__ for post in self.posts], f)

    # �Խ��� ���� �ε�
    def load(self):
        if os.path.exists(BOARD_FILENAME):
            with open(BOARD_FILENAME, 'r') as f:
                data = json.load(f)
                self.posts = [Post(**post_dict) for post_dict in data]