import json
import time
from datetime import datetime
from datetime import timedelta
from sqlalchemy.exc import IntegrityError

from flask import request, jsonify
from app import db, app
from app.models import Users, Task, UserTask, Taskmode, Activity, Subactivity, Managers, Workstations
from sqlalchemy import func
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import func, text


# 3 Admin Home Page task Data







# @app.route('/get_admin_schedule_task', methods=['GET'])
# def get_admin_schedule_task():
#     try:
#
#         page = request.args.get('page', type=int)
#         searchKey = request.args.get('searchKey', type=str)
#         tasks_per_page = 3
#         offset = page * tasks_per_page
#         current_date = datetime.now().date()
#         if searchKey is None or searchKey.strip() == "":
#             result_list = (
#                 db.session.query(Task)
#                 .order_by(Task.taskId.desc())
#                 .filter(
#                     Task.startDate <= current_date,
#                     text(f"{Task.endDate} + INTERVAL 3 DAY >= :current_date").params(current_date=current_date)
#                 )
#                 .limit(tasks_per_page)
#                 .offset(offset)
#                 .all()
#             )
#
#         else:
#
#             result_list = (
#                 db.session.query(Task)
#                 .filter(Task.taskName.ilike(f"%{searchKey}%"))
#                 .filter(
#                     Task.startDate <= current_date,
#                     text(f"{Task.endDate} + INTERVAL 3 DAY >= :current_date").params(current_date=current_date)
#                 )
#                 .order_by(Task.taskId.desc())
#                 .limit(tasks_per_page)
#                 .offset(offset)
#                 .all()
#             )
#
#         task_list = [task.as_dict() for task in result_list]
#         listSize = len(task_list)
#         if listSize == 0:
#             if page == 0:
#                 return jsonify({'code': 404, 'message': 'No Tasks Available', 'isLastPage': True})
#             else:
#                 return jsonify({'code': 409, 'message': 'No More Task Available', 'isLastPage': True})
#         elif listSize < tasks_per_page:
#             return jsonify(
#                 {'code': 200, 'response': task_list, 'message': 'Tasks retrieved successfully', 'isLastPage': True})
#         elif listSize == tasks_per_page:
#             return jsonify(
#                 {'code': 200, 'response': task_list, 'message': 'Task retrieved successfully', 'isLastPage': False})
#         return jsonify(
#             {'code': 200, 'response': task_list, 'message': 'Task retrieved successfully'})
#
#     except Exception as e:
#         print(str(e))
#         return jsonify({'code': 500, 'message': 'Internal Server Error'})


