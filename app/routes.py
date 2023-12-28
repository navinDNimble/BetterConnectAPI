from flask import request, jsonify

from flask import request, jsonify
import json
from sqlalchemy import func, case, or_
from datetime import datetime, timedelta
from app import db, app
from app.models import Users, Task, Photo, RelWorkstation, Managers, UserTask, Activity, Subactivity, Taskmode, \
    TaskUpdates, Workstations
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.mysql import insert


@app.route('/check_manager_mobile_number', methods=['GET'])
def check_manager_mobile_number():
    try:
        mobileNumber = request.args.get('mobileNumber', type=int)
        user = Managers.query.filter_by(mobileNumber=mobileNumber).first()
        if user:
            response = jsonify({'code': 200, 'message': 'Mobile number  exists.', 'response': user.as_dict()})
        else:
            response = jsonify({'code': 500, 'message': 'Mobile Number Is Not Register.'})

        print(response.get_data(as_text=True))
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/manager_task_counts', methods=['GET'])
def task_count():
    try:
        workStation = request.args.get('workStation', type=int)
        query = (
            db.session.query(
                func.count().label('total_rows'),
                func.sum(UserTask.isTaskComplete).label('completed_true_count')
            )
            .join(RelWorkstation, UserTask.workStation == RelWorkstation.security_workStation)
            .filter(RelWorkstation.workStation == workStation)
        )
        print("SQL Query:", query)
        counts = query.first()
        if counts.total_rows > 0:
            completed_false_count = counts.total_rows - counts.completed_true_count
            response_data = {
                'total_task': counts.total_rows,
                'completed_task': counts.completed_true_count,
                'pending_task': completed_false_count
            }
        else:
            response_data = {
                'total_task': 0,
                'completed_task': 0,
                'pending_task': 0
            }

        jsonResponse = jsonify({'code': 200, 'message': 'Data Fetch Successfully', 'response': response_data})
        return jsonResponse

    except Exception as e:
        print(str(e))
        return jsonify({'code': 409, 'message': 'e'})


@app.route('/manager_graph', methods=['GET'])
def get_manager_graph_data():
    try:
        workStation = request.args.get('workStation', type=int)
        activityId = request.args.get('activityId', type=int)
        first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        date_range = [first_day_of_month + timedelta(days=i) for i in
                      range((last_day_of_month - first_day_of_month).days + 1)]
        results = (
            db.session.query(
                func.DATE(TaskUpdates.update_date).label('date'),
                func.coalesce(
                    func.sum(
                        case(
                            (TaskUpdates.activityId == 11, TaskUpdates.survey_count)
                        )
                    ),
                    func.count().label('row_count')
                ).label('unit')
            )
            .join(RelWorkstation, TaskUpdates.workStation == RelWorkstation.security_workStation)
            .filter(RelWorkstation.workStation == workStation)
            .filter(TaskUpdates.update_date >= datetime.now() - timedelta(days=7))
            .filter(TaskUpdates.activityId == activityId)
            .group_by(func.DATE(TaskUpdates.update_date))
            .order_by(func.DATE(TaskUpdates.update_date).desc())
            .all()
        )

        date_dict = {result.date.strftime('%Y-%m-%d'): int(result.unit) for result in results}

        # Fill in missing dates with 0 values and order in descending order
        data = [{'date': date.strftime('%d'), 'unit': date_dict.get(date.strftime('%Y-%m-%d'), 0)} for date in
                sorted(date_range, reverse=False)]

        return jsonify({'code': 200, 'message': 'Data Fetched Success', 'response': data})

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/get_schedule_task', methods=['GET'])
def get_schedule_task():
    try:
        workStation = request.args.get('workStation', type=int)
        page = request.args.get('page', type=int)
        searchKey = request.args.get('searchKey', type=str)
        tasks_per_page = 10
        offset = page * tasks_per_page
        current_date = datetime.now().date()
        last_day = current_date - timedelta(days=30)
        if searchKey is None or searchKey.strip() == "":

            result_list = (
                db.session.query(Task)
                .order_by(Task.taskId.desc())
                .join(RelWorkstation, Task.workStation == RelWorkstation.security_workStation)
                .filter(RelWorkstation.workStation == workStation)
                .filter(
                    (Task.startDate >= last_day),
                    (Task.endDate + timedelta(days=3) >= current_date)
                )
                .limit(tasks_per_page)
                .offset(offset)
                .all()
            )

        else:
            result_list = (
                db.session.query(Task)
                .order_by(Task.taskId.desc())
                .join(RelWorkstation, Task.workStation == RelWorkstation.security_workStation)
                .filter(RelWorkstation.workStation == workStation)
                .filter(or_(
                    (Task.startDate >= last_day),
                    (Task.endDate + timedelta(days=3) >= current_date)
                ))
                .filter(Task.taskName.ilike(f"%{searchKey}%"))
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
            {'code': 200, 'response': task_list, 'message': 'Task retrieved successfully', 'isLastPage': False})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/get_task_users', methods=['GET'])
