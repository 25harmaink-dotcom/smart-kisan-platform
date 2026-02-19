import sqlite3
import os

DB_PATH = "smart_kisan.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Users / Farmers
    c.execute("""
    CREATE TABLE IF NOT EXISTS farmers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        state TEXT,
        district TEXT,
        password_hash TEXT NOT NULL,
        crop_type TEXT,
        area_size REAL,
        soil_type TEXT,
        water_source TEXT,
        farmer_category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Admins
    c.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        last_login TIMESTAMP
    )
    """)

    # Schemes
    c.execute("""
    CREATE TABLE IF NOT EXISTS schemes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        benefits TEXT,
        eligible_states TEXT,
        eligible_crops TEXT,
        eligible_categories TEXT,
        department TEXT,
        adoption_count INTEGER DEFAULT 0,
        rating REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Complaints
    c.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE NOT NULL,
        farmer_id INTEGER,
        farmer_name TEXT,
        state TEXT,
        district TEXT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        image_path TEXT,
        priority TEXT DEFAULT 'Medium',
        department TEXT,
        status TEXT DEFAULT 'Submitted',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES farmers(id)
    )
    """)

    # Admin logs
    c.execute("""
    CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_username TEXT,
        action TEXT,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Scheme adoptions
    c.execute("""
    CREATE TABLE IF NOT EXISTS scheme_adoptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id INTEGER,
        farmer_id INTEGER,
        adopted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rating INTEGER,
        FOREIGN KEY (scheme_id) REFERENCES schemes(id),
        FOREIGN KEY (farmer_id) REFERENCES farmers(id)
    )
    """)

    conn.commit()

    # Seed default admin
    import bcrypt
    admin_hash = bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode()
    c.execute("INSERT OR IGNORE INTO admins (username, password_hash) VALUES (?, ?)", ("admin", admin_hash))

    # Seed sample schemes if empty
    c.execute("SELECT COUNT(*) FROM schemes")
    count = c.fetchone()[0]
    if count == 0:
        sample_schemes = [
            ("PM-KUSUM", "Solar pump scheme for farmers", "50% subsidy on solar pumps, free electricity for 8 hours/day",
             "All", "All", "All", "Ministry of New & Renewable Energy", 4520, 4.3),
            ("Pradhan Mantri Krishi Sinchayee Yojana", "Har Khet Ko Pani - water to every farm",
             "Drip/sprinkler subsidy up to 55%, irrigation infrastructure support",
             "All", "All", "All", "Ministry of Agriculture", 8900, 4.5),
            ("Micro Irrigation Fund", "Fund for promoting micro irrigation",
             "Low interest loans for drip and sprinkler irrigation systems",
             "All", "All", "Small,Marginal", "NABARD", 2100, 4.1),
            ("Rajasthan Mukhyamantri Jal Swavlamban Abhiyan", "Water self-sufficiency scheme",
             "Water harvesting structures, farm ponds, check dams",
             "Rajasthan", "All", "All", "Rajasthan Govt", 1500, 4.0),
            ("National Mission for Sustainable Agriculture", "Climate resilient agriculture",
             "Training, soil health card, organic farming support",
             "All", "Wheat,Rice,Cotton,Sugarcane", "All", "Ministry of Agriculture", 3200, 4.2),
            ("Rythu Bandhu (Telangana)", "Investment support for farmers",
             "Rs 5000/acre per season direct benefit transfer",
             "Telangana", "All", "All", "Telangana Govt", 5100, 4.6),
            ("Kisan Credit Card", "Credit facility for agricultural needs",
             "Up to Rs 3 lakh credit at 4% interest rate",
             "All", "All", "All", "Ministry of Finance", 7800, 4.4),
            ("Soil Health Card Scheme", "Soil testing and health monitoring",
             "Free soil testing, customized fertilizer recommendations",
             "All", "All", "All", "Ministry of Agriculture", 6400, 4.2),
            ("Fasal Bima Yojana", "Crop insurance scheme",
             "Premium as low as 1.5-5%, coverage for crop loss",
             "All", "All", "All", "Ministry of Agriculture", 9200, 4.0),
            ("e-NAM", "Online agriculture market",
             "Access to national market, better price discovery, direct selling",
             "All", "All", "All", "Ministry of Agriculture", 4100, 3.9),
        ]
        for s in sample_schemes:
            c.execute("""INSERT INTO schemes (name, description, benefits, eligible_states, eligible_crops,
                         eligible_categories, department, adoption_count, rating) VALUES (?,?,?,?,?,?,?,?,?)""", s)

    conn.commit()
    conn.close()

# ---- CRUD helpers ----

def get_all_farmers():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM farmers ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_farmer_by_phone(phone):
    conn = get_conn()
    row = conn.execute("SELECT * FROM farmers WHERE phone=?", (phone,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_farmer_by_id(fid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM farmers WHERE id=?", (fid,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_farmer_profile(fid, data):
    conn = get_conn()
    conn.execute("""UPDATE farmers SET crop_type=?, area_size=?, soil_type=?, water_source=?,
                    farmer_category=?, state=?, district=? WHERE id=?""",
                 (data['crop_type'], data['area_size'], data['soil_type'],
                  data['water_source'], data['farmer_category'], data['state'], data['district'], fid))
    conn.commit()
    conn.close()

def create_farmer(name, phone, state, district, password_hash):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO farmers (name, phone, state, district, password_hash) VALUES (?,?,?,?,?)",
                     (name, phone, state, district, password_hash))
        conn.commit()
        fid = conn.execute("SELECT id FROM farmers WHERE phone=?", (phone,)).fetchone()[0]
        conn.close()
        return fid
    except Exception as e:
        conn.close()
        raise e

def get_all_schemes():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM schemes ORDER BY adoption_count DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_matching_schemes(state, crop, category):
    schemes = get_all_schemes()
    matched = []
    for s in schemes:
        state_ok = s['eligible_states'] == 'All' or state in (s['eligible_states'] or '').split(',')
        crop_ok = s['eligible_crops'] == 'All' or crop in (s['eligible_crops'] or '').split(',')
        cat_ok = s['eligible_categories'] == 'All' or category in (s['eligible_categories'] or '').split(',')
        if state_ok and crop_ok and cat_ok:
            matched.append(s)
    return matched

def add_scheme(data):
    conn = get_conn()
    conn.execute("""INSERT INTO schemes (name, description, benefits, eligible_states, eligible_crops,
                    eligible_categories, department) VALUES (?,?,?,?,?,?,?)""",
                 (data['name'], data['description'], data['benefits'], data['eligible_states'],
                  data['eligible_crops'], data['eligible_categories'], data['department']))
    conn.commit()
    conn.close()

def update_scheme(sid, data):
    conn = get_conn()
    conn.execute("""UPDATE schemes SET name=?, description=?, benefits=?, eligible_states=?,
                    eligible_crops=?, eligible_categories=?, department=? WHERE id=?""",
                 (data['name'], data['description'], data['benefits'], data['eligible_states'],
                  data['eligible_crops'], data['eligible_categories'], data['department'], sid))
    conn.commit()
    conn.close()

def delete_scheme(sid):
    conn = get_conn()
    conn.execute("DELETE FROM schemes WHERE id=?", (sid,))
    conn.commit()
    conn.close()

def create_complaint(farmer_id, farmer_name, state, district, title, description, priority, department, image_path=None):
    import uuid, datetime
    complaint_id = "CMP-" + str(uuid.uuid4())[:8].upper()
    conn = get_conn()
    conn.execute("""INSERT INTO complaints (complaint_id, farmer_id, farmer_name, state, district,
                    title, description, image_path, priority, department, status) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                 (complaint_id, farmer_id, farmer_name, state, district, title, description,
                  image_path, priority, department, 'Submitted'))
    conn.commit()
    conn.close()
    return complaint_id

