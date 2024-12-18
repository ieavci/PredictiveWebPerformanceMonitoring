import random
import json

def generate_dynamic_test_plan(base_url, path, users, loop_count):
    test_plan = {
        "base_url": base_url,
        "path": path,
        "users": users,
        "loop_count": loop_count,
        "requests": [
            {
                "url": f"{base_url}{path}",
                "method": "GET",
                "params": {"id": random.randint(1, 1000)},
            }
            for _ in range(users)
        ],
    }
    return json.dumps(test_plan, indent=4)

