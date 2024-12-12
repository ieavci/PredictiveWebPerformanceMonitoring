import random
import json
import datetime

def generate_dynamic_test_plan():
    users = random.randint(10, 500)
    duration = random.randint(10, 60)  # Saniye cinsinden
    endpoints = ["/", "/butik/liste/1/kadin", "/butik/liste/16/supermarket"]
    http_methods = ["GET", "POST", "PUT", "DELETE"]

    test_plan = {
        "users": users,
        "duration": duration,
        "requests": [
            {
                "endpoint": random.choice(endpoints),
                "method": random.choice(http_methods),
                "params": {"id": random.randint(1, 1000)},
            }
            for _ in range(users)
        ],
        "timestamp": datetime.datetime.now().isoformat(),
    }
    return test_plan

if __name__ == "__main__":
    test_plan = generate_dynamic_test_plan()

    with open('../inputs/dynamic_test_plan.json', 'w') as f:
        json.dump(test_plan, f, indent=4)

    print("Dinamik test planı oluşturuldu:", test_plan)
