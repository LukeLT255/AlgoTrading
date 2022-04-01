from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import gunicorn

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://idfgpxivkpzxxy:73f3fe559854c44dfbd33a1f5e82b5b0a49db5acf65e8889bbff47b48b0e79a3@ec2-54-173-77-184.compute-1.amazonaws.com:5432/dgg38c6arqqie'
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


