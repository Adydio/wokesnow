from flask import Flask, render_template, session, g
import config
from decorators import login_required
from exts import db, mail
from blueprints import qa_bp, user_bp, blog_bp
from flask_migrate import Migrate
from models import UserModel, QuestionModel, BlogModel, BlogCollectionModel, FollowModel
from flask_bootstrap import Bootstrap
from flaskext.markdown import Markdown
from blueprints.qa import avatar_1_list, avatar_2_list, avatar_3_list

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
mail.init_app(app)
Markdown(app)

migrate = Migrate(app, db)
bootstrap = Bootstrap(app)

app.register_blueprint(qa_bp)
app.register_blueprint(user_bp)
app.register_blueprint(blog_bp)


@app.before_request
def before_request():
    user_id = session.get("user_id")
    if user_id:
        try:
            user = UserModel.query.get(user_id)
            g.user = user
        except:
            g.user = None


@app.context_processor
def context_processor():
    if hasattr(g, "user"):
        return {"user": g.user}
    else:
        return {}


@app.route('/hot')
def hot():
    questions = QuestionModel.query.order_by(QuestionModel.comments.desc()).all()
    recent_questions = QuestionModel.query.order_by(QuestionModel.create_time.desc()).limit(5)
    return render_template('hot.html', questions=questions, hot_questions=recent_questions, avatar_1_list=avatar_1_list, avatar_2_list=avatar_2_list, avatar_3_list=avatar_3_list)


@app.route('/docs')
def docs():
    return render_template('introduction.html')



@app.route('/aboutus')
def aboutus():
    return render_template('team.html')


@app.route('/author/<int:author_id>', methods=['POST', 'GET'])
@login_required
def author_page(author_id):
    author = UserModel.query.get(author_id)
    username = session.get('username')
    user = UserModel.query.filter(UserModel.username == username).first()
    questionList = QuestionModel.query.filter(QuestionModel.author_id == author.id).order_by(
        QuestionModel.create_time.desc()).limit(3).all()
    blogList = BlogModel.query.filter(BlogModel.author_id == author.id).order_by(BlogModel.create_time.desc()).all()
    collected = BlogCollectionModel.query.filter(BlogCollectionModel.user == author.id).order_by(
        BlogCollectionModel.create_time.desc()).all()
    collected_blog = []
    for collection in collected:
        collect = None
        if collection is not None:
            collect = BlogModel.query.filter(collection.blog == BlogModel.id)
        collected_blog.append(collect[0])
    followList1 = FollowModel.query.filter(FollowModel.follower_id == author.id).order_by(
        FollowModel.create_time.desc()).all()
    followedList = []
    for follow1 in followList1:
        followed = UserModel.query.filter(UserModel.id == follow1.followed_id)
        followedList.append(followed[0])
    followList2 = FollowModel.query.filter(FollowModel.followed_id == author.id).order_by(
        FollowModel.create_time.desc()).all()
    followerList = []
    for follow2 in followList2:
        follower = UserModel.query.filter(UserModel.id == follow2.follower_id)
        followerList.append(follower[0])
    hot_blogs = BlogModel.query.order_by(BlogModel.comments.desc()).limit(5)
    return render_template("author_page.html", blogList=blogList, user=author, questionList=questionList, collected_blog
    =collected_blog, followedList=followedList, followerList=followerList, hot_blogs=hot_blogs)


if __name__ == '__main__':
    app.run(debug=True)
