import subprocess
import os

def run_jmeter_test(test_plan_name="dynamic_test_plan.jmx", results_output_path=None):
    jmeter_path = "C:/Users/iavcc/Downloads/Programs/JMeter/apache-jmeter-5.6.3/bin/jmeter.bat"  # JMeter binary path
    inputs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'inputs')
    outputs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

    test_plan_path = os.path.join(inputs_dir, test_plan_name)
    if results_output_path is None:
        results_output_path = os.path.join(outputs_dir, 'results.csv')

    command = [
        jmeter_path,
        '-n',  # Non-GUI mode
        '-t', test_plan_path,  # Test plan file
        '-l', results_output_path  # Output results file
    ]
    subprocess.run(command, check=True)
