import json
from datetime import datetime, timedelta
from flask import request, jsonify
from sqlalchemy import func, case
from app import db, app
from app.models import Task, UserTask, TaskUpdates, Photo, Users


@app.route('/check_mobile_number', methods=['GET'])
def check_mobile_number():
    try:
        mobileNumber = request.args.get('mobileNumber', type=int)
        user = Users.query.filter_by(mobileNumber=mobileNumber).first()
        if user:
            response = jsonify({'code': 200, 'message': 'Mobile number  exists.', 'response': user.as_dict()})
        else:
            response = jsonify({'code': 500, 'message': 'Mobile Number Is Not Register.'})
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/user_task_counts', methods=['GET'])
def user_task_count():
    try:

        userId = request.args.get('userId', type=int)
        print(userId)
        counts = db.session.query(
            func.count().label('total_rows'),
            func.sum(db.cast(UserTask.isTaskComplete, db.Integer)).label('completed_true_count')
        ).filter(UserTask.userId == userId).first()
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
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/user_graph', methods=['GET'])
def get_graph_data():
    try:
        userId = request.args.get('userId', type=int)
        activityId = request.args.get('activityId', type=int)

        # Get the first day of the current month
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
            .filter(TaskUpdates.userId == userId)
            .filter(TaskUpdates.update_date >= first_day_of_month)
            .filter(TaskUpdates.activityId == activityId)
            .group_by(func.DATE(TaskUpdates.update_date))
            .order_by(func.DATE(TaskUpdates.update_date).desc())
            .all()
        )


        # Create a dictionary to store results for each date
        date_dict = {result.date.strftime('%Y-%m-%d'): int(result.unit) for result in results}




        data = [{'date': date.strftime('%d'), 'unit': date_dict.get(date.strftime('%Y-%m-%d'), 0)} for date in
                sorted(date_range, reverse=False)]
        return jsonify({'code': 200, 'message': 'Data Fetched Success', 'response': data})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


@app.route('/get_user_task_completed', methods=['GET'])
def get_completed_user_task():
    try:

        page = request.args.get('page', type=int)
        print(page)
        userId = request.args.get('userId', type=int)
        print(userId)
        tasks_per_page = 10
        offset = page * tasks_per_page
        current_date = datetime.now().date()

        result_list = (
            db.session.query(UserTask, Task)
            .join(Task, Task.taskId == UserTask.taskId)
            .filter(UserTask.userId == userId, UserTask.isTaskComplete == 1)
            # .filter(Task.startDate <= current_date, Task.endDate >= current_date)
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


@app.route('/get_user_task_pending', methods=['GET'])
def get_pending_user_task():
    try:

        page = request.args.get('page', type=int)
        print(page)
        userId = request.args.get('userId', type=int)
        print(userId)
        tasks_per_page = 10
        offset = page * tasks_per_page
        current_date = datetime.now().date()

        # Todo : date bounding
        result_list = (
            db.session.query(UserTask, Task)
            .join(Task, Task.taskId == UserTask.taskId)
            .filter(UserTask.userId == userId, UserTask.isTaskComplete == 0)
            # .filter(Task.startDate <= current_date, Task.endDate >= current_date)
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
                return jsonify({'code': 404, 'message': 'No Pending UserTask Available', 'isLastPage': True})
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


@app.route('/update_task_details', methods=['POST'])
def update_task_details():
    try:

        raw_data = request.get_data()
        data_str = raw_data.decode('utf-8')
        data = json.loads(data_str)
        task_id = data.get('taskId')
        userTaskId = data.get('userTaskId')
        activityId = data.get('activityId')
        # if data.get('photo') == 1:
        photos = [Photo(photoUrl=photo_url) for photo_url in data.get('photoList', [])]
        # else:
        #     photos = []

        new_update = TaskUpdates(
            userTaskId=data.get('userTaskId'),
            taskId=data.get('taskId'),
            userId=data.get('userId'),
            activityId=data.get('activityId'),
            male_count=data.get('male_count'),
            female_count=data.get('female_count'),
            lg_code=data.get('lg_code'),
            wells_count=data.get('wells_count'),
            survey_count=data.get('survey_count'),
            village_count=data.get('village_count'),
            no_of_farmers=data.get('no_of_farmers'),
            subject=data.get('subject'),
            findings=data.get('findings'),
            reason_for_visit=data.get('reason_for_visit'),
            reason=data.get('reason'),
            meeting_with_whome=data.get('meeting_with_whome'),
            name_of_farmer=data.get('name_of_farmer'),
            photo=data.get('photo'),
            update_date=data.get('update_date'),
            photos=photos,
            workStation=data.get('workStation'),
        )
        print(activityId)
        print(new_update)

        db.session.add(new_update)

        print(userTaskId)

        userTask = UserTask.query.filter_by(userTaskId=userTaskId).first()
        print(userTask)

        if userTask:

            if activityId == 11:
                survey_count = data.get('survey_count')
                new_completeUnit = userTask.completedUnit + survey_count
                print(new_completeUnit)
            else:
                new_completeUnit = userTask.completedUnit + 1

            # if new_completeUnit > userTask.totalUnits:
            #     db.session.rollback()
            #     return jsonify({
            #         'code': 404,
            #         'message': f'Max Unit Available to Complete Task are {userTask.totalUnits - userTask.completedUnit}'
            #     })

            userTask.completedUnit = new_completeUnit

            if new_completeUnit >= userTask.totalUnits:
                userTask.isTaskComplete = 1
                # task = Task.query.filter_by(taskId=task_id).first()
                # task.user_completed_task = +1

            db.session.commit()
            return jsonify({'code': 200, 'message': ' Task Updated  successfully', 'response': new_update.as_dict()})
        else:
            # If the task is not found, return a 404 response
            return jsonify({'code': 404, 'message': 'Task not found for the provided user'})

    except Exception as e:
        print(str(e))
        db.session.rollback()
        return jsonify({'code': 404, 'message': f"Failed to update task: {str(e)}"})
