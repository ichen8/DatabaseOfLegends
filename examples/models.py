from app import db
from sqlalchemy.dialects.postgresql import JSON

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, index=True, nullable=False)
    password = db.Column(db.String(10), nullable=False)

    lastname = db.Column(db.String(), nullable=False)
    firstname = db.Column(db.String(), nullable=False)

    staddress = db.Column(db.String(), nullable=False)
    staddress2 = db.Column(db.String())
    city = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    zip = db.Column(db.String(), nullable=False)

    startdate = db.Column(db.DateTime, nullable=False)

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return self.id
 
    def __repr__(self):
        return '<id {}>' % (self.id)

class Child(db.Model):
    __tablename__ = 'child'

    id = db.Column(db.Integer, primary_key=True)
    childname = db.Column(db.String(), nullable=False)
    sex = db.Column(db.String(), nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Response(db.Model):
    __tablename__ = 'response'

    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    listens = db.Column(db.Integer, nullable=False)
    looks = db.Column(db.Integer, nullable=False)
    moves = db.Column(db.Integer, nullable=False)
    touches = db.Column(db.Integer, nullable=False)
    smells = db.Column(db.Integer, nullable=False)
    tastes = db.Column(db.Integer, nullable=False)
    talks = db.Column(db.Integer, nullable=False)

    answer1 = db.Column(db.Boolean, nullable=False)
    answer2 = db.Column(db.Boolean, nullable=False)
    answer3 = db.Column(db.Boolean, nullable=False)
    answer4 = db.Column(db.Boolean, nullable=False)
    answer5 = db.Column(db.Boolean, nullable=False)
    answer6 = db.Column(db.Boolean, nullable=False)
    answer7 = db.Column(db.Boolean, nullable=False)
    answer8 = db.Column(db.Boolean, nullable=False)
    answer9 = db.Column(db.Boolean, nullable=False)
    answer10 = db.Column(db.Boolean, nullable=False)
    answer11 = db.Column(db.Boolean, nullable=False)
    answer12 = db.Column(db.Boolean, nullable=False)
    answer13 = db.Column(db.Boolean, nullable=False)
    answer14 = db.Column(db.Boolean, nullable=False)
    answer15 = db.Column(db.Boolean, nullable=False)
    answer16 = db.Column(db.Boolean, nullable=False)
    answer17 = db.Column(db.Boolean, nullable=False)
    answer18 = db.Column(db.Boolean, nullable=False)
    answer19 = db.Column(db.Boolean, nullable=False)
    answer20 = db.Column(db.Boolean, nullable=False)
    answer21 = db.Column(db.Boolean, nullable=False)
    answer22 = db.Column(db.Boolean, nullable=False)
    answer23 = db.Column(db.Boolean, nullable=False)
    answer24 = db.Column(db.Boolean, nullable=False)
    answer25 = db.Column(db.Boolean, nullable=False)
    answer26 = db.Column(db.Boolean, nullable=False)
    answer27 = db.Column(db.Boolean, nullable=False)
    answer28 = db.Column(db.Boolean, nullable=False)
    answer29 = db.Column(db.Boolean, nullable=False)
    answer30 = db.Column(db.Boolean, nullable=False)

    dev_age = db.Column(db.Integer, nullable=False)
    chr_age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Form(db.Model):
    __tablename__ = 'form'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    variation = db.Column(db.String(), nullable=True)

    question1 = db.Column(db.Text, nullable=False)
    question2 = db.Column(db.Text, nullable=False)
    question3 = db.Column(db.Text, nullable=False)
    question4 = db.Column(db.Text, nullable=False)
    question5 = db.Column(db.Text, nullable=False)
    question6 = db.Column(db.Text, nullable=False)
    question7 = db.Column(db.Text, nullable=False)
    question8 = db.Column(db.Text, nullable=False)
    question9 = db.Column(db.Text, nullable=False)
    question10 = db.Column(db.Text, nullable=False)
    question11 = db.Column(db.Text, nullable=False)
    question12 = db.Column(db.Text, nullable=False)
    question13 = db.Column(db.Text, nullable=False)
    question14 = db.Column(db.Text, nullable=False)
    question15 = db.Column(db.Text, nullable=False)
    question16 = db.Column(db.Text, nullable=False)
    question17 = db.Column(db.Text, nullable=False)
    question18 = db.Column(db.Text, nullable=False)
    question19 = db.Column(db.Text, nullable=False)
    question20 = db.Column(db.Text, nullable=False)
    question21 = db.Column(db.Text, nullable=False)
    question22 = db.Column(db.Text, nullable=False)
    question23 = db.Column(db.Text, nullable=False)
    question24 = db.Column(db.Text, nullable=False)
    question25 = db.Column(db.Text, nullable=False)
    question26 = db.Column(db.Text, nullable=False)
    question27 = db.Column(db.Text, nullable=False)
    question28 = db.Column(db.Text, nullable=False)
    question29 = db.Column(db.Text, nullable=False)
    question30 = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Prescription(db.Model):
    __tablename__ = 'prescription'

    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    prescrip1 = db.Column(db.Integer, db.ForeignKey('prescrip.prescripid'), nullable=False)
    prescrip2 = db.Column(db.Integer, db.ForeignKey('prescrip.prescripid'), nullable=False)
    prescrip3 = db.Column(db.Integer, db.ForeignKey('prescrip.prescripid'), nullable=False)
    prescrip4 = db.Column(db.Integer, db.ForeignKey('prescrip.prescripid'), nullable=False)
    prescrip5 = db.Column(db.Integer, db.ForeignKey('prescrip.prescripid'), nullable=False)
    prescrip6 = db.Column(db.Integer, db.ForeignKey('prescrip.prescripid'), nullable=False)
    prescrip7 = db.Column(db.Integer, db.ForeignKey('prescrip.prescripid'), nullable=False)
    prescrip8 = db.Column(db.Integer, db.ForeignKey('prescrip.prescripid'), nullable=False)
    prescrip9 = db.Column(db.Integer, db.ForeignKey('prescrip.prescripid'), nullable=False)
    prescrip10 = db.Column(db.Integer, db.ForeignKey('prescrip.prescripid'), nullable=False)

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Prescrip(db.Model):
    __tablename__ = 'prescrip'

    prescripid = db.Column(db.Integer, primary_key=True)
    form = db.Column(db.String(), nullable=False)
    actid = db.Column(db.Integer, nullable=False)
    prescript = db.Column(db.Text, nullable=False)

    girl = db.Column(db.Boolean, nullable=False)
    boy = db.Column(db.Boolean, nullable=False)
    audinput = db.Column(db.Boolean, nullable=False)
    visinput = db.Column(db.Boolean, nullable=False)
    kininput = db.Column(db.Boolean, nullable=False)
    tacinput = db.Column(db.Boolean, nullable=False)
    olfinput = db.Column(db.Boolean, nullable=False)
    gusinput = db.Column(db.Boolean, nullable=False)
    oroutput = db.Column(db.Boolean, nullable=False)
    motoutput = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<id {}>'.format(self.id)