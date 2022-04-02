from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import gunicorn
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
db = SQLAlchemy(app)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Current value: {self.value} - Current time: {self.time}"


@app.route('/')
def index():
    return "hullooooo"

@app.route('/account')
def get_all_values():
    values = Account.query.all()

    output = []
    for value in values:
        value_data = {'value': value.value, 'time': value.time}

        output.append(value_data)

    return {"values": output}


