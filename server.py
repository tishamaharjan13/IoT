from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
import asyncio
from databases import Database
import jwt
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, set_access_cookies, unset_jwt_cookies
)

from functools import wraps
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from Models.capture import capture_face
from Models.training import train_model

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define User model
class Users(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create tables (run once at startup)
with app.app_context():
    db.create_all()

# If you need async support with databases package
database = Database("sqlite:///db.sqlite")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwt_token')
        
        if not token:
            return redirect(url_for('login_route'))  # Redirect to login if no token
            
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Users.query.filter_by(id=data['public_id']).first()
            if not current_user:
                return redirect(url_for('login_route'))
        except ExpiredSignatureError:
            return redirect(url_for('login_route'))  # Redirect if token expired
        except InvalidTokenError:
            return redirect(url_for('login_route'))  # Redirect if invalid token
            
        return f(current_user, *args, **kwargs)
    return decorated

@app.get("/")
def index_route():
    if request.cookies.get("jwt_token"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.get("/dashboard")
@token_required
def dashboard(current_user):
    print(current_user.name)
    return render_template("users.html", fullName=current_user.name)

@app.get("/login")
def login_route():
    if request.cookies.get("jwt_token"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.post("/login")
def post_login_route():
    email = request.form["email"]
    password = request.form["password"]
    user = Users.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid email or password'}), 401

    token = jwt.encode({'public_id': user.id, 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},app.config['SECRET_KEY'], algorithm="HS256")

    response = make_response(redirect(url_for('dashboard')))
    response.set_cookie('jwt_token', token)
    return response

@app.get("/signup")
def register_route():
    if request.cookies.get("jwt_token"):
        return redirect(url_for("dashboard"))
    return render_template("signup.html")

@app.post("/signup")
def post_signup_route():
    fullName = request.form["fullName"]
    email = request.form["email"]
    password = request.form["password"]
    
    # Check if user exists (synchronous version)
    user_exists = Users.query.filter_by(email=email).first() is not None
    if user_exists:
        return jsonify({'message': 'User already exists. Please login.'}), 400
    hashed_password = generate_password_hash(password)

    if not user_exists:
        new_user = Users(name=fullName, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        token = jwt.encode({"id":new_user.id, 'exp':datetime.now(timezone.utc) + timedelta(hours=1)},app.config['SECRET_KEY'], algorithm="HS256")
        print(new_user)
    
    response = make_response(redirect(url_for('index_route')))
    response.set_cookie('jwt_token', token)
    return response


@app.post("/add-user")
def post_add_user():
    name = request.form["name"]
    capture_face(name)
    train_model()
    return make_response(redirect(url_for("dashboard")))
    

if __name__ == "__main__":
    app.run(debug=True)