from sqlalchemy.orm import relationship, class_mapper

from app import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    mobileNumber = db.Column(unique=True, nullable=False)
    emailId = db.Column(db.String(255), unique=True, nullable=False)
    workStation = db.Column(db.Integer, db.ForeignKey('workstations.id'))
    workStationName = db.relationship('Workstations', backref=db.backref('users', lazy=True))
    post = db.Column()
    employeeId = db.Column(db.String(255), unique=True, nullable=False)
    reportAuthority = db.Column()
    joiningDate = db.Column(db.Date)  # Assuming joiningDate is a date column
    profilePhoto = db.Column(db.String(255))  # Assuming profilePhoto is a file path or URL

    def as_dict(self):
        return {
            'userId': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'mobileNumber': self.mobileNumber,
            'emailId': self.emailId,
             'workStation': self.workStation,  # Assuming 'id' is the primary key
            'workStationName': self.workStationName.workStationName if self.workStationName else None,
            'post': self.post,
            'employeeId': self.employeeId,
            'reportAuthority': self.reportAuthority,
            'joiningDate': str(self.joiningDate) if self.joiningDate else None,
            'profilePhoto': self.profilePhoto,
        }


class Managers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    mobileNumber = db.Column(unique=True, nullable=False)
    emailId = db.Column(db.String(255), unique=True, nullable=False)
    workStation = db.Column(db.Integer, db.ForeignKey('workstations.id'))
    workStationName = db.relationship('Workstations', backref=db.backref('managers', lazy=True))
    post = db.Column()
    employeeId = db.Column(db.String(255), unique=True, nullable=False)
    reportAuthority = db.Column()
    joiningDate = db.Column(db.Date)  # Assuming joiningDate is a date column
    profilePhoto = db.Column(db.String(255))  # Assuming profilePhoto is a file path or URL

    def as_dict(self):
        return {
            'userId': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'mobileNumber': self.mobileNumber,
            'emailId': self.emailId,
            'workStation': self.workStation,
            'workStationName': self.workStationName.workStationName,
            'post': self.post,
            'employeeId': self.employeeId,
            'reportAuthority': self.reportAuthority,
            'joiningDate': str(self.joiningDate) if self.joiningDate else None,
            'profilePhoto': self.profilePhoto,
        }


class Workstations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workStationName = db.Column(db.String(255))

    def as_dict(self):
        return {
            'id': self.id,
            'workStationName': self.workStationName}

class Task(db.Model):
    taskId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    taskName = db.Column(db.String(255), nullable=False)
    activityId = db.Column()
    subActivityId = db.Column()
    activityName = db.Column()
    subActivityName = db.Column()
    modeName = db.Column()
    modeId = db.Column()
    startDate = db.Column()
    endDate = db.Column()
    workStation = db.Column(db.Integer, db.ForeignKey('workstations.id'))
    workStationName = db.relationship('Workstations', backref=db.backref('task', lazy=True))
    user_alloted = db.Column(db.Integer, default=0)
    user_completed_task = db.Column(db.Integer, default=0)
    createdBy = db.Column(db.Integer, default=1)

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
            'workStation': self.workStation,
            'workStationName': self.workStationName.workStationName,
            'user_alloted': self.user_alloted,
            'user_completed_task': self.user_completed_task,
            'createdBy': self.createdBy
        }


class UserTask(db.Model):
    userTaskId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column()
    taskId = db.Column()
    totalUnits = db.Column(nullable=False)
    completedUnit = db.Column(db.Integer, default=0)
    isTaskComplete = db.Column(db.Integer, default=0)
    assignBy = db.Column(db.Integer, default=1)
    workStation = db.Column(db.Integer, db.ForeignKey('workstations.id'))
    workStationName = db.relationship('Workstations', backref=db.backref('user_task', lazy=True))

    def as_dict(self):
        return {
            'userTaskId': self.userTaskId,
            'userId': self.userId,
            'taskId': self.taskId,
            'totalUnits': self.totalUnits,
            'completedUnit': self.completedUnit,
            'isTaskComplete': self.isTaskComplete,
            'assignBy': self.assignBy,
            'workStation': self.workStation,
            'workStationName': self.workStationName.workStationName
        }


class TaskUpdates(db.Model):
    taskUpdateId = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    workStation = db.Column(db.Integer, db.ForeignKey('workstations.id'))
    workStationName = db.relationship('Workstations', backref=db.backref('task_updates', lazy=True))

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
            'update_date': str(self.update_date) if self.update_date else None,
            'workStation': self.workStation,
            'workStationName': self.workStationName.workStationName
        }


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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


class RelWorkstation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workStation = db.Column(db.Integer, db.ForeignKey('user.ws'))
    security_workStation = db.Column(db.Integer, db.ForeignKey('user.ws'))
def to_dict(model):
    return {column.key: getattr(model, column.key) for column in class_mapper(model.__class__).mapped_table.c}