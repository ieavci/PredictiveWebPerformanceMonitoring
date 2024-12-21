import os
from .generate_test_plan import create_test_plan

def generate_dynamic_test_plan(base_url, path, user_count, loop_count):
    test_plan_file = os.path.join(os.path.dirname(__file__), '../inputs/dynamic_test_plan.jmx')
    create_test_plan(user_count, loop_count, base_url, path, output_file=test_plan_file)
    return test_plan_file