def get_complaints_by_farmer(farmer_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM complaints WHERE farmer_id=? ORDER BY created_at DESC", (farmer_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_complaints():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM complaints ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_complaint_status(complaint_id, status, department=None):
    conn = get_conn()
    if department:
        conn.execute("UPDATE complaints SET status=?, department=?, updated_at=CURRENT_TIMESTAMP WHERE complaint_id=?",
                     (status, department, complaint_id))
    else:
        conn.execute("UPDATE complaints SET status=?, updated_at=CURRENT_TIMESTAMP WHERE complaint_id=?",
                     (status, complaint_id))
    conn.commit()
    conn.close()

def get_admin_by_username(username):
    conn = get_conn()
    row = conn.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

def log_admin_action(username, action, details=""):
    conn = get_conn()
    conn.execute("INSERT INTO admin_logs (admin_username, action, details) VALUES (?,?,?)",
                 (username, action, details))
    conn.commit()
    conn.close()

def get_admin_logs():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM admin_logs ORDER BY timestamp DESC LIMIT 100").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def adopt_scheme(scheme_id, farmer_id, rating=None):
    conn = get_conn()
    # Check if already adopted
    exists = conn.execute("SELECT id FROM scheme_adoptions WHERE scheme_id=? AND farmer_id=?",
                          (scheme_id, farmer_id)).fetchone()
    if not exists:
        conn.execute("INSERT INTO scheme_adoptions (scheme_id, farmer_id, rating) VALUES (?,?,?)",
                     (scheme_id, farmer_id, rating))
        conn.execute("UPDATE schemes SET adoption_count = adoption_count + 1 WHERE id=?", (scheme_id,))
        conn.commit()
    conn.close()

def get_stats():
    conn = get_conn()
    stats = {}
    stats['total_farmers'] = conn.execute("SELECT COUNT(*) FROM farmers").fetchone()[0]
    stats['total_complaints'] = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    stats['resolved_complaints'] = conn.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'").fetchone()[0]
    stats['total_schemes'] = conn.execute("SELECT COUNT(*) FROM schemes").fetchone()[0]
    stats['total_adoptions'] = conn.execute("SELECT SUM(adoption_count) FROM schemes").fetchone()[0] or 0
    stats['high_priority'] = conn.execute("SELECT COUNT(*) FROM complaints WHERE priority='High'").fetchone()[0]
    conn.close()
    return stats

def get_complaint_by_states():
    conn = get_conn()
    rows = conn.execute("SELECT state, COUNT(*) as count FROM complaints GROUP BY state").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_scheme_adoption_trend():
    conn = get_conn()
    rows = conn.execute("""SELECT s.name, s.adoption_count FROM schemes s ORDER BY s.adoption_count DESC LIMIT 8""").fetchall()
    conn.close()
    return [dict(r) for r in rows]
