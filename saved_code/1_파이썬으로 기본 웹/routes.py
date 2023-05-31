```python
from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Post
from forms import PostForm

bp_home = Blueprint("home", __name__, url_prefix='/')
bp_post = Blueprint("post", __name__, url_prefix='/post')

# 게시판 목록
@bp_home.route('/')
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)

# 게시글 작성
@bp_post.route('/create', methods=["GET", "POST"])
def create():
    form = PostForm()
    if request.method == "POST" and form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        post = Post(title=title, content=content)
        post.save()
        return redirect(url_for("home.index"))

    return render_template("create.html", form=form)

# 게시글 상세보기
@bp_post.route('/<int:post_id>')
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("detail.html", post=post)

# 게시글 수정
@bp_post.route('/<int:post_id>/edit', methods=["GET", "POST"])
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    if request.method == "POST" and form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        post.title = title
        post.content = content
        post.update()
        flash("수정되었습니다.", "success")
        return redirect(url_for("post.detail", post_id=post_id))

    return render_template("edit.html", form=form)

# 게시글 삭제
@bp_post.route('/<int:post_id>/delete', methods=["GET", "POST"])
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        post.delete()
        flash("삭제되었습니다.", "success")
        return redirect(url_for("home.index"))

    return render_template("delete.html", post=post)
```