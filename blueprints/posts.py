from flask import Blueprint, jsonify, g


bp = Blueprint('posts', __name__, url_prefix='/posts')


# @bp.route("/collect_question/<int:pid>")
# def collect(pid):
#     # 判断是否收藏
#     if g.user.is_collected(pid):
#         # 取消收藏
#         g.user.del_collection(pid)
#     else:
#         # 添加收藏
#         g.user.add_collection(pid)
#     # 将字典转为JSON字符串
#     return jsonify({'result': 'ok'})
