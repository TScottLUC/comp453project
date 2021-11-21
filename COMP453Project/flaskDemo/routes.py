import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt
from flaskDemo.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, AssignmentForm
from flaskDemo.models import User, Gene, Protein, Paper, Authors, Ligand, Organism, ReferencedIn, BiologicalProcess, GOAnnotations, FoundIn
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.route("/")
@app.route("/home")
def home():
    results = Protein.query.join(GOAnnotations, Protein.UniProtEntryID == GOAnnotations.UniProtEntryID) \
                .add_columns(Protein.UniProtEntryID, Protein.ScientificName, Protein.Function, Protein.AALength) \
                .join(BiologicalProcess, GOAnnotations.GOTermID == BiologicalProcess.GOTermID) \
                .add_columns(BiologicalProcess.GOTermID, BiologicalProcess.Name, GOAnnotations.Qualifier)
    return render_template('assign_home.html', title="GO Annotations", m_n_join = results)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/assignments/<GOTermID>/<UniProtEntryID>", methods=['Get','Post'])
@login_required
def assign(GOTermID, UniProtEntryID):
    goannotation = GOAnnotations.query.get_or_404([UniProtEntryID, GOTermID])
    return render_template('assign.html', title=goannotation.UniProtEntryID + '_' + goannotation.GOTermID, goannotation=goannotation, now=datetime.utcnow())


@app.route("/assignment/new", methods=['Get','Post'])
@login_required
def new_assign():
    form = AssignmentForm()
    if form.validate_on_submit():
        assign = GOAnnotations(UniProtEntryID=form.UniProtEntryID.data, GOTermID=form.GOTermID.data, Qualifier=form.Qualifier.data)
        db.session.add(assign)
        db.session.commit()
        flash('You have added a new assignment!', 'success')
        return redirect(url_for('home'))
    return render_template('create_assign.html', title='New Assignment',
                           form=form, legend='New Assignment')



@app.route("/assign/<GOTermID>/<UniProtEntryID>/delete", methods=['POST'])
@login_required
def delete_assign(GOTermID, UniProtEntryID):
    #return"delete page under construction"
    goannotation = GOAnnotations.query.get_or_404([UniProtEntryID, GOTermID]))
    db.session.delete(goannotation)
    db.session.commit()
    flash('The assignment has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/assign/<GOTermID>/<UniProtEntryID>/update", methods=['GET', 'POST'])
@login_required
def update_assign(GOTermID, UniProtEntryID):
    return"update page under construction"
    dept = Department.query.get_or_404(dnumber)
    currentDept = dept.dname

    form = DeptUpdateForm()
    if form.validate_on_submit():          # notice we are are not passing the dnumber from the form
        if currentDept !=form.dname.data:
            dept.dname=form.dname.data
            dept.mgr_ssn=form.mgr_ssn.data
            dept.mgr_start=form.mgr_start.data
            db.session.commit()
            flash('Your department has been updated!', 'success')
        return redirect(url_for('goannotation', GOTermID=GOTermID, UniProtEntryID=UniProtEntryID))
    elif request.method == 'GET':              # notice we are not passing the dnumber to the form
        form.dnumber.data = dept.dnumber
        form.dname.data = dept.dname
        form.mgr_ssn.data = dept.mgr_ssn
        form.mgr_start.data = dept.mgr_start
    return render_template('create_dept.html', title='Update Department',
                           form=form, legend='Update Department')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

