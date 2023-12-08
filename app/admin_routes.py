import json
import time
from datetime import datetime
from datetime import timedelta
from sqlalchemy.exc import IntegrityError

from flask import request, jsonify
from app import db, app
from app.models import Users, Task, UserTask, Taskmode, Activity, Subactivity, Managers
from sqlalchemy import func
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import func, text


# 3 Admin Home Page task Data

@app.route('/check_manager_mobile_number', methods=['GET'])
def check_manager_mobile_number():
    try:
        mobileNumber = request.args.get('mobileNumber', type=int)
        user = Managers.query.filter_by(mobileNumber=mobileNumber).first()
        if user:
            response = jsonify({'code': 200, 'message': 'Mobile number  exists.', 'response': user.as_dict()})
        else:
            response = jsonify({'code': 500, 'message': 'Mobile Number Is Not Register.'})

        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/admin_task_counts', methods=['GET'])
def task_count():
    try:
        counts = db.session.query(
            func.count().label('total_rows'),
            func.sum(db.cast(UserTask.isTaskComplete, db.Integer)).label('completed_true_count')
        ).first()
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


@app.route('/get_task_to_assign', methods=['GET'])
def get_task_to_assign():
    try:

        page = request.args.get('page', type=int)
        searchKey = request.args.get('searchKey', type=str)
        tasks_per_page = 3
        offset = page * tasks_per_page
        current_date = datetime.now().date()
        if searchKey is None or searchKey.strip() == "":
            result_list = (
                db.session.query(Task)
                .order_by(Task.taskId.desc())
                .filter(Task.endDate >= current_date)
                .limit(tasks_per_page)
                .offset(offset)
                .all()
            )
        else:

            result_list = (
                db.session.query(Task)
                .filter(Task.taskName.ilike(f"%{searchKey}%"))
                .filter(Task.endDate >= current_date)
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


@app.route('/get_admin_schedule_task', methods=['GET'])
def get_admin_schedule_task():
    try:
   
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
                .limit(tasks_per_page)
                .offset(offset)
                .all()
            )

        else:

            result_list = (
                db.session.query(Task)
                .filter(Task.taskName.ilike(f"%{searchKey}%"))
                .filter(
                    Task.startDate <= current_date,
                    text(f"{Task.endDate} + INTERVAL 3 DAY >= :current_date").params(current_date=current_date)
                )
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


@app.route('/get_task_users', methods=['GET'])
def get_task_users():
    try:
       
        page = request.args.get('page', type=int)
        taskId = request.args.get('taskId', type=int)
        tasks_per_page = 3
        offset = page * tasks_per_page

        result_list = (
            db.session.query(UserTask, Users)
            .filter(UserTask.taskId == taskId)
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


@app.route('/get_user_tasks', methods=['GET'])
def get_user_tasks():
    try:
       
        page = request.args.get('page', type=int)
        print(page)
        userId = request.args.get('userId', type=int)
        print(userId)
        tasks_per_page = 3
        offset = page * tasks_per_page

        result_list = (
            db.session.query(UserTask, Task)
            .join(Task, Task.taskId == UserTask.taskId)
            .filter(UserTask.userId == userId)
            .order_by(UserTask.userTaskId.desc())
            .limit(tasks_per_page)
            .offset(offset)
            .all()
        )
        task_list = [
            {
                'userTask': user_task.as_dict(),
                'task': task_info.as_dict()
            }
            for user_task, task_info in result_list
        ]

        listSize = len(task_list)
        if listSize == 0:
            if page == 0:
                return jsonify({'code': 404, 'message': 'No UserTask Available', 'isLastPage': True})
            else:
                return jsonify({'code': 409, 'message': 'No More UserTask Available', 'isLastPage': True})
        elif listSize < tasks_per_page:
            return jsonify(
                {'code': 200, 'response': task_list, 'message': 'UserTask retrieved successfully', 'isLastPage': True})
        elif listSize == tasks_per_page:
            return jsonify(
                {'code': 200, 'response': task_list, 'message': 'UserTask retrieved successfully', 'isLastPage': False})
        return jsonify(
            {'code': 200, 'response': task_list, 'message': 'UserTask retrieved successfully'})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/get_all_user', methods=['GET'])
def get_admin_user_list():
    try:
    
        page = request.args.get('page', type=int)
        searchKey = request.args.get('searchKey', type=str)
        tasks_per_page = 3
        offset = page * tasks_per_page
        if searchKey is None or searchKey.strip() == "":
            # If search key is empty, retrieve all users without filtering
            users = Users.query.order_by(Users.id.desc()).limit(tasks_per_page).offset(offset).all()
        else:

            names = searchKey.split()

            if len(names) == 1:
                # If only one name is provided, search for it in both first and last names
                users = Users.query.filter(
                    (Users.firstName.ilike(f"%{names[0]}%")) | (Users.lastName.ilike(f"%{names[0]}%"))
                ).order_by(Users.id.desc()).limit(tasks_per_page).offset(offset).all()
            elif len(names) == 2:
                # If two names are provided, assume the first is the first name and the second is the last name
                users = Users.query.filter(
                    (Users.firstName.ilike(f"%{names[0]}%")) & (Users.lastName.ilike(f"%{names[1]}%"))
                ).order_by(Users.id.desc()).limit(tasks_per_page).offset(offset).all()
            else:
                users = Users.query.filter(
                    (Users.firstName.ilike(f"%{names[0]}%")) | (Users.lastName.ilike(f"%{names[0]}%"))
                ).order_by(Users.id.desc()).limit(tasks_per_page).offset(offset).all()

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


@app.route('/activities', methods=['GET'])
def get_activities():
    try:
    
        activities = Activity.query.all()
        subActivities = Subactivity.query.all()
        taskMode = Taskmode.query.all()
        activities_list = [activity.as_dict() for activity in activities]
        subActivities_list = [subactivity.as_dict() for subactivity in subActivities]
        taskMode_list = [taskMode.as_dict() for taskMode in taskMode]
        response_data = {
            'code': 200,
            'response': {
                'activities': activities_list,
                'subActivities': subActivities_list,
                'taskModes': taskMode_list
            },
            'message': 'Data retrieved successfully',
            'isLastPage': False
        }
        return jsonify(response_data)
    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/create_task', methods=['POST'])
def create_task():
    try:
        raw_data = request.get_data()
        data_str = raw_data.decode('utf-8')
        data = json.loads(data_str)
        new_task = Task(
            taskName=data['taskName'],
            activityId=data['activityId'],
            subActivityId=data['subActivityId'],
            activityName=data['activityName'],
            subActivityName=data['subActivityName'],
            modeName=data['modeName'],
            modeId=data['modeId'],
            startDate=data['startDate'],
            endDate=data['endDate'],
            user_alloted=data['user_alloted'],
            user_completed_task=data['user_completed_task'],
            createdBy=data['createdBy']  # admin or role id by whose task is created
        )
        print(new_task)
        db.session.add(new_task)
        db.session.commit()

        return jsonify({'code': 200, 'message': 'Task created successfully'})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 409, 'message': "Failed to create a new Task"})