def get_task_users():
    try:

        page = request.args.get('page', type=int)
        taskId = request.args.get('taskId', type=int)
        tasks_per_page = 10
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
                return jsonify({'code': 404, 'message': 'No Task Users Available', 'isLastPage': True})
            else:
                return jsonify({'code': 409, 'message': 'No More Task Users', 'isLastPage': True})
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


@app.route('/get_update_task_details', methods=['GET'])
def get_update_task_details():
    try:

        userTaskId = request.args.get('userTaskId', type=int)
        taskUpdates = TaskUpdates.query.filter_by(userTaskId=userTaskId).order_by(TaskUpdates.taskUpdateId.desc())
        taskUpdateList = [taskUpdates.as_dict() for taskUpdates in taskUpdates]
        listSize = len(taskUpdateList)
        if listSize == 0:
            jsonResponse = jsonify({'code': 404, 'message': 'No Task Updates Available'})
        else:
            jsonResponse = jsonify({'code': 200, 'response': taskUpdateList, 'message': 'User retrieved successfully'})

        print(jsonResponse)
        return jsonResponse
    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/get_all_user', methods=['GET'])
def get_user_list():
    try:
        workStation = request.args.get('workStation', type=int)
        page = request.args.get('page', type=int)
        searchKey = request.args.get('searchKey', type=str)
        tasks_per_page = 10
        offset = page * tasks_per_page
        if searchKey is None or searchKey.strip() == "":
            users = (
                db.session.query(Users)
                .order_by(Users.id.desc())
                .join(RelWorkstation, Users.workStation == RelWorkstation.security_workStation)
                .filter(RelWorkstation.workStation == workStation)
                .limit(tasks_per_page)
                .offset(offset)
                .all()
            )
        else:

            names = searchKey.split()

            if len(names) == 1:
                users = (
                    db.session.query(Users)
                    .order_by(Users.id.desc())
                    .join(RelWorkstation, Users.workStation == RelWorkstation.security_workStation)
                    .filter(RelWorkstation.workStation == workStation)
                    .filter(
                        (Users.firstName.ilike(f"%{names[0]}%")) | (Users.lastName.ilike(f"%{names[0]}%"))
                    )
                    .limit(tasks_per_page)
                    .offset(offset)
                    .all()
                )
            elif len(names) == 2:
                # If two names are provided, assume the first is the first name and the second is the last name

                users = (
                    db.session.query(Users)
                    .order_by(Users.id.desc())
                    .join(RelWorkstation, Users.workStation == RelWorkstation.security_workStation)
                    .filter(RelWorkstation.workStation == workStation)
                    .filter(
                        (Users.firstName.ilike(f"%{names[0]}%")) & (Users.lastName.ilike(f"%{names[1]}%"))
                    )
                    .limit(tasks_per_page)
                    .offset(offset)
                    .all()
                )
            else:
                users = (
                    db.session.query(Users)
                    .order_by(Users.id.desc())
                    .join(RelWorkstation, Users.workStation == RelWorkstation.security_workStation)
                    .filter(RelWorkstation.workStation == workStation)
                    .filter(
                        (Users.firstName.ilike(f"%{names[0]}%")) | (Users.lastName.ilike(f"%{names[0]}%"))
                    )
                    .limit(tasks_per_page)
                    .offset(offset)
                    .all()
                )

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


