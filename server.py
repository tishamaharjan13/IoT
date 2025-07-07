
import os
import shutil
from flask import Flask, flash,render_template, request, redirect, url_for, make_response, jsonify
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

import threading
import socket
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
import aiohttp
import subprocess

from functools import wraps
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from services.capture import capture_face
from services.training import train_model

app = Flask(__name__, template_folder="templates")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
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

class RecogUser(db.Model):
    __tablename__ = 'recogUser'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    folderPath = db.Column(db.String(100))

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
            current_user = Users.query.filter_by(id=data['id']).first()
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
    users = select(RecogUser)
    return render_template("users.html", fullName=current_user.name, users=db.session.scalars(users))

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

    token = jwt.encode({'id': user.id, 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},app.config['SECRET_KEY'], algorithm="HS256")

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
        flash('User already exists', 'error')
        return redirect(url_for("register_route"))

    hashed_password = generate_password_hash(password)

    if not user_exists:
        new_user = Users(name=fullName, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        token = jwt.encode({"id":new_user.id, 'exp':datetime.now(timezone.utc) + timedelta(hours=1)},app.config['SECRET_KEY'], algorithm="HS256")
    
    flash('User registered sucessfully', 'success')
    response = make_response(redirect(url_for('index_route')))
    response.set_cookie('jwt_token', token)
    return response


@app.post("/add-user")
def post_add_user():
    name = request.form["name"]
    recogUser_exists = RecogUser.query.filter_by(name=name).first() is not None
    if recogUser_exists:
        flash("User already in system", 'error')
        return redirect(url_for("dashboard"))
    user_folder = capture_face(name)
    train_model()
    if not recogUser_exists:
        new_recogUser = RecogUser(name=name, folderPath=user_folder)
        db.session.add(new_recogUser)
        db.session.commit()
    subprocess.run(["bash", "shell.sh"])
    flash("User registered into system successfully", 'success')
    return make_response(redirect(url_for("dashboard")))

@app.post("/remove-user")
def post_remove_user():
    name=request.form["name"]
    stmt = select(RecogUser).where(RecogUser.name == name)
    recogUser_exists = db.session.scalars(stmt).one()

    if not recogUser_exists:
        flash("User does not exists", "error")
        return redirect(url_for("dashboard"))
    db.session.delete(recogUser_exists)
    db.session.commit()

    dataset_path = 'dataset'
    user_folder = os.path.join(dataset_path, name)
    
    shutil.rmtree(user_folder)
    train_model()
    subprocess.run(["bash", "shell.sh"])
    flash("User removed successful", 'success')
    return make_response(redirect(url_for("dashboard")))

@app.get("/live-stream")
def get_live_stream():
    return render_template("live.html")

pc = None

@app.route("/connect", methods=["POST"])
def connect():
    async def run():
        global pc
        pc = RTCPeerConnection()

        # Dummy data channel to allow offer creation
        pc.createDataChannel("chat")

        @pc.on("track")
        def on_track(track):
            if track.kind == "video":
                print("🎥 Receiving video track...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(show_video(track))

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        async with aiohttp.ClientSession() as session:
            async with session.post("http://127.0.0.1:9991/offer", json={
                "offer": {
                    "sdp": pc.localDescription.sdp,
                    "type": pc.localDescription.type
                }
            }) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"❌ Server returned error {resp.status}: {text}")
                    return
                response = await resp.json()


        answer = RTCSessionDescription(sdp=response["answer"]["sdp"], type=response["answer"]["type"])
        await pc.setRemoteDescription(answer)

    def start_loop():
        asyncio.run(run())

    threading.Thread(target=start_loop).start()
    return jsonify({"status": "connected"})

async def show_video(track):
    while True:
        frame = await track.recv()
        img = frame.to_ndarray(format="bgr24")
        cv2.imshow("Live", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    app.run(debug=True)