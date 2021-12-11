import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskDemo import app, db, bcrypt, mysql
from flaskDemo.forms import RegistrationForm, LoginForm, UpdateAccountForm, AssignmentForm, GOAnnotationUpdateForm
from flaskDemo.models import User, Gene, Protein, Paper, Authors, Ligand, Organism, ReferencedIn, BiologicalProcess, GOAnnotations, FoundIn
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

@app.route("/")
@app.route("/home")
def home():
    
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM protein")
    proteins = cursor.fetchall()

    cursor.execute("SELECT protein.UniProtEntryID, goannotations.Qualifier, biologicalprocess.Name FROM protein, goannotations, biologicalprocess WHERE protein.UniProtEntryID = goannotations.UniProtEntryID AND goannotations.GOTermID = biologicalprocess.GOTermID AND goannotations.GOTermID IN (SELECT GOTermID FROM goannotations WHERE Qualifier = '"'located_in'"')")
    locations = cursor.fetchall()

    subquery = Ligand.query.with_entities(Ligand.UniProtEntryID).subquery()
    ligands = Protein.query.filter(Protein.UniProtEntryID.in_(subquery)).distinct()

    return render_template('home.html', title="Home", proteins=proteins, locations=locations, ligands=ligands)

@app.route("/")
@app.route("/<UniProtEntryID>/info", methods=['Get','Post'])
def protein(UniProtEntryID):
    protein = Protein.query.get_or_404(UniProtEntryID)

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM gene LEFT JOIN protein ON gene.GeneID = protein.GeneID WHERE protein.UniProtEntryID = '" + str(UniProtEntryID) + "'")

    gene = cursor.fetchone()

    goannotations = GOAnnotations.query.filter(GOAnnotations.UniProtEntryID == UniProtEntryID).join(BiologicalProcess, BiologicalProcess.GOTermID == GOAnnotations.GOTermID).add_columns(BiologicalProcess.GOTermID, BiologicalProcess.Name, GOAnnotations.Qualifier)
    ligands = Ligand.query.filter(Ligand.UniProtEntryID == UniProtEntryID)
    papers = ReferencedIn.query.filter(ReferencedIn.UniProtEntryID == UniProtEntryID).join(Paper, Paper.DOI == ReferencedIn.DOI).add_columns(ReferencedIn.DOI, Paper.Title, Paper.Journal, Paper.PublicationDate)

    return render_template('protein_page.html', title=protein.UniProtEntryID, protein=protein, gene=gene, goannotations=goannotations, ligands=ligands, papers=papers)


@app.route("/")
@app.route("/go_annotations")
def go_annotations():
    results = Protein.query.join(GOAnnotations, Protein.UniProtEntryID == GOAnnotations.UniProtEntryID) \
                .add_columns(Protein.UniProtEntryID, Protein.ScientificName, Protein.Function, Protein.AALength) \
                .join(BiologicalProcess, GOAnnotations.GOTermID == BiologicalProcess.GOTermID) \
                .add_columns(BiologicalProcess.GOTermID, BiologicalProcess.Name, GOAnnotations.Qualifier)
    return render_template('go_annotations.html', title="GO Annotations", m_n_join = results)


@app.route("/go_annotations/<GOTermID>/<UniProtEntryID>", methods=['Get','Post'])
@login_required
def go_annotation(GOTermID, UniProtEntryID):
    goannotation = GOAnnotations.query.get_or_404([UniProtEntryID, GOTermID])
    return render_template('edit_go_annotation.html', title=goannotation.UniProtEntryID + '_' + goannotation.GOTermID, goannotation=goannotation, now=datetime.utcnow())


