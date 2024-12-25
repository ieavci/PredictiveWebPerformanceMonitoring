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

        # Summary results dosyasını güncelle
        update_summary_results(results_file, summary_file, loop_count)

        return redirect(url_for('summary_results'))
    except Exception as e:
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
        results_file = os.path.join(OUTPUTS_DIR, 'results.csv')
        summary_file = os.path.join(OUTPUTS_DIR, 'summary_results.csv')

        # summary_results.csv'yi yükleyin
        summary_data = pd.read_csv(summary_file).to_dict(orient='records')

        # LSTM anomalileri ve özet verisini oluşturun
        lstm_anomalies, lstm_summary, plot_base64 = lstm_anomaly_detection(results_file)

        # Reconstruction errors ve threshold verisini JSON formatına dönüştürün
        reconstruction_errors = lstm_anomalies['reconstruction_error'].tolist()
        threshold = lstm_summary['Threshold Used']

        return render_template(
            'summary_results.html',
            summary_data=summary_data,
            lstm_summary=lstm_summary,
            reconstruction_errors=reconstruction_errors,
            threshold=threshold
        )
    except Exception as e:
        return f"Error occurred: {e}", 500




if __name__ == '__main__':
    app.run(debug=True)
