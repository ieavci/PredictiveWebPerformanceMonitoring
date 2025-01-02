# app.py
import csv
import os
import sys
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request, redirect, url_for
from importlib.machinery import SourceFileLoader
import plotly.express as px



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

update_summary_results = SourceFileLoader(
    "analyze_results.update_summary_results",
    os.path.join(BASE_DIR, "ai_output_analyzer", "analyze_results.py")
).load_module().update_summary_results


# Flask app setup   
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

from ai_input_generator.generate_test_plan import create_test_plan, update_jmx

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
        results_file = os.path.join(OUTPUTS_DIR, 'results.csv')
        summary_file = os.path.join(OUTPUTS_DIR, 'summary_results.csv')
        error_file = os.path.join(OUTPUTS_DIR, 'error_results.csv')

        # Parametrelerden loop_count alın
        loop_count = int(request.form.get("loop_count", 1))

        # Eğer dosyalar yoksa, gerekli başlıklarla oluştur
        pd.DataFrame(columns=[
            'timeStamp', 'elapsed', 'label', 'responseCode', 'responseMessage',
            'threadName', 'dataType', 'success', 'failureMessage', 'bytes',
            'sentBytes', 'grpThreads', 'allThreads', 'URL', 'Latency', 'IdleTime', 'Connect'
        ]).to_csv(results_file, index=False)

        if not os.path.exists(summary_file):
            pd.DataFrame(columns=[
                "Kullanıcı Sayısı", "Döngü Sayısı", "LSTM Anomali Sayısı",
                "LSTM Anomali Yüzdesi (%)", "Ortalama Yanıt Süresi (ms)",
                "Hata Oranı (%)", "Maksimum Yanıt Süresi (ms)", "Minimum Yanıt Süresi (ms)"
            ]).to_csv(summary_file, index=False)

        # JMeter testi çalıştır
        run_jmeter_test()

        # LSTM anomali tespiti
        lstm_anomalies, lstm_summary, plot_base64 = lstm_anomaly_detection(results_file)

        # Anomali sonuçlarını kaydet
        anomalies_file = os.path.join(OUTPUTS_DIR, 'anomalies.csv')
        lstm_anomalies.to_csv(anomalies_file, index=False)

        # Hatalı satırları filtrele ve `error_results.csv` dosyasına yaz
        print("Loading results.csv...")
        results_file = pd.read_csv(results_file)
        print(f"Results DataFrame:\n{results_file.head()}")

        error_codes = [
            400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418,
            421, 422, 423, 424, 425, 426, 427, 428, 429, 431, 444, 451, 499, 500, 501, 502, 503, 504, 505,
            506, 507, 508, 510, 511
        ]
        error_data = results_file[results_file['responseCode'].astype(int).isin(error_codes)]
        print(f"Filtered Error DataFrame:\n{error_data.head()}")

        error_data.to_csv(error_file, index=False)
        print(f"Error results written to {error_file}")

        # Summary results dosyasını güncelle
        update_summary_results(results_file, summary_file, loop_count)

        return redirect(url_for('summary_results'))
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"Error occurred: {e}", 500


