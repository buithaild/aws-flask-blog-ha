from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for
from sqlalchemy import text
from . import db
from .models import Post
from .instance_info import get_instance_info

blog = Blueprint("blog", __name__)


@blog.app_context_processor
def inject_instance():
    return {"instance": get_instance_info()}


@blog.get("/")
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("index.html", posts=posts)


@blog.get("/posts/new")
def new_post():
    return render_template("create_post.html")


@blog.post("/posts")
def create_post():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if not title or not content or len(title) > 200:
        return "Title (max 200 characters) and content are required", 400
    post = Post(title=title, content=content)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for("blog.post_detail", post_id=post.id))


@blog.get("/posts/<int:post_id>")
def post_detail(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    return render_template("post_detail.html", post=post)


@blog.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(status="healthy"), 200
    except Exception:
        return jsonify(status="unhealthy"), 503


@blog.get("/instance-info")
def instance_info():
    return jsonify(get_instance_info())
