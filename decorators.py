from flask import g, redirect, url_for, flash
from functools import wraps


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if hasattr(g, 'user'):
            return func(*args, **kwargs)
        else:
            flash("请先登录!")
            return redirect(url_for("user.login"))

    return wrapper