@app.route('/update_test_plan', methods=['POST'])
def update_test_plan():
    try:
        # Kullanıcıdan gelen veriler
        base_url = request.form.get('base_url')
        path = request.form.get('path')
        users = int(request.form.get('users'))  # Varsayılan değer: 10
        loop_count = int(request.form.get('loop_count'))  # Varsayılan değer: 1

        # JMX dosyasını güncelle
        update_jmx(base_url, path, users, loop_count)

        # Testi çalıştır ve sonuçları analiz et
        results_file = os.path.join(OUTPUTS_DIR, 'results.csv')
        summary_file = os.path.join(OUTPUTS_DIR, 'summary_results.csv')

        # Gerekli dosyaları oluştur
        if not os.path.exists(results_file):
            pd.DataFrame(columns=[
                'timeStamp', 'elapsed', 'label', 'responseCode', 'responseMessage',
                'threadName', 'dataType', 'success', 'failureMessage', 'bytes',
                'sentBytes', 'grpThreads', 'allThreads', 'URL', 'Latency', 'IdleTime', 'Connect'
            ]).to_csv(results_file, index=False)

        if not os.path.exists(summary_file):
            pd.DataFrame(columns=[
                "Kullanıcı Sayısı", "Döngü Sayısı", "LSTM Anomali Sayısı",
                "LSTM Anomali Yüzdesi (%)", "Ortalama Yanıt Süresi (ms)",
                "Hata Oranı (%)", "Maksimum Yanıt Süresi (ms)", "Minimum Yanıt Süresi (ms)"
            ]).to_csv(summary_file, index=False)

        # JMeter testi çalıştır
        run_jmeter_test()

        # LSTM anomali tespiti
        lstm_anomalies, lstm_summary, plot_base64 = lstm_anomaly_detection(results_file)

        # Anomali sonuçlarını kaydet
        anomalies_file = os.path.join(OUTPUTS_DIR, 'anomalies.csv')
        lstm_anomalies.to_csv(anomalies_file, index=False)

        # Summary sonuçlarını güncelle (loop_count ekleniyor)
        update_summary_results(results_file, summary_file, loop_count)

        return redirect(url_for('summary_results'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    
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
    

@app.route('/anomalies_results')
def anomalie_results():
    try:
        # Load anomalie results
        anomalie_file = os.path.join(OUTPUTS_DIR, 'anomalies.csv')
        
        # Check if the file exists
        if os.path.exists(anomalie_file):
            anomalie_data = pd.read_csv(anomalie_file).to_dict(orient='records')
        else:
            anomalie_data = []

        return render_template('anomalies_results.html', anomalie_data=anomalie_data)
    
    except Exception as e:
        return f"Error occurred: {e}", 500


@app.route('/summary_results')
def summary_results():
    try:
        results_file_path = os.path.join(OUTPUTS_DIR, 'results.csv')
        summary_file_path = os.path.join(OUTPUTS_DIR, 'summary_results.csv')

        # Dosyaları yükleme
        results_file = pd.read_csv(results_file_path)
        summary_data = pd.read_csv(summary_file_path).to_dict(orient='records')

        # LSTM anomalileri ve özet verisini oluşturun
        lstm_anomalies, lstm_summary, plot_base64 = lstm_anomaly_detection(results_file_path)

        # Reconstruction errors ve threshold verisini JSON formatına dönüştürün
        reconstruction_errors = lstm_anomalies['reconstruction_error'].tolist()
        threshold = lstm_summary['Threshold Used']

        # Timestamp'leri dönüştürme
        results_file['timeStamp'] = pd.to_datetime(results_file['timeStamp'], unit='ms')

        # Response Time Distribution (Box Plot)
        response_time_fig = px.box(
            results_file, 
            x='label', 
            y='elapsed', 
            title='Response Time Distribution by Test',
            labels={'label': 'Test Name', 'elapsed': 'Response Time (ms)'},
            color='label'
        )

        # Success/Failure Count (Stacked Bar Chart)
        success_count = results_file.groupby(['label', 'success']).size().reset_index(name='count')
        success_failure_fig = px.bar(
            success_count, 
            x='label', 
            y='count', 
            color='success', 
            title='Success vs Failure Count by Test',
            labels={'label': 'Test Name', 'count': 'Count', 'success': 'Success'},
            barmode='stack'
        )

        # HTTP Response Code Distribution (Pie Chart)
        response_code_count = results_file['responseCode'].value_counts().reset_index()
        response_code_count.columns = ['responseCode', 'count']
        response_code_fig = px.pie(
            response_code_count, 
            names='responseCode', 
            values='count', 
            title='HTTP Response Code Distribution'
        )

        # Time Series Analysis of Success/Failure
        results_file['success_numeric'] = results_file['success'].astype(int)
        time_series_fig = px.line(
            results_file, 
            x='timeStamp', 
            y='success_numeric', 
            title='Time Series of Success (1) and Failure (0)',
            labels={'timeStamp': 'Timestamp', 'success_numeric': 'Success (1) / Failure (0)'},
            color='label'
        )
        # Line chart for Latency, IdleTime, Connect, and Elapsed time by Test
        multi_metric_fig = px.line(
        results_file, 
        x='timeStamp', 
        y=['Latency', 'IdleTime', 'Connect', 'elapsed'],  # Multiple y-values
        title='Latency, IdleTime, Connect, and Elapsed Time by Test',
        labels={'timeStamp': 'Timestamp'},
        color='label',
        line_shape='linear'
        )

        # Fonksiyona girdiğiniz Plotly figüründen JSON-uyumlu hale getirme
        def jsonify_figure(fig):
            fig_dict = fig.to_dict()
            # Verinin içindeki numpy.ndarray türündeki tüm değerleri listeye dönüştürün
            for trace in fig_dict.get('data', []):
                for key, value in trace.items():
                    if isinstance(value, np.ndarray):
                        trace[key] = value.tolist()
            for key, value in fig_dict.get('layout', {}).items():
                if isinstance(value, np.ndarray):
                    fig_dict['layout'][key] = value.tolist()
            return fig_dict

        # Kullanım
        response_time_html = jsonify_figure(response_time_fig)
        success_failure_html = jsonify_figure(success_failure_fig)
        response_code_html = jsonify_figure(response_code_fig)
        time_series_html = jsonify_figure(time_series_fig)
        multi_metric_html = jsonify_figure(multi_metric_fig)
        
        return render_template(
            'summary_results.html',
            summary_data=summary_data,
            lstm_summary=lstm_summary,
            reconstruction_errors=reconstruction_errors,
            threshold=threshold,
            response_time_boxplot=response_time_html,
            success_failure_bar_chart=success_failure_html,
            response_code_pie_chart=response_code_html,
            success_failure_time_series=time_series_html,
            multi_metric_chart=multi_metric_html 
        )
        
    except Exception as e:
        return f"Error occurred: {e}", 500




if __name__ == '__main__':
    app.run(debug=True)