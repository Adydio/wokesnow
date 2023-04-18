from flask import Blueprint, render_template, request, jsonify, session, g, url_for, redirect
from exts import db
from models import BlogModel, UserModel, BlogLikesModel, BlogCollectionModel, CommentModel, QuestionModel
from decorators import login_required
from .forms import AnswerForm


bp = Blueprint('blog', __name__, url_prefix='/blog')


@bp.route("/", methods=['GET', 'POST'])
def blog_index():
    blogs = BlogModel.query.order_by(db.text("-create_time")).all()
    hot_blogs = BlogModel.query.order_by(BlogModel.comments.desc()).limit(5)
    return render_template("blogbase.html", blogs=blogs, hot_blogs=hot_blogs)


@bp.route("/<int:blog_id>")
def blog_detail(blog_id):
    blog = BlogModel.query.get(blog_id)
    username = session.get('username')
    user = UserModel.query.filter(UserModel.username == username).first()
    # return render_template("detail.html", question=question)
    hot_blogs = BlogModel.query.order_by(BlogModel.comments.desc()).limit(5)
    return render_template('blog_detail.html', blog=blog, user=user, hot_blogs=hot_blogs)

@bp.route('/like')
def blog_like():
    blog_id_ = request.args.get('bid')
    tag = request.args.get('id')
    username = session.get('username')
    user = UserModel.query.filter(UserModel.username == username).first()
    blog_ = BlogModel.query.get(blog_id_)
    blog_like_ = BlogLikesModel.query.filter(BlogLikesModel.user == user.id, BlogLikesModel.blog == blog_.id).first()
    if tag == '1' and blog_like_:
        blog_.likes -= 1
        db.session.delete(blog_like_)
    elif tag == '0' and (blog_like_ is None):
        blog_.likes += 1
        new_likes = BlogLikesModel(user=user.id, blog=blog_.id)
        db.session.add(new_likes)
    db.session.commit()
    return jsonify(num=blog_.likes)


@bp.route('/collect')
def blog_collection():
    blog_id = request.args.get('bid')
    tag = request.args.get('id')
    username = session.get('username')
    user = UserModel.query.filter(UserModel.username == username).first()
    blog_ = BlogModel.query.get(blog_id)
    blog_collection_ = BlogCollectionModel.query.filter(BlogCollectionModel.user == user.id, BlogCollectionModel.blog == blog_.id).first()
    if tag == '3' and blog_collection_:
        blog_.collects -= 1
        db.session.delete(blog_collection_)
    elif tag == '2' and (blog_collection_ is None):
        blog_.collects += 1
        new_collection = BlogCollectionModel(user=user.id, blog=blog_.id)
        db.session.add(new_collection)
    db.session.commit()
    return jsonify(num_=blog_.collects)


@bp.route("/comment/<int:blog_id>", methods=['POST'])
@login_required
def comment(blog_id):
    form = AnswerForm(request.form)
    if form.validate():
        blog = BlogModel.query.get(blog_id)
        content = form.content.data
        comment_model = CommentModel(content=content, author=g.user, blog_id=blog_id)
        db.session.add(comment_model)
        blog.comments += 1
        db.session.commit()
        # question = QuestionModel.query.get(question_id)
        # print(question.comments)
        # comment_ = int(question.comments) + 1
        # cursor.execute("update question set comments=%d where question_id=%d" % (comment_, question_id))
        # conn.commit()
        return redirect(url_for("blog.blog_detail", blog_id=blog_id))
    else:
        return redirect(url_for("blog.blog_detail", blog_id=blog_id))

@bp.route('/hot')
def hot():
    blogs = BlogModel.query.order_by(BlogModel.likes.desc())
    recent_blogs = BlogModel.query.order_by(BlogModel.create_time.desc()).limit(5)
    return render_template('hotblog.html', blogs=blogs, hot_blogs=recent_blogs)