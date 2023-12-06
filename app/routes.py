import json
from sqlalchemy.exc import IntegrityError

from flask import request, jsonify
from app import db, app
from app.models import Users, Task, UserTask, Photo
from sqlalchemy import func
from sqlalchemy.dialects.mysql import insert


# 10 Check Mobile Number Registered

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


# 9 assign users to tasks


# 8 assign users to tasks
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
            print(passed_total_units)

            stmt = insert(UserTask).values(userId=user_id, taskId=task_id, totalUnits=passed_total_units)
            stmt = stmt.on_duplicate_key_update(totalUnits=UserTask.totalUnits)
            db.session.execute(stmt)
            db.session.commit()

        return jsonify({'code': 200, 'message': 'Users assigned to the task successfully'})

    except Exception as e:
        print(str(e))
        return jsonify({'code': 500, 'message': 'Internal Server Error'})


# 4   return the task list for admin
@app.route('/get_admin_task', methods=['GET'])
def get_admin_task():
    try:
        page = request.args.get('page', type=int)
        searchKey = request.args.get('searchKey', type=str)
        tasks_per_page = 3
        offset = page * tasks_per_page

        if searchKey is None or searchKey.strip() == "":
            tasks = Task.query.order_by(Task.taskId.desc()).limit(tasks_per_page).offset(offset).all()
        else:

            tasks = Task.query.filter(
                (Task.taskName.ilike(f"%{searchKey}%"))).order_by(Task.taskId.desc()).limit(tasks_per_page).offset(
                offset).all()

        task_list = [task.as_dict() for task in tasks]

        listSize = len(task_list)
        if listSize == 0:
            if page == 0:
                return jsonify({'code': 409, 'message': 'No Task Available', 'isLastPage': True})
            else:
                return jsonify({'code': 404, 'message': 'No More Task Available', 'isLastPage': True})
        elif listSize < tasks_per_page:
            return jsonify(
                {'code': 200, 'response': task_list, 'message': 'Tasks retrieved successfully', 'isLastPage': True})
        elif listSize == tasks_per_page:
            return jsonify(
                {'code': 200, 'response': task_list, 'message': 'Tasks retrieved successfully', 'isLastPage': False})

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