@app.route('/get_users_for_assigned_task', methods=['GET'])
def get_users_for_assigned_task():
    try:
        page = request.args.get('page', type=int)
        taskId = request.args.get('taskId', type=int)
        workStation = request.args.get('workStation', type=int)
        searchKey = request.args.get('searchKey', type=str)
        tasks_per_page = 10
        offset = page * tasks_per_page
        if searchKey is None or searchKey.strip() == "":
            users = (
                db.session.query(Users)
                .order_by(Users.id.desc())
                .join(RelWorkstation, Users.workStation == RelWorkstation.security_workStation)
                .filter(RelWorkstation.workStation == workStation)
                .outerjoin(UserTask, (UserTask.userId == Users.id) & (UserTask.taskId == taskId))
                .filter(UserTask.userId.is_(None))
                .limit(tasks_per_page)
                .offset(offset)
                .all()
            )
        else:

            names = searchKey.split()
            if len(names) == 1:
                users = (
                    db.session.query(Users)
                    .order_by(Users.id.desc())
                    .join(RelWorkstation, Users.workStation == RelWorkstation.security_workStation)
                    .filter(RelWorkstation.workStation == workStation)
                    .filter(
                        (Users.firstName.ilike(f"%{names[0]}%")) | (Users.lastName.ilike(f"%{names[0]}%"))
                    )
                    .outerjoin(UserTask, (UserTask.userId == Users.id) & (UserTask.taskId == taskId))
                    .filter(UserTask.userId.is_(None))
                    .limit(tasks_per_page)
                    .offset(offset)
                    .all()
                )
            elif len(names) == 2:
                # If two names are provided, assume the first is the first name and the second is the last name

                users = (
                    db.session.query(Users)
                    .order_by(Users.id.desc())
                    .join(RelWorkstation, Users.workStation == RelWorkstation.security_workStation)
                    .filter(RelWorkstation.workStation == workStation)
                    .filter(
                        (Users.firstName.ilike(f"%{names[0]}%")) & (Users.lastName.ilike(f"%{names[1]}%"))
                    )
                    .outerjoin(UserTask, (UserTask.userId == Users.id) & (UserTask.taskId == taskId))
                    .filter(UserTask.userId.is_(None))
                    .limit(tasks_per_page)
                    .offset(offset)
                    .all()
                )
            else:
                users = (
                    db.session.query(Users)
                    .order_by(Users.id.desc())
                    .join(RelWorkstation, Users.workStation == RelWorkstation.security_workStation)
                    .filter(RelWorkstation.workStation == workStation)
                    .filter(
                        (Users.firstName.ilike(f"%{names[0]}%")) | (Users.lastName.ilike(f"%{names[0]}%"))
                    )
                    .outerjoin(UserTask, (UserTask.userId == Users.id) & (UserTask.taskId == taskId))
                    .filter(UserTask.userId.is_(None))
                    .limit(tasks_per_page)
                    .offset(offset)
                    .all()
                )

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




@app.route('/get_user_tasks', methods=['GET'])
def get_user_tasks():
    try:

        page = request.args.get('page', type=int)
        print(page)
        userId = request.args.get('userId', type=int)
        print(userId)
        tasks_per_page = 10
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


@app.route('/get_task_to_assign', methods=['GET'])
def get_task_to_assign():
    try:
        workStation = request.args.get('workStation', type=int)
        page = request.args.get('page', type=int)
        searchKey = request.args.get('searchKey', type=str)
        tasks_per_page = 20
        offset = page * tasks_per_page
        current_date = datetime.now().date()
        if searchKey is None or searchKey.strip() == "":

            result_list = (
                db.session.query(Task)
                .order_by(Task.taskId.desc())
                .join(RelWorkstation, Task.workStation == RelWorkstation.security_workStation)
                .filter(RelWorkstation.workStation == workStation)
                .filter(Task.endDate >= current_date)
                .limit(tasks_per_page)
                .offset(offset)
                .all()
            )
        else:

            result_list = (
                db.session.query(Task)
                .order_by(Task.taskId.desc())
                .join(RelWorkstation, Task.workStation == RelWorkstation.security_workStation)
                .filter(RelWorkstation.workStation == workStation)
                .filter(Task.endDate >= current_date)
                .filter(Task.taskName.ilike(f"%{searchKey}%"))
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
        print(new_user.as_dict())
        return jsonify({'code': 200, 'message': 'User created successfully', 'response': new_user.as_dict()})

    except IntegrityError as e:
        db.session.rollback()
        print(str(e))
        error_message = str(e)
        if 'for key \'users.mobileNumber\'' in error_message:
            return jsonify(
                {'code': 409, 'message': 'Mobile number already exists. Please use a different mobile number.'})
        elif 'for key \'users.emailId\'' in error_message:
            return jsonify(
                {'code': 409, 'message': 'Email already exists. Please use a different email address.'})
        elif 'for key \'users.employeeId\'' in error_message:
            return jsonify(
                {'code': 409, 'message': 'Employee ID already exists. Please use a different employee ID.'})
        else:
            return jsonify({'code': 409, 'message': str(e)})

    except Exception as e:
        print(str(e))
        db.session.rollback()
        return jsonify({'code': 409, 'message': "Failed to create a new User"})


@app.route('/get_reporting_authority', methods=['GET'])
def get_all_authority():
    try:

        authority = Managers.query.filter(Managers.post == 4).all()
        authority_list = [authority.as_dict() for authority in authority]
        return jsonify(
            {'code': 200, 'response': authority_list, 'message': 'User retrieved successfully', 'isLastPage': True})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/create_task', methods=['POST'])
def create_task():
    try:
        raw_data = request.get_data()
        data_str = raw_data.decode('utf-8')
        data = json.loads(data_str)
        workstation = Workstations.query.get(data['workStation'])
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
            workStation=data['workStation'],
            workStationName=workstation,
            user_alloted=data['user_alloted'],
            user_completed_task=data['user_completed_task'],
            createdBy=data['createdBy']  # admin or role id by whose task is created
        )
        print(new_task.as_dict())
        db.session.add(new_task)
        db.session.commit()

        return jsonify({'code': 200, 'message': 'Task created successfully', 'response': new_task.as_dict()})

    except Exception as e:
        db.session.rollback()
        print(str(e))
        return jsonify({'code': 409, 'message': "Failed to create a new Task"})


