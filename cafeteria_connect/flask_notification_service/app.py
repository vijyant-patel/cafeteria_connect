from flask import Flask
from routes.notify import notify_bp

app = Flask(__name__)
app.register_blueprint(notify_bp, url_prefix="/notify")

if __name__ == "__main__":
    print("sdf")
    app.run(port=5002, debug=True)
