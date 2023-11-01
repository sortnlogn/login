from flask import Flask, render_template, redirect, url_for
from flask import request, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # секретный ключ для шифрования сессии, необходим для Flask-Login
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # URI базы данных
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # указываем на функцию для авторизации

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['role_id']

        user = User(username=username, password=password, role_id=role_id)
        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    if 'username' in session:
        if User.query.filter_by(username=session['username'], role='admin').first():
            return 'Welcome, admin!'
        else:
            return 'You are not authorized to access this page!'
    else:
        return redirect(url_for('login'))

@app.route('/teacher')
def teacher():
    if 'username' in session:
        if User.query.filter_by(username=session['username'], role='teacher').first():
            return 'Welcome, teacher!'
        else:
            return 'You are not authorized to access this page!'
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
