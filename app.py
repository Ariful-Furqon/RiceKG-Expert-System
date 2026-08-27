"""
Flask Web Application for Rice Pest and Disease Diagnostic Expert System.
"""

import os
import json
from flask import Flask, request, render_template, redirect, url_for
from model import predict_diseases

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index_page():
    """Renders the main diagnostic form."""
    return render_template("index.html")


@app.route('/result', methods=['GET', 'POST'])
def diagnose():
    """Handles symptom selection and executes ontology-based reasoning."""
    if request.method == 'POST':
        selected_symptoms = request.form.getlist('mycheckbox')
        print(f"[Diagnosis Request] Selected symptoms ({len(selected_symptoms)}):", selected_symptoms)
        diagnosed_results = predict_diseases(selected_symptoms)
        print(f"[Diagnosis Result] Inferred:", diagnosed_results)
        return render_template('result.html', penyakit=diagnosed_results)
    return redirect(url_for('index_page'))


@app.route("/about/")
def about():
    """Renders about page."""
    return render_template("about.html")


@app.route("/turtle")
def turtle():
    """Reference data endpoint."""
    data_path = os.path.join(BASE_DIR, 'static', 'data.json')
    data = []
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    return render_template("penyu.html", penyu=data)

    
if __name__ == "__main__":
    app.run(debug=True)