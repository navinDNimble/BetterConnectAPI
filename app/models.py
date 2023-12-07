from app import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column()  # Assuming a maximum length of 50 characters for first name
    lastName = db.Column()  # Assuming a maximum length of 50 characters for last name
    mobileNumber = db.Column()  # Assuming a maximum length of 10 for mobile number
    emailId = db.Column()  # Assuming a maximum length of 255 for email ID
    workStation = db.Column()  # Assuming a maximum length of 50 characters for work station
    post = db.Column()  # Assuming a maximum length of 50 characters for post
    employeeId = db.Column()  # Assuming a maximum length of 20 for employee ID
    reportAuthority = db.Column()  # Assuming a maximum length of 50 characters for report authority
    joiningDate = db.Column()  # Assuming a Date type for joining date
    profilePhoto = db.Column()  # Assuming a

    def as_dict(self):
        return {
            'userId': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'mobileNumber': self.mobileNumber,
            'emailId': self.emailId,
            'workStation': self.workStation,
            'post': self.post,
            'employeeId': self.employeeId,
            'reportAuthority': self.reportAuthority,
            'joiningDate': str(self.joiningDate) if self.joiningDate else None,
            'profilePhoto': self.profilePhoto,
        }


class Task(db.Model):
    taskId = db.Column(db.Integer, primary_key=True)
    taskName = db.Column()
    activityId = db.Column()
    subActivityId = db.Column()
    activityName = db.Column()
    subActivityName = db.Column()
    modeName = db.Column()
    modeId = db.Column()
    startDate = db.Column()
    endDate = db.Column()
    user_alloted = db.Column()
    user_completed_task = db.Column()
    createdBy = db.Column()

    def as_dict(self):
        return {
            'taskId': self.taskId,
            'taskName': self.taskName,
            'activityId': self.activityId,
            'subActivityId': self.subActivityId,
            'activityName': self.activityName,
            'subActivityName': self.subActivityName,
            'modeName': self.modeName,
            'modeId': self.modeId,
            'startDate': str(self.startDate),
            'endDate': str(self.endDate),
            'user_alloted': self.user_alloted,
            'user_completed_task': self.user_completed_task,
            'createdBy': self.createdBy
        }


class UserTask(db.Model):
    userTaskId = db.Column(db.Integer, primary_key=True)
    userId = db.Column()
    taskId = db.Column()
    totalUnits = db.Column()
    completedUnit = db.Column()
    isTaskComplete = db.Column()

    def as_dict(self):
        return {
            'userTaskId': self.userTaskId,
            'userId': self.userId,
            'taskId': self.taskId,
            'totalUnits': self.totalUnits,
            'completedUnit': self.completedUnit,
            'isTaskComplete': self.isTaskComplete
        }


class TaskUpdates(db.Model):
    taskUpdateId = db.Column(db.Integer, primary_key=True)
    userTaskId = db.Column()
    taskId = db.Column()
    userId = db.Column()
    male_count = db.Column()
    female_count = db.Column()
    lg_code = db.Column()
    wells_count = db.Column()
    survey_count = db.Column()
    village_count = db.Column()
    no_of_farmers = db.Column()
    subject = db.Column()
    findings = db.Column()
    reason_for_visit = db.Column()
    reason = db.Column()
    meeting_with_whome = db.Column()
    name_of_farmer = db.Column()
    photo = db.Column()
    update_date = db.Column()
    photos = db.relationship('Photo', backref='task_update', lazy=True, cascade='all, delete-orphan')

    def as_dict(self):
        return {
            'taskUpdateId': self.taskUpdateId,
            'userTaskId': self.userTaskId,
            'taskId': self.taskId,
            'userId': self.userId,
            'male_count': self.male_count,
            'female_count': self.female_count,
            'lg_code': self.lg_code,
            'wells_count': self.wells_count,
            'survey_count': self.survey_count,
            'village_count': self.village_count,
            'no_of_farmers': self.no_of_farmers,
            'subject': self.subject,
            'findings': self.findings,
            'reason_for_visit': self.reason_for_visit,
            'meeting_with_whome': self.meeting_with_whome,
            'name_of_farmer': self.name_of_farmer,
            'photo': self.photo,
            'photos': [photo.as_dict() for photo in self.photos],
            'update_date': str(self.update_date) if self.update_date else None
        }


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    taskUpdateId = db.Column(db.Integer, db.ForeignKey('task_updates.taskUpdateId'), nullable=False)
    photoUrl = db.Column(db.String(255))

    def as_dict(self):
        return {
            'id': self.id,
            'taskUpdateId': self.taskUpdateId,
            'photoUrl': self.photoUrl,
        }

class Activity(db.Model):
    activityId = db.Column(db.Integer, primary_key=True)
    activityName = db.Column(db.String(255), nullable=False)

    def as_dict(self):
        return {
            'activityId': self.activityId,
            'activityName': self.activityName,
        }


class Subactivity(db.Model):
    indexKey = db.Column(db.Integer, primary_key=True)
    subActivityId = db.Column(db.Integer)  # Assuming it's an integer, adjust as needed
    subActivityName = db.Column(db.String(255))  # Adjust the length based on your needs
    activityId = db.Column(db.Integer)

    def as_dict(self):
        return {
            'subActivityId': self.subActivityId,
            'subActivityName': self.subActivityName,
            'activityId': self.activityId}


class Taskmode(db.Model):
    taskModeId = db.Column(db.Integer, primary_key=True)
    taskModeName = db.Column()

    def as_dict(self):
        return {
            'taskModeId': self.taskModeId,
            'taskModeName': self.taskModeName}


class Managers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column()  # Assuming a maximum length of 50 characters for first name
    lastName = db.Column()  # Assuming a maximum length of 50 characters for last name
    mobileNumber = db.Column()  # Assuming a maximum length of 10 for mobile number
    emailId = db.Column()  # Assuming a maximum length of 255 for email ID
    workStation = db.Column()  # Assuming a maximum length of 50 characters for work station
    post = db.Column()  # Assuming a maximum length of 50 characters for post
    employeeId = db.Column()  # Assuming a maximum length of 20 for employee ID
    reportAuthority = db.Column()  # Assuming a maximum length of 50 characters for report authority
    joiningDate = db.Column()  # Assuming a Date type for joining date
    profilePhoto = db.Column()  # Assuming a

    def as_dict(self):
        return {
            'userId': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'mobileNumber': self.mobileNumber,
            'emailId': self.emailId,
            'workStation': self.workStation,
            'post': self.post,
            'employeeId': self.employeeId,
            'reportAuthority': self.reportAuthority,
            'joiningDate': str(self.joiningDate) if self.joiningDate else None,
            'profilePhoto': self.profilePhoto,
        }

