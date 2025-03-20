# app.py
from flask import Flask
from models import db
from routes import main_blueprint

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///warehouse.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(main_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
