from datetime import datetime

from flask import request, jsonify
from sqlalchemy import func
from app import db, app
from app.models import Users, Task, UserTask

@app.route('/manager_task_counts', methods=['GET'])
def manager_task_count():
    try:
        id = request.args.get('id', type=int)
        counts = db.session.query(
            func.count().label('total_rows'),
            func.sum(db.cast(UserTask.isTaskComplete, db.Integer)).label('completed_true_count')
        ).filter(UserTask.assignBy == id).first()

        if counts.total_rows > 0:
            completed_false_count = counts.total_rows - counts.completed_true_count
            print(str(counts.total_rows))
            print(str(counts.completed_true_count))
            print(str(completed_false_count))
            response_data = {
                'total_task': counts.total_rows,
                'completed_task': counts.completed_true_count,
                'pending_task': completed_false_count
            }
            return jsonify({'code': 200, 'message': 'Data Fetch Successfully', 'response': response_data})
        else:
            response_data = {
                'total_task': 0,
                'completed_task': 0,
                'pending_task': 0
            }
            return jsonify({'code': 200, 'message': 'Data Fetch Successfully', 'response': response_data})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 409, 'message': 'e'})

@app.route('/get_manager_schedule_task', methods=['GET'])
def get_manager_schedule_task():
    try:
   
        id = request.args.get('id', type=int)
        page = request.args.get('page', type=int)
        searchKey = request.args.get('searchKey', type=str)
        tasks_per_page = 3
        offset = page * tasks_per_page
        current_date = datetime.now().date()
        if searchKey is None or searchKey.strip() == "":
            result_list = (
                db.session.query(Task)
                .order_by(Task.taskId.desc())
                # .filter(
                #     Task.startDate <= current_date,
                #     text(f"{Task.endDate} + INTERVAL 3 DAY >= :current_date").params(current_date=current_date)
                # )
                .filter(Task.createdBy == id)
                .limit(tasks_per_page)
                .offset(offset)
                .all()
            )

        else:
            result_list = (
                db.session.query(Task)
                .filter(Task.taskName.ilike(f"%{searchKey}%"))
                # .filter(
                #     Task.startDate <= current_date,
                #     text(f"{Task.endDate} + INTERVAL 3 DAY >= :current_date").params(current_date=current_date)
                # )
                .filter(Task.createdBy == id)
                .order_by(Task.taskId.desc())
                .limit(tasks_per_page)
                .offset(offset)
                .all()
            )

        task_list = [task.as_dict() for task in result_list]
        listSize = len(task_list)
        if listSize == 0:
            if page == 0:
                return jsonify({'code': 404, 'message': 'No Tasks Available', 'isLastPage': True})
            else:
                return jsonify({'code': 409, 'message': 'No More Task Available', 'isLastPage': True})
        elif listSize < tasks_per_page:
            return jsonify(
                {'code': 200, 'response': task_list, 'message': 'Tasks retrieved successfully', 'isLastPage': True})
        elif listSize == tasks_per_page:
            return jsonify(
                {'code': 200, 'response': task_list, 'message': 'Task retrieved successfully', 'isLastPage': False})
        return jsonify(
            {'code': 200, 'response': task_list, 'message': 'Task retrieved successfully'})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/get_manager_all_user', methods=['GET'])
