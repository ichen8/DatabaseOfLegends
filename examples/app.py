import os
import datetime
import random

from flask import Flask, render_template, request, redirect, session, url_for, abort, g
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask.ext.heroku import Heroku
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required


app = Flask(__name__)
app.secret_key = "super secrety key"
app.debug = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://jpgcdlakhlfgwm:6fa195bb8dc3205531771afadae5f094d64d08d89af64e3a46ad14712f471cae@ec2-50-19-113-219.compute-1.amazonaws.com:5432/dft9g1vmha5fqm"
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:password@localhost/watchmegrowdb"

heroku = Heroku(app)
db = SQLAlchemy(app)

from models import *

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    user = User()
    user.email = request.form['txtEmail']
    user.password = request.form['txtPassword']

    user.lastname = request.form['txtLastName']
    user.firstname = request.form['txtFirstName']

    user.staddress = request.form['txtAddress']
    user.city = request.form['txtCity']
    user.state = request.form['txtState']
    user.zip = request.form['txtZip']
    user.startdate = datetime.datetime.now().date()

    db.session.add(user)
    db.session.commit()

    login_user(user)
    return redirect(url_for('index'))
 
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['txtEmail']
    password = request.form['txtPassword']
    registered_user = User.query.filter_by(email=email, password=password).first()
    if registered_user is None:
        return redirect(url_for('login'))
    login_user(registered_user)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index')) 

@app.route('/')
@login_required
def index():
    childtable = []
    children = Child.query.filter_by(parent_id=current_user.get_id()).all()
    for child in children:
        child_dict = {
            "name": child.childname,
            "birthdate": child.birthdate,
            "id": child.id,
            "responsestatus": ""
        }

        if _get_response_status(child) == True:
            child_dict["responsestatus"] = "Create New Response"

        childtable.append(child_dict)

    return render_template('index.html', childtable=childtable)

@app.route('/child/', methods=['GET', 'POST'])
@login_required
def child():
    if request.method == "GET":
        return render_template('child.html')

    child = Child()
    child.childname = request.form['txtChildName']
    child.sex = request.form['radioGender']
    child.birthdate = request.form['birthdate']
    child.parent_id = current_user.get_id()

    db.session.add(child)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/response/<childid>', methods=['GET'])
@app.route('/response/<childid>/<formid>', methods=['POST'])
@login_required
def response(childid, formid=None):
    child = Child.query.get(int(childid))
    if child == None:
        return "invalid child id"
    elif child.parent_id != current_user.get_id():
        return "authentication error"

    if request.method == "GET":
        if _get_response_status(child) == False:
            return "new response not required"

        form_number = int((_get_month_diff(child.birthdate) / 6) + 1)
        forms = Form.query.filter_by(number=form_number).all()
        form = random.choice(forms)

        details = {
            "childid": childid,
            "formid": form.id
        }

        questions = {}
        for col in Form.__table__.columns:
            q = col.name
            if q != "id" and q != "number" and q != "variation":
                questions[q] = getattr(form, q)

        return render_template('response.html', questions=questions, details=details)

    response = Response()
    response.child_id = int(childid)
    response.form_id = int(formid)
    response.date = datetime.datetime.now().date()

    response.listens = request.form['rangeListens']
    response.looks = request.form['rangeLooks']
    response.moves = request.form['rangeMoves']
    response.touches = request.form['rangeTouches']
    response.smells = request.form['rangeSmells']
    response.tastes = request.form['rangeTastes']
    response.talks = request.form['rangeTalks']

    response.answer1 = 'chkQ1' in request.form
    response.answer2 = 'chkQ2' in request.form
    response.answer3 = 'chkQ3' in request.form
    response.answer4 = 'chkQ4' in request.form
    response.answer5 = 'chkQ5' in request.form
    response.answer6 = 'chkQ6' in request.form
    response.answer7 = 'chkQ7' in request.form
    response.answer8 = 'chkQ8' in request.form
    response.answer9 = 'chkQ9' in request.form
    response.answer10 = 'chkQ10' in request.form
    response.answer11 = 'chkQ11' in request.form
    response.answer12 = 'chkQ12' in request.form
    response.answer13 = 'chkQ13' in request.form
    response.answer14 = 'chkQ14' in request.form
    response.answer15 = 'chkQ15' in request.form
    response.answer16 = 'chkQ16' in request.form
    response.answer17 = 'chkQ17' in request.form
    response.answer18 = 'chkQ18' in request.form
    response.answer19 = 'chkQ19' in request.form
    response.answer20 = 'chkQ20' in request.form
    response.answer21 = 'chkQ21' in request.form
    response.answer22 = 'chkQ22' in request.form
    response.answer23 = 'chkQ23' in request.form
    response.answer24 = 'chkQ24' in request.form
    response.answer25 = 'chkQ25' in request.form
    response.answer26 = 'chkQ26' in request.form
    response.answer27 = 'chkQ27' in request.form
    response.answer28 = 'chkQ28' in request.form
    response.answer29 = 'chkQ29' in request.form
    response.answer30 = 'chkQ30' in request.form

    # calculate developmental age
    form_number = Form.query.get(response.form_id).number
    num_tasks = 0
    for i in range(1, 31):
        if getattr(response, "answer" + str(i)):
            num_tasks += 1
    response.dev_age = (form_number * 6) + (num_tasks / 5) - 6

    #calculate chronological age
    response.chr_age = _get_month_diff(child.birthdate)

    db.session.add(response)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/prescription/<childid>')
