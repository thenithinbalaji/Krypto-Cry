from flask import Flask, render_template
from threading import Thread
import requests
import os

# loading env variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception as err:
    print(err)

app = Flask(__name__)


@app.route("/")
def home():
    data = requests.get(str(os.getenv("coin_api"))).json()
    return render_template("index.html", data=data)


def run():
    app.run(host="0.0.0.0", port=8080)


def runserver():
    thd = Thread(target=run)
    thd.start()


if __name__ == "__main__":
    app.run()
