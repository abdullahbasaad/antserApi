from flask import Flask, render_template, redirect, url_for, flash, session, make_response, jsonify, request
from flask_restful import Api, Resource
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user
from datetime import timedelta 
from endpoints import get_data, data_describtion, user_profile
from upload_csv import upload_csv_file
from globals import *
from Model import User, db, Profile_setting
from update_setting import get_user_profile, get_setting, get_profile_setting


app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'Should be secret!!!'
app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql://postgres:pass@ip address/Data base name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = 'public-key'
app.config['RECAPTCHA_PRIVATE_KEY'] = 'private-key'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)

#app.config['APP_THEME'] = "spacelab.css"

''' Routing '''
app.register_blueprint(get_data)
app.register_blueprint(data_describtion)
app.register_blueprint(upload_csv_file)
app.register_blueprint(user_profile)
app.register_blueprint(get_setting)
app.register_blueprint(get_user_profile)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except:
        return None

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=40)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(max=100)])
    user_name = StringField('User Name', validators=[InputRequired(), Length(min=4, max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=40)])
    confirmPassword = PasswordField('Confirm Password', [EqualTo('password', message='Passwords must match.')])
    recaptcha = RecaptchaField()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                auto_kill = get_profile_setting(user.email).kill_session
                if auto_kill > 0:
                    session.permanent = True
                    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=float(auto_kill))
                else:
                    session.permanent = False

                session['username'] = user.user_name
                session['email'] = user.email
                flash("You are successfuly logged in!", 'success')  
                return redirect(url_for('dashboard'))

        flash("Invalid user name or password!", 'error') 
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email address is already inserted', 'error')
        else:
            new_user = User(user_name=form.user_name.data, email=form.email.data, password=hashed_password)
            set = Profile_setting(email=form.email.data, kill_session= 0, theme= 'Defualt theme')
            db.session.add(new_user)
            db.session.add(set)
            db.session.commit()
            
            flash('User has been created', 'success')
        return render_template('signup.html', form=form)

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', thms = THEMES ,tms= LOGIN_SESSIONS_TIMES, name= session['username'], data= get_profile_setting(session['email']))

@login_required
def upload_data():
    return url_for(upload_csv_file)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/load-data')
@login_required
def load_data():
    return render_template('Load_data.html',records=DATASETSNROOT, colnames=COLUMNNAMES)

@app.route('/describe')
@login_required
def data_describe():
    if len(COLUMNDATATYPES) == 0:
        flash('No dataset has been loaded..','error')
        return render_template('dashboard.html', name= session['username'])
    else:
        return render_template("describtion.html", records=COLUMNDATATYPES, data_stat=DATDICREF, obj_stat=OBJDICREF,
                                num_stat=NUMDICREF, cat_stat=CATDICREF)


@app.route("/json")
@login_required
def get_json():
    res = make_response(jsonify(DATASETS), 200)
    return res

class Dataset(Resource):

    # Endpoint to check a Query string validation
    @app.route("/qstr")
    @login_required
    def qs():
        if request.args:
            req = request.args
            res = {}
            for key, value in req.items():
                res[key] = value

            res = make_response(jsonify(res), 200)
            return res

        res = make_response(jsonify({"error": "No Query String"}), 404)
        return res

    # Endpoint to make a query from a Json structure or return error
    @app.route("/json/<collection>/<member>")
    @login_required
    def get_data(collection, member):
        print("getting the value of %s in the collection %s" % (member, collection))
        if collection in DATASETS:
            member = DATASETS[collection].get(member)
            if member:
                res = make_response(jsonify({"res": member}), 200)
                return res

            res = make_response(jsonify({"error": "A member not found"}), 404)
            return res

        res = make_response(jsonify({"error": "A collection not found"}), 404)
        return res

    # Endpoint to PUT a update a member value in a particular collection
    @app.route("/json/<collection>/<member>", methods=["PUT"])
    @login_required
    def put_col_mem(collection, member):
        req = request.get_json()

        if collection in DATASETS:
            if member:
                DATASETS[collection][member] = req["new"]
                res = make_response(jsonify({"res": DATASETS[collection]}), 200)
                return res

            res = make_response(jsonify({"error": "Memeber Not found"}), 404)
            return res

        res = make_response(jsonify({"error": "Collection Not found"}), 404)
        return res

    # Endpoint to DELETE a particular collection
    @app.route("/json/<collection>", methods=["DELETE"])
    @login_required
    def delete_col(collection):

        if collection in DATASETS:
            del DATASETS[collection]
            res = make_response(jsonify({"Success": "Collection is deleted"}), 200)
            return res

        res = make_response(jsonify({"error": "Collection not found"}), 404)
        return res  

    # Endpoint to POST a new row or a query from a Json structure or return error
    @app.route("/json/<collection>", methods=["POST"])
    @login_required
    def create_col(collection):
        req = request.get_json()

        if collection in DATASETS:
            res = make_response(jsonify({"error": "Collection already exists"}), 400)
            return res

        DATASETS.update({collection: req})

        res = make_response(jsonify({"Message": "Collection created"}), 201)
        return res

api.add_resource(Dataset, "/json")
  

if __name__ == '__main__':
    print("Server running in port %s" % (PORT))
    db.init_app(app)
    app.run(host='0.0.0.0', port=PORT)
