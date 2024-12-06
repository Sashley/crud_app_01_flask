from app import app

with app.test_request_context():
    print("\nRegistered URL rules:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
