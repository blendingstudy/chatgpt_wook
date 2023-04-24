import os
import json
from datetime import datetime

# 게시판 파일명 설정
BOARD_FILENAME = os.path.join('data', 'board.json')

# 게시글 클래스
class Post:
    def __init__(self, title, content, author, date):
        self.title = title
        self.content = content
        self.author = author
        self.date = date

    def __repr__(self):
        return f'{self.title} by {self.author} on {self.date}'

# 게시판 클래스
class Board:
    def __init__(self):
        self.posts = []
        self.load()

    def write_post(self, title, content, author):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.posts.append(Post(title, content, author, now))
        self.save()

    def read_posts(self):
        return self.posts

    def delete_post(self, title):
        deleted = False

        for post in self.posts:
            if post.title == title:
                self.posts.remove(post)
                deleted = True
                break

        if deleted:
            self.save()

        return deleted

    def save(self):
        with open(BOARD_FILENAME, 'w') as f:
            data = [{
                'title': post.title,
                'content': post.content,
                'author': post.author,
                'date': post.date
            } for post in self.posts]
            json.dump(data, f)

    def load(self):
        if os.path.exists(BOARD_FILENAME):
            with open(BOARD_FILENAME, 'r') as f:
                data = json.load(f)
                self.posts = [Post(**post_dict) for post_dict in data]


def main():
    board = Board()

    while True:
        print('Menu')
        print('1. Write a post')
        print('2. Read posts')
        print('3. Delete a post')
        print('4. Exit')
        choice = input('Enter your choice: ')

        if choice == '1':
            title = input('Enter the title of your post: ')
            content = input('Enter the content of your post: ')
            author = input('Enter your name: ')
            board.write_post(title, content, author)
            print('Your post has been added successfully!')

        elif choice == '2':
            posts = board.read_posts()
            if not posts:
                print('There are no posts yet.')
            else:
                print('List of posts:')
                for post in posts:
                    print(post)
                print()

        elif choice == '3':
            title = input('Enter the title of the post you want to delete: ')
            deleted = board.delete_post(title)
            if deleted:
                print('The post has been deleted successfully.')
            else:
                print('The post was not found.')

        elif choice == '4':
            print('Goodbye!')
            break

        else:
            print('Invalid choice. Please try again.')

if __name__ == '__main__':
    main()