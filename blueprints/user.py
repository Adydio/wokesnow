from flask import Blueprint, render_template, jsonify, request, url_for, session, flash, redirect, g
from exts import mail, db
from flask_mail import Message
from models import EmailCaptchaModel, UserModel, QuestionModel, BlogModel, BlogCollectionModel, FollowModel
from datetime import datetime
import string
import random
from .forms import RegisterForm, LoginForm,changeForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from decorators import login_required
import time, os, uuid
from datetime import timedelta


bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("sign-in.html")
    else:
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            user = UserModel.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect("/")
            else:
                flash("邮箱和密码不匹配！")
                return redirect(url_for("user.login"))
        else:
            flash("邮箱或密码格式错误！")
            return redirect(url_for("user.login"))


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("register_.html")
    else:
        form = RegisterForm(request.form)
        if form.validate():
            letters = string.digits + string.ascii_letters
            email = form.email.data
            password = form.password.data
            username = form.username.data
            hash_password = generate_password_hash(password)
            nickname = ''.join(random.sample(letters, 10))
            anonymous_avatar_1 = random.randint(0, 42)
            anonymous_avatar_2 = random.randint(0, 13)
            anonymous_avatar_3 = random.randint(0, 13)
            user = UserModel(email=email, password=hash_password, username=username, nickname=nickname, anonymous_avatar_1=anonymous_avatar_1, anonymous_avatar_2=anonymous_avatar_2, anonymous_avatar_3=anonymous_avatar_3)
            db.session.add(user)
            db.session.commit()
            flash("注册成功！")
            return redirect(url_for("user.login"))
        else:
            flash("注册失败，请重试。注意名字不能含有空格，请核对验证码，并且确保邮箱用户名未被注册过。")
            return redirect(url_for("user.register"))


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('user.login'))

@bp.route("/captcha", methods=['POST', 'GET'])
def get_captcha():
    email = request.form.get("email")
    letters = string.digits
    captcha = "".join(random.sample(letters, 6))
    if email:
        message = Message(
            subject="验证码",
            recipients=[email],
            body=f"[匿名墙]您的注册验证码是：{captcha}，您正在登录匿名讨论板账号，若非本人操作，请忽略此邮件。如果你收到了两封邮件，请以第一封邮件的验证码为准。"
        )
        mail.send(message)
        captcha_model = EmailCaptchaModel.query.filter_by(email=email).first()
        if captcha_model:
            captcha_model.captcha = captcha
            captcha_model.create_time = datetime.now()
            db.session.commit()
        else:
            captcha_model = EmailCaptchaModel(email=email, captcha=captcha)
            db.session.add(captcha_model)
            db.session.commit()
        # print("captcha:", captcha)
        # code: 200，成功的、正常的请求
        return jsonify({"code": 200})
    else:
        # code：400，客户端错误
        return jsonify({"code": 400}, {"message": "请先传递邮箱！"})


@bp.route("/myBlog")
@login_required
def myBlog():
    username = session.get('username')

    user = UserModel.query.filter(UserModel.username == username).first()
    # order_by按照时间倒序
    questionList = QuestionModel.query.filter(QuestionModel.author_id == user.id).order_by(QuestionModel.create_time.desc()).limit(3).all()
    blogList = BlogModel.query.filter(BlogModel.author_id == user.id).order_by(BlogModel.create_time.desc()).all()
    collected = BlogCollectionModel.query.filter(BlogCollectionModel.user == user.id).order_by(BlogCollectionModel.create_time.desc()).all()
    collected_blog = []
    for collection in collected:
        collect = None
        if collection is not None:
            collect = BlogModel.query.filter(collection.blog == BlogModel.id)
        collected_blog.append(collect[0])
    followList1 = FollowModel.query.filter(FollowModel.follower_id == user.id).order_by(FollowModel.create_time.desc()).all()
    followedList = []
    for follow1 in followList1:
        followed = UserModel.query.filter(UserModel.id == follow1.followed_id)
        followedList.append(followed[0])
    followList2 = FollowModel.query.filter(FollowModel.followed_id == user.id).order_by(FollowModel.create_time.desc()).all()
    followerList = []
    for follow2 in followList2:
        follower = UserModel.query.filter(UserModel.id == follow2.follower_id)
        followerList.append(follower[0])
    hot_blogs = BlogModel.query.order_by(BlogModel.comments.desc()).limit(5)
    return render_template("myBlog.html", blogList=blogList, user=user, questionList=questionList, collected_blog=collected_blog
                           , followedList=followedList, followerList=followerList, hot_blogs=hot_blogs)

# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# 设置静态文件缓存过期时间
bp.send_file_max_age_default = timedelta(seconds=20)


@bp.route('/change_idiom', methods=['POST', 'GET'])
@login_required
def change_idiom():
    username = session.get('username')
    user = UserModel.query.filter(UserModel.username == username).first()
    form = changeForm(request.form)
    user.idiom = form.idiom.data
    db.session.commit()
    return redirect(url_for("user.myBlog"))\



# 上传照片
@bp.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        # 通过file标签获取文件
        f = request.files['file']
        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "图片类型：png、PNG、jpg、JPG、bmp"})
        # 当前文件所在路径
        basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 一定要先创建该文件夹，不然会提示没有该路径
        upload_path = os.path.join(basepath, '/static/uploadImg', secure_filename(f.filename))
        # 保存文件
        filename = 'user'+str(g.user.id) + '.' + f.filename.rsplit('.', 1)[1]
        file_path = os.path.join(basepath, 'static', 'uploadImg', filename)
        f.save(file_path)
        print(filename)
        g.user.gravatar = '../static/uploadImg/' + filename
        db.session.commit()
        # 返回上传成功界面
        return redirect(url_for("user.myBlog"))


# md编辑器上传图片
@bp.route('/imgUpload', methods=['POST'])
@login_required
def imgUpload():
    try:
        file = request.files.get('editormd-image-file');
        fname = secure_filename(file.filename);
        ext = fname.rsplit('.')[-1];
        # 生成一个uuid作为文件名
        fileName = str(uuid.uuid4()) + "." + ext;
        filePath = os.path.join("static/uploadImg/", fileName);
        file.save(filePath)
        return {
            'success': 1,
            'message': '上传成功!',
            'url': "/" + filePath
        }
    except Exception:
        return {
            'success': 0,
            'message': '上传失败'
        }


# 写博客页面
@bp.route('/writeBlog', methods=['POST', 'GET'])
@login_required
def writeblog():
    if request.method == 'GET':
        hot_blogs = BlogModel.query.order_by(BlogModel.comments.desc()).limit(5)
        return render_template('writeBlog.html', hot_blogs=hot_blogs)
    if request.method == 'POST':
        title = request.form.get("title")
        text = request.form.get("text")
        username = session.get('username')
        create_time = time.strftime("%Y-%m-%d %H:%M:%S")
        user = UserModel.query.filter(UserModel.username == username).first()
        blog = BlogModel(title=title, content=text, create_time=create_time, author_id=user.id)
        db.session.add(blog)
        db.session.commit()
        blog = BlogModel.query.filter(BlogModel.create_time == create_time).first()
        hot_blogs = BlogModel.query.order_by(BlogModel.comments.desc()).limit(5)
        return render_template('blogSuccess.html', title=title, id=blog.id, user=user, hot_blogs=hot_blogs)


@bp.route('/follow')
@login_required
def follow():
    author_id_ = request.args.get('bid')
    tag = request.args.get('id')
    username = session.get('username')
    user = UserModel.query.filter(UserModel.username == username).first()
    author_ = UserModel.query.get(author_id_)
    author_follow_ = FollowModel.query.filter(FollowModel.follower_id == user.id, FollowModel.followed_id == author_.id).first()
    if tag == '1' and author_follow_:
        author_.followed -= 1
        user.follow -= 1
        db.session.delete(author_follow_)
        db.session.commit()
        return jsonify(num="未关注")
    elif tag == '0' and (author_follow_ is None):
        author_.followed += 1
        user.follow += 1
        new_follows = FollowModel(follower_id=user.id, followed_id=author_.id)
        db.session.add(new_follows)
        db.session.commit()
        return jsonify(num="已关注")
