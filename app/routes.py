import json
from sqlalchemy.exc import IntegrityError

from flask import request, jsonify
from app import db, app
from app.models import Users, Task, UserTask
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
            # TODO:KEEP THE TOTAL UNITS VALUE SAME IF PASSED TOTAL UNITS LESS THAN COMPLETED UNits
            stmt = insert(UserTask).values(userId=user_id, taskId=task_id, totalUnits=passed_total_units)
            # stmt = stmt.on_duplicate_key_update(totalUnits=passed_total_units)
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





# 2   CREATE Task



# 1 create User Admin

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
            joiningDate=data['joiningDate']
        )
        db.session.add(new_user)
        db.session.commit()
        print(new_user)
        return jsonify({'code': 200, 'message': 'User created successfully' , 'response': new_user.as_dict()})

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

# @app.route('/api/users', methods=['GET'])
# def get_users():
#     try:
#         users_list = Users.query.all()
#         data = [user.as_dict() for user in users_list]
#         return jsonify({'code': True, 'data': data})
#     except Exception as e:
#         return jsonify({'code': False, 'message': str(e)})