@app.route('/assign_users_to_task', methods=['POST'])
def assign_users_to_task():
    try:
        raw_data = request.get_data()
        data_str = raw_data.decode('utf-8')
        data = json.loads(data_str)
        user_assignments = data['userList']
        task_id = data['taskId']
        print(user_assignments)

        for assignment in user_assignments:
            user_id = assignment['userId']
            print(user_id)
            passed_total_units = assignment['total_units']
            workStation = assignment['workStation']
            print(passed_total_units)
            stmt = insert(UserTask).values(userId=user_id, taskId=task_id, totalUnits=passed_total_units,
                                           workStation=workStation)
            stmt = stmt.on_duplicate_key_update(totalUnits=passed_total_units,
                                                isTaskComplete=case(
                                                    (UserTask.completedUnit < passed_total_units, 0),
                                                    else_=1
                                                ))
            db.session.execute(stmt)
            db.session.commit()

        return jsonify({'code': 200, 'message': 'Users assigned to the task successfully'})

    except Exception as e:
        print(str(e))
        db.session.rollback()
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


@app.route('/get_photos_url', methods=['GET'])
def get_photo_urls():
    taskUpdateId = request.args.get('taskUpdateId', type=int)
    photos = Photo.query.filter_by(taskUpdateId=taskUpdateId).all()

    if not photos:
        return jsonify({'code': 400, 'message': 'No Photos For This Task'})

    # Return a list of photo URLs in the response
    photo_urls = [photo.photoUrl for photo in photos]
    return jsonify({'code': 200, 'message': 'Photo Fetched SuccessFully', 'response': photo_urls})

# @app.route('/get_all_task', methods=['GET'])
# def get_all_task():
#     try:
#         workStation = request.args.get('workStation', type=int)
#         page = request.args.get('page', type=int)
#         searchKey = request.args.get('searchKey', type=str)
#         tasks_per_page = 10
#         offset = page * tasks_per_page
#
#         if searchKey is None or searchKey.strip() == "":
#             tasks = (
#                 db.session.query(Task)
#                 .order_by(Task.taskId.desc())
#                 .join(RelWorkstation, Task.workStation == RelWorkstation.security_workStation)
#                 .filter(RelWorkstation.workStation == workStation)
#                 .limit(tasks_per_page)
#                 .offset(offset)
#                 .all()
#             )
#         else:
#
#             tasks = (
#                 db.session.query(Task)
#                 .order_by(Task.taskId.desc())
#                 .join(RelWorkstation, Task.workStation == RelWorkstation.security_workStation)
#                 .filter(RelWorkstation.workStation == workStation)
#                 .filter((Task.taskName.ilike(f"%{searchKey}%")))
#                 .limit(tasks_per_page)
#                 .offset(offset)
#                 .all()
#             )
#
#         task_list = [task.as_dict() for task in tasks]
#
#         listSize = len(task_list)
#         if listSize == 0:
#             if page == 0:
#                 return jsonify({'code': 409, 'message': 'No Task Available', 'isLastPage': True})
#             else:
#                 return jsonify({'code': 404, 'message': 'No More Task Available', 'isLastPage': True})
#         elif listSize < tasks_per_page:
#             return jsonify(
#                 {'code': 200, 'response': task_list, 'message': 'Tasks retrieved successfully', 'isLastPage': True})
#         elif listSize == tasks_per_page:
#             return jsonify(
#                 {'code': 200, 'response': task_list, 'message': 'Tasks retrieved successfully', 'isLastPage': False})
#
#     except Exception as e:
#         print(str(e))
#         return jsonify({'code': 500, 'message': 'Internal Server Error'})