@login_required
def prescription(childid):
    child = Child.query.get(int(childid))
    if child == None:
        return "invalid child id"
    elif child.parent_id != current_user.get_id():
        return "authentication error"

    # get most recent prescription
    latest_prescription = Prescription.query.filter_by(child_id=int(childid)).order_by(desc(Prescription.date)).first()
    if latest_prescription != None:
        if _get_month_diff(latest_prescription.date) == 0:
            #return "too soon for new prescription"
            prescriptable = []
            for i in range(1, 11):
                prescrip_id = getattr(latest_prescription, "prescrip" + str(i))
                prescriptable.append(Prescrip.query.get(prescrip_id).prescript)
            return render_template('prescription.html', prescriptable=prescriptable)

    # get most recent response
    response = Response.query.filter_by(child_id=int(childid)).order_by(desc(Response.date)).first()

    if response == None:
        return "no responses"
    
    birthdate = Child.query.get(int(childid)).birthdate
    chr_age = _get_month_diff(birthdate)
    dev_age = response.dev_age + ((response.dev_age * _get_month_diff(response.date)) / response.chr_age)
    age = max(dev_age, chr_age)

    form = Form.query.get(response.form_id)
    if age > form.number * 6:
        return "need to submit new response"

    prescrip_list = []

    """
    Selects prescriptions which cannot be done by the child which are 
    at or below the child's current chronological or developmental age, whichever is higher
    """
    maxi = 30
    if age % 6 != 0:
        maxi = int((age % 6) * 5)
    for i in range(1, maxi + 1):
        if getattr(response, "answer" + str(i)) == False:
            prescrips = Prescrip.query.filter_by(form=str(form.number) + str(form.variation), actid=i).all()
            prescrip = random.choice(prescrips)
            prescrip_list.append(prescrip)

    """
    If there are fewer than 10 tasks meeting these criteria, select as many prescriptions as are needed
    appropriate for the child's developmental age
    """
    maxj = 30
    if dev_age % 6 != 0:
        maxj = int((dev_age % 6) * 5)
    while len(prescrip_list) < 10:
        actid = random.randint(maxj - 5, maxj)
        prescrips = Prescrip.query.filter_by(form=str(form.number) + str(form.variation), actid=actid).all()
        prescrip = random.choice(prescrips)
        prescrip_list.append(prescrip)

    random.shuffle(prescrip_list)

    prescription = Prescription()
    prescription.child_id = int(childid)
    prescription.response_id = response.id
    prescription.date = datetime.datetime.now().date()

    prescriptable = []
    for i in range(1, 11):
        setattr(prescription, "prescrip" + str(i), prescrip_list[i - 1].prescripid)
        prescriptable.append(prescrip_list[i - 1].prescript)

    db.session.add(prescription)
    db.session.commit()

    return render_template('prescription.html', prescriptable=prescriptable)

@app.route('/delete/<childid>')
@login_required
def delete(childid):
    child = Child.query.get(int(childid))
    if child == None:
        return "invalid child id"
    elif child.parent_id != current_user.get_id():
        return "authentication error"

    prescriptions = Prescription.query.filter_by(child_id=int(childid)).all()
    for prescription in prescriptions:
        db.session.delete(prescription)

    responses = Response.query.filter_by(child_id=int(childid)).all()
    for response in responses:
        db.session.delete(response)

    child = Child.query.get(int(childid))
    db.session.delete(child)
    db.session.commit()
    return redirect(url_for('index'))

def _get_month_diff(d1, d2=None):
    if d2 == None:
        d2 = datetime.datetime.now().date()
    return (d2.year - d1.year) * 12 + d2.month - d1.month

"""
Return true if child requires new response, false otherwise
Child requires new response once every 6 months
"""
def _get_response_status(child):
    form_number = int((_get_month_diff(child.birthdate) / 6) + 1)

    if form_number > 6:
        return False

    #check if child already has response for this form number
    response = Response.query.filter_by(child_id=child.id).order_by(desc(Response.date)).first()
    if (response != None) and (Form.query.get(response.form_id).number >= form_number):
        return False

    return True

if __name__ == '__main__':
    app.run()