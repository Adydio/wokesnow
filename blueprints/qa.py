from flask import Blueprint, render_template, request, g, redirect, url_for, flash, jsonify, session
from decorators import login_required
from .forms import QuestionForm, AnswerForm
from models import QuestionModel, AnswerModel, UserModel
from exts import db
from sqlalchemy import or_

bp = Blueprint('qa', __name__, url_prefix='/')

avatar_1_list = ['cat', 'cow', 'crow', 'dog', 'dove', 'dragon', 'fish', 'fish-fins', 'frog', 'hippo', 'horse',
                 'horse-head',
                 'kiwi-bird', 'locust', 'otter', 'shield-cat', 'shield-dog', 'bed', 'cookie-bite', 'gamepad', 'robot',
                 'snowman',
                 'face-angry', 'face-dizzy', 'face-flushed', 'face-frown', 'face-grin-beam', 'face-grin-beam-sweat',
                 'face-grin-hearts',
                 'face-grin-squint-tears', 'face-grin-stars', 'face-grin-tongue-wink', 'face-kiss', 'face-kiss-beam',
                 'fane-kiss-wink-heart',
                 'face-laugh-squint', 'face-laugh-wink', 'face-meh', 'face-meh-blank', 'face-rolling-eyes',
                 'face-sad-cry', 'face-sad-tear',
                 'face-tired']
avatar_2_list = ['000000', 'FFFF00', 'B0E0E6', 'FFFFFF', '4169E1', '00FF00', '802A2A', 'FAFFF0', 'F0E68C', '308014',
                 'FF0000', 'FFC0CB', '0000FF', 'A020F0']
avatar_3_list = ['000000', 'FFFF00', 'B0E0E6', 'FFFFFF', '4169E1', '00FF00', '802A2A', 'FAFFF0', 'F0E68C', '308014',
                 'FF0000', 'FFC0CB', '0000FF', 'A020F0']

@bp.route("/")
def index():
    questions = QuestionModel.query.order_by(db.text("-create_time")).all()
    hot_questions = QuestionModel.query.order_by(QuestionModel.comments.desc()).limit(5)
    return render_template("bbs.html", questions=questions, hot_questions=hot_questions, avatar_1_list=avatar_1_list, avatar_2_list=avatar_2_list, avatar_3_list=avatar_3_list)


@bp.route("/question/publish", methods=['GET', 'POST'])
@login_required
def publish_question():
    # 判断是否登录，如果没有登录，跳转到登录页面
    if request.method == 'GET':
        hot_questions = QuestionModel.query.order_by(QuestionModel.comments.desc()).limit(5)
        return render_template("publish_question.html", hot_questions=hot_questions)
    else:
        form = QuestionForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            question = QuestionModel(title=title, content=content, author=g.user)
            db.session.add(question)
            db.session.commit()
            flash("已发布一条匿名帖！")
            return redirect("/")
        else:
            hot_questions = QuestionModel.query.order_by(QuestionModel.comments.desc()).limit(5)
            flash("标题或内容格式错误！")
            return redirect(url_for("qa.publish_question", hot_questions=hot_questions))


@bp.route("/question/<int:question_id>")
def question_detail(question_id):
    hot_questions = QuestionModel.query.order_by(QuestionModel.comments.desc()).limit(5)
    question = QuestionModel.query.get(question_id)
    return render_template('detail.html', question=question, hot_questions=hot_questions, avatar_1_list=avatar_1_list, avatar_2_list=avatar_2_list, avatar_3_list=avatar_3_list)


@bp.route("/answer/<int:question_id>", methods=['POST'])
@login_required
def answer(question_id):
    form = AnswerForm(request.form)
    if form.validate():
        hot_questions = QuestionModel.query.order_by(QuestionModel.comments.desc()).limit(5)
        question = QuestionModel.query.get(question_id)
        content = form.content.data
        answer_model = AnswerModel(content=content, author=g.user, question_id=question_id)
        db.session.add(answer_model)
        question.comments += 1
        db.session.commit()
        return redirect(url_for("qa.question_detail", question_id=question_id, hot_questions=hot_questions))
    else:
        hot_questions = QuestionModel.query.order_by(QuestionModel.comments.desc()).limit(5)
        # flash("表单验证失败！")
        return redirect(url_for("qa.question_detail", question_id=question_id, hot_questions=hot_questions))


@bp.route("/search")
def search():
    # /search?q=xxx
    q = request.args.get("q")
    # filter_by：直接使用字段的名称
    # filter：使用模型.字段名称
    questions = QuestionModel.query.filter(
        or_(QuestionModel.title.contains(q), QuestionModel.content.contains(q))).order_by(db.text("-create_time"))
    return render_template("homepage.html", questions=questions)


@bp.route("reply/<int:answer_id>", methods=['GET', 'POST'])
@login_required
def reply(answer_id):
    if request.method == 'GET':
        answer_ = AnswerModel.query.get(answer_id)
        return render_template("reply.html", answer_id=answer_id, answer=answer_)
    else:
        form = AnswerForm(request.form)
        answer_ = AnswerModel.query.get(answer_id)
        question = QuestionModel.query.filter(QuestionModel.id == answer_.question_id).first()
        if form.validate():
            content = form.content.data
            reply_ = AnswerModel(question_id=question.id, content=content, author_id=g.user.id, reply_id=answer_id)
            db.session.add(reply_)
            db.session.commit()
            flash("回复成功！")
            return redirect(url_for("qa.question_detail", question_id=question.id))
        else:
            flash("内容格式错误！请至少输入1个字符。")
            # return redirect(url_for("qa.reply", answer_id=answer_id, answer=answer_))
            return render_template("reply.html", answer_id=answer_id, answer=answer_)



# @bp.route('/like')
# def answer_like():
#     answer_id_ = request.args.get('bid')
#     tag = request.args.get('id')
#     username = session.get('username')
#     user = UserModel.query.filter(UserModel.username == username)
#     answer_ = AnswerModel.query.get(answer_id_)
#     answer_like_ = CommentLikeModel.query.filter(CommentLikeModel.user == user.id, CommentLikeModel.answer == answer_.id).first()
#     if tag == '1' and answer_like_:
#         answer_.likes -= 1
#         db.session.delete(answer_like_)
#     elif tag == '0' and (answer_like_ is None):
#         answer_.likes += 1
#         new_likes = CommentLikeModel(user=user.id, answer=answer_.id)
#         db.session.add(new_likes)
#     db.session.commit()
#     return jsonify(numb=answer_.likes)