def get_manager_all_user():
    try:
    
        id = request.args.get('id', type=int)
        page = request.args.get('page', type=int)
        searchKey = request.args.get('searchKey', type=str)
        tasks_per_page = 3
        offset = page * tasks_per_page
        if searchKey is None or searchKey.strip() == "":
            # If search key is empty, retrieve all users without filtering
            users = Users.query.order_by(Users.id.desc()).filter(Users.reportAuthority == id).limit(
                tasks_per_page).offset(offset).all()
        else:

            names = searchKey.split()

            if len(names) == 1:
                # If only one name is provided, search for it in both first and last names
                users = Users.query.filter(
                    (Users.firstName.ilike(f"%{names[0]}%")) | (Users.lastName.ilike(f"%{names[0]}%"))
                ).filter(Users.reportAuthority == id).order_by(Users.id.desc()).limit(tasks_per_page).offset(
                    offset).all()
            elif len(names) == 2:
                # If two names are provided, assume the first is the first name and the second is the last name
                users = Users.query.filter(
                    (Users.firstName.ilike(f"%{names[0]}%")) & (Users.lastName.ilike(f"%{names[1]}%"))
                ).filter(Users.reportAuthority == id).order_by(Users.id.desc()).limit(tasks_per_page).offset(
                    offset).all()
            else:
                users = Users.query.filter(
                    (Users.firstName.ilike(f"%{names[0]}%")) | (Users.lastName.ilike(f"%{names[0]}%"))
                ).filter(Users.reportAuthority == id).order_by(Users.id.desc()).limit(tasks_per_page).offset(
                    offset).all()

        user_list = [users.as_dict() for users in users]
        listSize = len(user_list)
        if listSize == 0:
            if page == 0:
                return jsonify({'code': 404, 'message': 'No User Available', 'isLastPage': True})
            else:
                return jsonify({'code': 409, 'message': 'No More User Available', 'isLastPage': True})
        elif listSize < tasks_per_page:
            return jsonify(
                {'code': 200, 'response': user_list, 'message': 'User retrieved successfully', 'isLastPage': True})
        elif listSize == tasks_per_page:
            return jsonify(
                {'code': 200, 'response': user_list, 'message': 'User retrieved successfully', 'isLastPage': False})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/get_manager_task_users', methods=['GET'])
def get_manager_task_users():
    try:
        id = request.args.get('id', type=int)
        page = request.args.get('page', type=int)
        taskId = request.args.get('taskId', type=int)
        tasks_per_page = 3
        offset = page * tasks_per_page

        result_list = (
            db.session.query(UserTask, Users)
            .filter(UserTask.taskId == taskId, Users.reportAuthority == id)
            .join(Users, Users.id == UserTask.userId)
            .order_by(UserTask.userTaskId.desc())
            .limit(tasks_per_page)
            .offset(offset)
            .all()
        )
        user_list = [
            {
                'userTask': user_task.as_dict(),
                'user': user_info.as_dict()
            }
            for user_task, user_info in result_list
        ]

        listSize = len(user_list)
        if listSize == 0:
            if page == 0:
                return jsonify({'code': 404, 'message': 'No UserTask Available', 'isLastPage': True})
            else:
                return jsonify({'code': 409, 'message': 'No More UserTask Available', 'isLastPage': True})
        elif listSize < tasks_per_page:
            return jsonify(
                {'code': 200, 'response': user_list, 'message': 'UserTask retrieved successfully', 'isLastPage': True})
        elif listSize == tasks_per_page:
            return jsonify(
                {'code': 200, 'response': user_list, 'message': 'UserTask retrieved successfully', 'isLastPage': False})
        return jsonify(
            {'code': 200, 'response': user_list, 'message': 'UserTask retrieved successfully'})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})

@app.route('/get_manager_task_to_assign', methods=['GET'])
def get_manager_task_to_assign():
    try:
        id = request.args.get('id', type=int)
        page = request.args.get('page', type=int)
        searchKey = request.args.get('searchKey', type=str)
        tasks_per_page = 3
        offset = page * tasks_per_page
        current_date = datetime.now().date()
        if searchKey is None or searchKey.strip() == "":
            result_list = (
                db.session.query(Task)
                .order_by(Task.taskId.desc())
                .filter(Task.endDate >= current_date ,Task.createdBy == id)
                .limit(tasks_per_page)
                .offset(offset)
                .all()
            )
        else:

            result_list = (
                db.session.query(Task)
                .filter(Task.taskName.ilike(f"%{searchKey}%"))
                .filter(Task.endDate >= current_date ,Task.createdBy == id)
                .order_by(Task.taskId.desc())
                .limit(tasks_per_page)
                .offset(offset)
                .all()
            )

        task_list = [task.as_dict() for task in result_list]
        listSize = len(task_list)
        if listSize == 0:
            if page == 0:
                return jsonify({'code': 404, 'message': 'No Tasks Available', 'isLastPage': True})
            else:
                return jsonify({'code': 409, 'message': 'No More Task Available', 'isLastPage': True})
        elif listSize < tasks_per_page:
            return jsonify(
                {'code': 200, 'response': task_list, 'message': 'Tasks retrieved successfully', 'isLastPage': True})
        elif listSize == tasks_per_page:
            return jsonify(
                {'code': 200, 'response': task_list, 'message': 'Task retrieved successfully', 'isLastPage': False})
        return jsonify(
            {'code': 200, 'response': task_list, 'message': 'Task retrieved successfully'})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})