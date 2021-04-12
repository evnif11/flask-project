from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Todo(db.Model):
    __tablename__ = 'todo'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(256))
    status = db.Column(db.Integer)
    due = db.Column(db.String(64))
    tstamp = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'user': self.user.userid,
            'tstamp': self.tstamp
        }


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(32))
    password = db.Column(db.String(128))
    todos = db.relationship('Todo', backref='user', lazy=True)
