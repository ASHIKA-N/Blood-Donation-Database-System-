from flask import Flask, render_template, request, redirect, url_for
import oracledb

# --------------------------------------------------------
# 🔹 ORACLE CONNECTION
# --------------------------------------------------------
oracledb.init_oracle_client(lib_dir=None)

app = Flask(__name__, template_folder="../front")
app.static_folder = "../front"

def get_db_connection():
    conn = oracledb.connect(
        user="root",
        password="Gt650101",
        dsn="localhost:1521/XEPDB1"
    )
    return conn


# --------------------------------------------------------
# 🔹 INDEX PAGE
# --------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------------
# 🔹 ROLE HANDLER
# --------------------------------------------------------
@app.route("/select_role", methods=["POST"])
def select_role():
    role = request.form.get("role")
    routes = {
        "donor": "donor_dashboard",
        "bloodbank": "bloodbank_dashboard",
        "hospital": "hospital_dashboard",
        "customer": "customer_dashboard",
        "admin": "admin_dashboard",
        "foundation": "foundation_dashboard",
    }
    return redirect(url_for(routes.get(role, "index")))


# --------------------------------------------------------
# 🔹 DONOR DASHBOARD (ADD + VIEW)
# --------------------------------------------------------
@app.route("/donor", methods=["GET", "POST"])
def donor_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form.get("D_name")
        contact = request.form.get("D_contact")
        address = request.form.get("D_address")
        age = request.form.get("D_age")
        gender = request.form.get("D_gender")
        bb_id = request.form.get("BB3_id")

        try:
            cursor.execute("""
                INSERT INTO Donor (D_name, D_contact, D_address, D_age, D_gender, D_history, BB3_id)
                VALUES (:1, :2, :3, :4, :5, 0, :6)
            """, (name, contact, address, age, gender, bb_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error adding donor: {e}</h3>"

    cursor.execute("SELECT * FROM Donor ORDER BY D_id")
    donors = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("donor.html", donors=donors)


# --------------------------------------------------------
# 🔹 CUSTOMER DASHBOARD (ADD + VIEW)
# --------------------------------------------------------
@app.route("/customer", methods=["GET", "POST"])
def customer_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form.get("C_name")
        address = request.form.get("C_address")
        contact = request.form.get("C_contact")
        gender = request.form.get("C_gender")
        history = request.form.get("C_history")

        try:
            cursor.execute("""
                INSERT INTO Customer (C_name, C_address, C_contact, C_gender, C_history)
                VALUES (:1, :2, :3, :4, :5)
            """, (name, address, contact, gender, history))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error adding customer: {e}</h3>"

    cursor.execute("SELECT * FROM Customer ORDER BY C_id")
    customers = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("customer.html", customers=customers)


# --------------------------------------------------------
# 🔹 HOSPITAL DASHBOARD (ADD + VIEW)
# --------------------------------------------------------
@app.route("/hospital", methods=["GET", "POST"])
def hospital_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form.get("Hs_name")
        address = request.form.get("Hs_address")
        contact = request.form.get("Hs_contact")
        foundation_id = request.form.get("F1_id")

        try:
            cursor.execute("""
                INSERT INTO Hospital (Hs_name, Hs_address, Hs_contact, F1_id)
                VALUES (:1, :2, :3, :4)
            """, (name, address, contact, foundation_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error adding hospital: {e}</h3>"

    cursor.execute("SELECT * FROM Hospital ORDER BY Hs_id")
    hospitals = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("hospital.html", hospitals=hospitals)


# --------------------------------------------------------
# 🔹 BLOOD BANK DASHBOARD (ADD + VIEW)
# --------------------------------------------------------
@app.route("/bloodbank", methods=["GET", "POST"])
def bloodbank_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form.get("BB_name")
        address = request.form.get("BB_address")
        contact = request.form.get("BB_contact")
        volume = request.form.get("BB_volume")
        btype = request.form.get("BB_type")
        foundation_id = request.form.get("F2_id")

        try:
            cursor.execute("""
                INSERT INTO Bloodbank (BB_name, BB_address, BB_contact, BB_volume, BB_type, F2_id)
                VALUES (:1, :2, :3, :4, :5, :6)
            """, (name, address, contact, volume, btype, foundation_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error adding blood bank: {e}</h3>"

    cursor.execute("SELECT * FROM Bloodbank ORDER BY BB_id")
    banks = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("bloodbank.html", banks=banks)


# --------------------------------------------------------
# 🔹 FOUNDATION DASHBOARD (VIEW ALL + RELATIONS)
# --------------------------------------------------------
@app.route("/foundation", methods=["GET", "POST"])
def foundation_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Add new foundation
    if request.method == "POST":
        name = request.form.get("F_name")
        address = request.form.get("F_address")
        contact = request.form.get("F_contact")
        email = request.form.get("F_mail_id")

        try:
            cursor.execute("""
                INSERT INTO Foundation (F_name, F_address, F_contact, F_mail_id)
                VALUES (:1, :2, :3, :4)
            """, (name, address, contact, email))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error adding foundation: {e}</h3>"

    # Fetch all foundations
    cursor.execute("SELECT * FROM Foundation ORDER BY F_id")
    foundations = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

    # Fetch hospitals linked to foundations
    cursor.execute("SELECT * FROM Hospital WHERE F1_id IS NOT NULL ORDER BY F1_id")
    hospitals = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

    # Fetch blood banks linked to foundations
    cursor.execute("SELECT * FROM Bloodbank WHERE F2_id IS NOT NULL ORDER BY F2_id")
    banks = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("foundation.html", foundations=foundations, hospitals=hospitals, banks=banks)


# --------------------------------------------------------
# 🔹 ADMIN DASHBOARD
# --------------------------------------------------------
@app.route("/admin")
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {}
    tables = ["Foundation", "Hospital", "Donor", "Bloodbank", "Customer"]
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        stats[t] = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return render_template("admin.html", stats=stats)


# --------------------------------------------------------
# 🔹 RUN APP
# --------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
