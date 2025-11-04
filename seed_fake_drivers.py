from app import create_app, db
from models import User, Driver

def seed_fake_drivers():
    # Data for fake drivers
    fake_drivers = [
        {"firstname": "John", "lastname": "Dlamini", "phone": "0781000001", "license_number": "LIC1001"},
        {"firstname": "Lerato", "lastname": "Mkhize", "phone": "0781000002", "license_number": "LIC1002"},
        {"firstname": "Thabo", "lastname": "Nkosi", "phone": "0781000003", "license_number": "LIC1003"},
        {"firstname": "Nomsa", "lastname": "Khumalo", "phone": "0781000004", "license_number": "LIC1004"},
        {"firstname": "Sipho", "lastname": "Zungu", "phone": "0781000005", "license_number": "LIC1005"},
    ]

    for d in fake_drivers:
        # Check if user already exists
        existing_user = User.query.filter_by(phone=d["phone"]).first()
        if existing_user:
            print(f"Skipping {d['firstname']} {d['lastname']} (already exists)")
            continue

        # Create User first
        user = User(
            firstname=d["firstname"],
            lastname=d["lastname"],
            phone=d["phone"],
            role="driver"
        )
        db.session.add(user)
        db.session.flush()  # assign user.id

        # Create Driver linked to user
        driver = Driver(
            user_id=user.id,
            license_number=d["license_number"]
        )
        db.session.add(driver)

    db.session.commit()
    print("✅ Fake drivers seeded successfully!")

if __name__ == "__main__":
    app = create_app()  # your app factory
    with app.app_context():
        seed_fake_drivers()
