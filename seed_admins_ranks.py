from datetime import datetime
from models import User, Admin, Rank, db
from app import create_app   # ✅ added import for create_app

def seed():
    # Clear existing admin/rank data (optional)
    Admin.query.delete()
    Rank.query.delete()
    User.query.filter(User.role == 'admin').delete()
    db.session.commit()

    # 1) Create admin users + admin profiles
    admins_data = [
        {'firstname': 'Sipho',     'lastname': 'Mkhize',    'phone': '0821000001'},
        {'firstname': 'Thandi',    'lastname': 'Zulu',      'phone': '0821000002'},
        {'firstname': 'Lungelo',   'lastname': 'Ndaba',     'phone': '0821000003'},
        {'firstname': 'Nomsa',     'lastname': 'Dlamini',   'phone': '0821000004'},
        {'firstname': 'Jabulani',  'lastname': 'Gwala',     'phone': '0821000005'},
        {'firstname': 'Zinhle',    'lastname': 'Mthembu',   'phone': '0821000006'},
        {'firstname': 'Phumlani',  'lastname': 'Mkhwanazi', 'phone': '0821000007'},
        {'firstname': 'Bongi',     'lastname': 'Sithole',   'phone': '0821000008'},
        {'firstname': 'Kwanele',   'lastname': 'Dube',      'phone': '0821000009'},
        {'firstname': 'Nosipho',   'lastname': 'Magwaza',   'phone': '0821000010'},
        {'firstname': 'Shainan',   'lastname': 'Pillay',    'phone': '0821000011'},
        {'firstname': 'Mbuso',     'lastname': 'Nkalanga',  'phone': '0821000012'},
    ]

    admin_objs = []
    for data in admins_data:
        user = User(
            firstname = data['firstname'],
            lastname  = data['lastname'],
            phone     = data['phone'],
            role      = 'admin',
            created_at= datetime.utcnow()
        )
        db.session.add(user)
        db.session.flush()

        admin = Admin(
            user_id = user.id
        )
        db.session.add(admin)
        db.session.flush()

        admin_objs.append(admin)

    # 2) Create ranks associated with each admin; leave destinations empty for now
    ranks_data = [
        {
            'name':     "Cartwright Taxi Rank",
            'address':  "Beatrice St, Durban Central, Durban, 4025",
            'city':      "Durban",
            'province':  "KwaZulu-Natal",
            'latitude': -29.85194,
            'longitude':31.01892,
            'max_capacity':1000,
            'admin':    admin_objs[0]
        },
        {
            'name':     "Klaarwater Taxi Rank",
            'address':  "1-5 Stanfield Ln, Pinetown CBD, Pinetown, 3620",
            'city':      "Pinetown",
            'province':  "KwaZulu-Natal",
            'latitude': -29.81352,
            'longitude':30.85440,
            'max_capacity':1000,
            'admin':    admin_objs[1]
        },
        {
            'name':     "Gateway Mall Taxi Rank",
            'address':  "Rnk152 Gateway Theatre of Shopping, 1 Palm Blvd, Umhlanga Ridge, uMhlanga, 4319",
            'city':      "uMhlanga Ridge",
            'province':  "KwaZulu-Natal",
            'latitude': -29.7270365,
            'longitude':31.0634261,
            'max_capacity':1000,
            'admin':    admin_objs[2]
        },
        {
            'name':     "Chatsworth Centre Taxi Rank",
            'address':  "R K Khan Cir, Chatsworth, 4092",
            'city':      "Chatsworth",
            'province':  "KwaZulu-Natal",
            'latitude': -29.9126673,
            'longitude':30.8797731,
            'max_capacity':1000,
            'admin':    admin_objs[3]
        },
        {
            'name':     "Ballito Taxis",
            'address':  "Shop 204, Ballito Junction Regional Mall, Ballito Dr, oThongathi, 4420",
            'city':      "Ballito",
            'province':  "KwaZulu-Natal",
            'latitude': -29.5226337,
            'longitude':31.1999831,
            'max_capacity':10,
            'admin':    admin_objs[4]
        },
        {
            'name':     "Richards Bay Taxi Rank",
            'address':  "Richards Bay Central, Richards Bay, 3900",
            'city':      "Richards Bay",
            'province':  "KwaZulu-Natal",
            'latitude': -28.74908,
            'longitude': 32.0445639,
            'max_capacity':1000,
            'admin':    admin_objs[5]
        },
        {
            'name':     "Esigingqini Taxi Rank",
            'address':  "Milner Estate Lennox Estate & Pan, East London, 5201",
            'city':      "East London",
            'province':  "Eastern Cape",
            'latitude': -32.9906639,
            'longitude':27.6351423,
            'max_capacity':1000,
            'admin':    admin_objs[6]
        },
        {
            'name':     "uMnambithi Taxi Rank",
            'address':  "17 Queen St, uMnambithi, 3370",
            'city':      "uMnambithi",
            'province':  "KwaZulu-Natal",
            'latitude': -28.561595,
            'longitude':29.7804104,
            'max_capacity':1500,
            'admin':    admin_objs[7]
        },
        {
            'name':     "Market Square Taxi Rank",
            'address':  "Church St, Pietermaritzburg, 3201",
            'city':      "Pietermaritzburg",
            'province':  "KwaZulu-Natal",
            'latitude': -29.5997373,
            'longitude':30.3814918,
            'max_capacity':18,
            'admin':    admin_objs[8]
        },
        {
            'name':     "MTN Rank",
            'address':  "16-2 Martin St, Selby, Johannesburg, 2001",
            'city':      "Johannesburg",
            'province':  "Gauteng",
            'latitude': -26.2115258,
            'longitude':28.0352905,
            'max_capacity':2500,
            'admin':    admin_objs[9]
        },
        {
            'name':     "Market Durban",
            'address':  "Market Rd, Greyville, Berea, 4001",
            'city':      "Durban",
            'province':  "KwaZulu-Natal",
            'latitude': -29.8597464,
            'longitude':31.0112912,
            'max_capacity':2500,
            'admin':    admin_objs[10]
        },
        {
            'name':     "eMalahleni Long Distance Taxi Rank",
            'address':  "Main St, eMalahleni, 1035",
            'city':      "eMalahleni",
            'province':  "Mpumalanga",
            'latitude': -25.8765149,
            'longitude':29.2049209,
            'max_capacity':1000,
            'admin':    admin_objs[11]
        },
    ]

    for rd in ranks_data:
        rank = Rank(
            name        = rd['name'],
            address     = rd['address'],
            city        = rd['city'],
            province    = rd['province'],
            latitude    = rd['latitude'],
            longitude   = rd['longitude'],
            max_capacity= rd['max_capacity'],
            created_at  = datetime.utcnow(),
            admin_id    = rd['admin'].id
        )
        db.session.add(rank)

    db.session.commit()
    print("Seeded admins and ranks.")

if __name__ == "__main__":
    app = create_app()  # this must import your Flask app factory
    with app.app_context():
        seed()
