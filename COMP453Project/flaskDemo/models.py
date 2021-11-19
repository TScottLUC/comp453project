from datetime import datetime
from flaskDemo import db, login_manager
from flask_login import UserMixin
from functools import partial
from sqlalchemy import orm

db.Model.metadata.reflect(db.engine)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['user']

    def get_id(self):
        return (self.userid)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Gene(db.Model):
    __table__ = db.Model.metadata.tables['gene']
    
class Protein(db.Model):
    __table__ = db.Model.metadata.tables['protein']

class Paper(db.Model):
    __table__ = db.Model.metadata.tables['paper']

class Authors(db.Model):
    __table__ = db.Model.metadata.tables['authors']

class Ligand(db.Model):
    __table__ = db.Model.metadata.tables['ligand']

class Organism(db.Model):
    __table__ = db.Model.metadata.tables['organism']

class ReferencedIn(db.Model):
    __table__ = db.Model.metadata.tables['referencedin']

class BiologicalProcess(db.Model):
    __table__ = db.Model.metadata.tables['biologicalprocess']

class GOAnnotations(db.Model):
    __table__ = db.Model.metadata.tables['goannotations']

class FoundIn(db.Model):
    __table__ = db.Model.metadata.tables['foundin']
    

  
