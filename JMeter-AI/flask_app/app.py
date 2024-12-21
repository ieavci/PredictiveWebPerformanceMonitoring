# app.py
import os
import sys
import pandas as pd
from flask import Flask, jsonify, render_template, request, redirect, url_for
from importlib.machinery import SourceFileLoader

# Set up project base directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

INPUTS_DIR = os.path.join(BASE_DIR, 'inputs')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')

# Ensure necessary directories exist
os.makedirs(INPUTS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Dynamically load modules
ai_input_generator = SourceFileLoader("ai_input_generator.input_generator", 
    os.path.join(BASE_DIR, "ai_input_generator", "input_generator.py")).load_module()
generate_dynamic_test_plan = ai_input_generator.generate_dynamic_test_plan

analyze_results = SourceFileLoader("analyze_results", 
    os.path.join(BASE_DIR, "ai_output_analyzer", "analyze_results.py")).load_module()
analyze_detailed_results = analyze_results.analyze_detailed_results

lstm_anomaly_detector = SourceFileLoader("lstm_anomaly_detector", 
    os.path.join(BASE_DIR, "ai_output_analyzer", "lstm_anomaly_detector.py")).load_module()
lstm_anomaly_detection = lstm_anomaly_detector.lstm_anomaly_detection

execute_test = SourceFileLoader("test_executor.execute_test", 
    os.path.join(BASE_DIR, "test_executor", "execute_test.py")).load_module()
run_jmeter_test = execute_test.run_jmeter_test

# Flask app setup
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

from ai_input_generator.generate_test_plan import create_test_plan

@app.route("/generate-test-plan", methods=["POST"])
def generate_test_plan():
    # Parametreleri alın
    user_count = request.form.get("user_count", 10)
    loop_count = request.form.get("loop_count", 1)
    base_url = request.form.get("base_url", "localhost")
    path = request.form.get("path", "/")

    # Test planını oluştur
    create_test_plan(user_count, loop_count, base_url, path)

    return jsonify({"message": "Test plan created successfully"}), 200

@app.route('/run-test', methods=['POST'])
def run_test():
    try:
        base_url = request.form['base_url']
        path = request.form['path']
        users = int(request.form['users'])
        loop_count = int(request.form['loop_count'])

        # Generate dynamic test plan
        test_plan_path = generate_dynamic_test_plan(base_url, path, users, loop_count)

        # Execute JMeter test
        results_path = os.path.join(OUTPUTS_DIR, 'results.csv')
        run_jmeter_test(test_plan_path, results_path)

        # Analyze results
        analyze_detailed_results(results_path, OUTPUTS_DIR, users, loop_count)

        return redirect(url_for('summary_results'))

    except Exception as e:
        return f"Error occurred: {e}", 500

@app.route('/error_results')
def error_results():
    try:
        # Load error results
        error_file = os.path.join(OUTPUTS_DIR, 'error_results.csv')
        
        # Check if the file exists
        if os.path.exists(error_file):
            error_data = pd.read_csv(error_file).to_dict(orient='records')
        else:
            error_data = []

        return render_template('error_results.html', error_data=error_data)
    
    except Exception as e:
        return f"Error occurred: {e}", 500


@app.route('/summary_results')
def summary_results():
    try:
        # Load summary and anomaly results
        results_file = os.path.join(OUTPUTS_DIR, 'results.csv')
        summary_file = os.path.join(OUTPUTS_DIR, 'summary_results.csv')

        summary_data = pd.read_csv(summary_file).to_dict(orient='records')
        lstm_anomalies, lstm_summary = lstm_anomaly_detection(results_file)

        return render_template(
            'summary_results.html',
            summary_data=summary_data,
            lstm_summary=lstm_summary
        )
    except Exception as e:
        return f"Error occurred: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
