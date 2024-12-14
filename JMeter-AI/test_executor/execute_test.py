import subprocess
import sys
import os

# Proje kök dizinini belirle
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)


def run_jmeter_test(input_file, output_file):
    # Sabit test planı dosyasının tam yolu
    test_plan_path = os.path.abspath("C:/Users/iavcc/Desktop/Online Dersler/Kalite Güvencesi ve Testi/JMeter-AI/inputs/test_plan.jmx")

    # Mutlak yolları kullan
    input_file = os.path.abspath(input_file)
    output_file = os.path.abspath(output_file)

    jmeter_command = [
        "C:/Users/iavcc/Downloads/Programs/JMeter/apache-jmeter-5.6.3/bin/jmeter.bat",
        "-n",
        "-t",  # JMeter test planı
        test_plan_path,
        "-l",  # Test sonuçlarının kaydedileceği CSV dosyası
        output_file,
        "-Jinput_file=" + input_file,
    ]

    # Komutu çalıştır (cwd parametresi ile çalışma dizinini ayarla)
    subprocess.run(jmeter_command, cwd=BASE_DIR, check=True)
