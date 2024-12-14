import random
import json

def generate_dynamic_test_plan(base_url, path):
    users = random.randint(10, 500)
    duration = random.randint(10, 60)  # Saniye cinsinden

    test_plan = {
        "base_url": base_url,
        "path": path,
        "users": users,
        "duration": duration,
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
