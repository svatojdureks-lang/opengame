from flask import Flask, render_template
import csv
from csv import DictReader


app = Flask(__name__)

@app.route("/")
def index() -> list[dict]:
    games = []
    with open ("out/games.csv", "r", encoding="utf-8") as f:
        reader = DictReader(f, )
        for row in reader:
            games.append(row)
    return render_template("template.html")


if __name__ == "__main__":
    app.run(debug=True)