@app.route("/go_annotations/new", methods=['Get','Post'])
@login_required
def new_go_annotation():
    form = AssignmentForm()
    if form.validate_on_submit():
        assign = GOAnnotations(UniProtEntryID=form.UniProtEntryID.data, GOTermID=form.GOTermID.data, Qualifier=form.Qualifier.data)
        db.session.add(assign)
        db.session.commit()
        flash('You have added a new assignment!', 'success')
        return redirect(url_for('go_annotations'))
    return render_template('create_go_annotation.html', title='New GO Annotation',
                           form=form, legend='New GO Annotation')



@app.route("/go_annotations/<GOTermID>/<UniProtEntryID>/delete", methods=['POST'])
@login_required
def delete_go_annotation(GOTermID, UniProtEntryID):
    goannotation = GOAnnotations.query.get_or_404([UniProtEntryID, GOTermID])
    db.session.delete(goannotation)
    db.session.commit()
    flash('The assignment has been deleted!', 'success')
    return redirect(url_for('go_annotations'))


@app.route("/go_annotations/<GOTermID>/<UniProtEntryID>/update", methods=['GET', 'POST'])
@login_required
def update_go_annotation(GOTermID, UniProtEntryID):

    goAnnotation = GOAnnotations.query.get_or_404([UniProtEntryID, GOTermID])
    currentUniProtEntryID = goAnnotation.UniProtEntryID
    currentGOTermID = goAnnotation.GOTermID
    currentQualifier = goAnnotation.Qualifier

    form = GOAnnotationUpdateForm(startingUniProtEntryID=currentUniProtEntryID, startingGOTermID=currentGOTermID)
    if form.validate_on_submit():         
        goAnnotation.UniProtEntryID=form.UniProtEntryID.data
        goAnnotation.GOTermID=form.GOTermID.data
        goAnnotation.Qualifier=form.Qualifier.data
        db.session.commit()
        flash('Your GO Annotation has been updated!', 'success')
        return redirect(url_for('assign', GOTermID=goAnnotation.GOTermID, UniProtEntryID=goAnnotation.UniProtEntryID))
    elif request.method == 'GET':              
        form.UniProtEntryID.data = currentUniProtEntryID
        form.GOTermID.data = currentGOTermID
        form.Qualifier.data = currentQualifier
    return render_template('create_go_annotation.html', title='Update GO Annotation',
                           form=form, legend='Update GO Annotation')

@app.route("/largeProteins", methods=['Get','Post'])
def aminoAcidLength():
    proteins = Protein.query.all()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT AVG(AALength) AS avgAALength FROM protein")
    amino = cursor.fetchone()
    cursor.execute("SELECT * FROM protein WHERE AALength > (SELECT AVG(AALength) as AverageAALength FROM protein)")
    proteins = cursor.fetchall()

    return render_template('amino.html', proteins=proteins, amino=amino, title="Large Proteins")


@app.route("/cellMolImmunolPapers", methods=['Get','Post'])
def paperDateJournal():
    allpapers = Paper.query.all()

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM paper WHERE Journal='Cell Mol Immunol.' AND PublicationDate > '2020-01-01'")
    papers = cursor.fetchall()


    return render_template('papers.html', papers=papers, title="Cellular and Molecular Immunology Papers (2020-Present)")


@app.route("/2021Papers", methods=['Get', 'Post'])
def paperByYear():
    allpapers = Paper.query.all()
    papers = Paper.query.filter(Paper.PublicationDate > '2021-01-01')

    return render_template('papers.html', papers=papers, title="2021 Papers")

@app.route("/enablesProteinBinding", methods=['Get', 'Post'])
def annotationQualifierGoID():
    proteins = GOAnnotations.query.filter(GOAnnotations.Qualifier == 'enables', GOAnnotations.GOTermID== 'GO:0005515').join(Protein, GOAnnotations.UniProtEntryID==Protein.UniProtEntryID).add_columns(Protein.UniProtEntryID, Protein.Function, Protein.AALength, Protein.StructureFile, Protein.ScientificName)

    return render_template('enablesProteinBinding.html', proteins=proteins, title="Enables Protein Binding")

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

