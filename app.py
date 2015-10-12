from flask import Flask, render_template, request, redirect
import os
import time
import WMATAWatcher as ww
import dill
from sklearn.ensemble import RandomForestClassifier

with open('wwEst100815.pkl', 'r') as f:
    wwEst = dill.load(f)

with open('wwEst100815_notweets.pkl', 'r') as f:
    wwEst_notweets = dill.load(f)

app = Flask(__name__)


@app.route("/")
def main_page():
    #  As currently written, will perform a search on targeted
    #  search terms, produce a feature array, and supply it
    #  to a trained Random Forest.
    app.timestring, app.test = ww.produce_test_data()
    if app.test[6] == 0:
        app.pred = wwEst_notweets.predict(app.test)
    else:
        app.pred = wwEst.predict(app.test)
    if app.pred == 1:
        app.prediction = 'DELAY LIKELY'
        app.color = 'ff6d6d'
    else:
        app.prediction = 'NO DELAY DETECTED'
        app.color = '6dff70'
    return render_template('index.html', timestring=app.timestring,
                           prediction=app.prediction, color=app.color)

if __name__ == "__main__":
    # taken verbatim from:
    # http://virantha.com/2013/11/14/starting-a-simple-flask-app-with-heroku/
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