@app.route('/create_user', methods=['POST'])
def create_user():
    try:
        raw_data = request.get_data()
        data_str = raw_data.decode('utf-8')
        data = json.loads(data_str)

        new_user = Users(
            firstName=data['firstName'],
            lastName=data['lastName'],
            mobileNumber=data['mobileNumber'],
            emailId=data['emailId'],
            workStation=data['workStation'],
            post=data['post'],
            employeeId=data['employeeId'],
            reportAuthority=data['reportAuthority'],
            joiningDate=data['joiningDate'],
            profilePhoto=data['profilePhoto'],
        )
        db.session.add(new_user)
        db.session.commit()
        print(new_user)
        return jsonify({'code': 200, 'message': 'User created successfully', 'response': new_user.as_dict()})

    except IntegrityError as e:
        db.session.rollback()
        print(str(e))
        error_message = str(e)
        if 'for key \'mobileNumber\'' in error_message:
            return jsonify(
                {'code': 409, 'message': 'Mobile number already exists. Please use a different mobile number.'})
        elif 'for key \'emailId\'' in error_message:
            return jsonify(
                {'code': 409, 'message': 'Email already exists. Please use a different email address.'})
        elif 'for key \'employeeId\'' in error_message:
            return jsonify(
                {'code': 409, 'message': 'Employee ID already exists. Please use a different employee ID.'})
        else:
            return jsonify({'code': 409, 'message': str(e)})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 409, 'message': "Failed to create a new User"})


@app.route('/get_all_authority', methods=['GET'])
def get_all_authority():
    try:
   

        authority = Managers.query.all()
        authority_list = [authority.as_dict() for authority in authority]
        return jsonify(
            {'code': 200, 'response': authority_list, 'message': 'User retrieved successfully', 'isLastPage': True})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})
