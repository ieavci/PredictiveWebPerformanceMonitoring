
import sys
import os

# Proje kök dizinini belirle
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

from flask import Flask, render_template, request, redirect, url_for
#from ai_input_generator.input_generator import generate_dynamic_test_plan
#from test_executor.execute_test import run_jmeter_test
from ai_output_analyzer.analyze_results import analyze_detailed_results


INPUTS_DIR = os.path.join(BASE_DIR, 'inputs')
#OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
OUTPUTS_DIR = os.path.abspath(os.path.join(BASE_DIR, 'outputs'))



if not os.path.exists(OUTPUTS_DIR):
    print(f"OUTPUTS_DIR dizini oluşturulamadı: {OUTPUTS_DIR}")

print(f"OUTPUTS_DIR: {OUTPUTS_DIR}")
print(f"Çalışma dizini: {os.getcwd()}")



from importlib.machinery import SourceFileLoader

input_generator = SourceFileLoader("ai_input_generator.input_generator", 
    os.path.join(BASE_DIR, "ai_input_generator", "input_generator.py")).load_module()
generate_dynamic_test_plan = input_generator.generate_dynamic_test_plan

# ai_input_generator içe aktarma
ai_input_generator = SourceFileLoader("ai_input_generator.input_generator", 
    os.path.join(BASE_DIR, "ai_input_generator", "input_generator.py")).load_module()
generate_dynamic_test_plan = ai_input_generator.generate_dynamic_test_plan

# test_executor içe aktarma
test_executor = SourceFileLoader("test_executor.execute_test", 
    os.path.join(BASE_DIR, "test_executor", "execute_test.py")).load_module()
run_jmeter_test = test_executor.run_jmeter_test


# Gerekli klasörleri oluştur
os.makedirs(INPUTS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-test', methods=['POST'])
def run_test():
    base_url = request.form['base_url']
    path = request.form['path']

    # Dinamik test girdisi oluştur
    test_plan = generate_dynamic_test_plan(base_url, path)

    # Test girdisini kaydet
    input_path = os.path.join(INPUTS_DIR, 'dynamic_test_plan.json')
    with open(input_path, 'w') as f:
        f.write(test_plan)

    # JMeter testi çalıştır
    output_path = os.path.abspath(os.path.join(OUTPUTS_DIR, 'results.csv'))
    run_jmeter_test(input_path, output_path)

    # Çıktıyı analiz et
    results = analyze_detailed_results(output_path, OUTPUTS_DIR)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
