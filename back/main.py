from flask import Flask, render_template, request, redirect, url_for
import oracledb
import os

# --------------------------------------------------------
# 🔹 ORACLE CONFIGURATION (Thin Mode)
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
# 🔹 INDEX PAGE (ROLE SELECTION)
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
# 🔹 LOGIN PAGE
# --------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        role_map = {
            "donor": "donor_dashboard",
            "hospital": "hospital_dashboard",
            "bloodbank": "bloodbank_dashboard",
            "foundation": "foundation_dashboard",
            "customer": "customer_dashboard",
            "admin": "admin_dashboard",
        }
        return redirect(url_for(role_map.get(role, "index")))
    return render_template("login.html")


# --------------------------------------------------------
# 🔹 DONOR DASHBOARD (VIEW + ADD)
# --------------------------------------------------------
@app.route("/donor", methods=["GET", "POST"])
def donor_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🩸 Add new donor
    if request.method == "POST":
        name = request.form.get("D_name")
        contact = request.form.get("D_contact")
        address = request.form.get("D_address")
        age = request.form.get("D_age")
        gender = request.form.get("D_gender")
        history = 0
        bb_id = request.form.get("BB3_id")

        try:
            cursor.execute("""
                INSERT INTO Donor (D_name, D_contact, D_address, D_age, D_gender, D_history, BB3_id)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (name, contact, address, age, gender, history, bb_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error adding donor: {e}</h3>"

    # 🧾 Fetch updated donor list
    cursor.execute("SELECT * FROM Donor ORDER BY D_id")
    columns = [col[0] for col in cursor.description]
    donors = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("donor.html", donors=donors)


# --------------------------------------------------------
# 🔹 VIEW SPECIFIC DONOR + APPOINTMENTS
# --------------------------------------------------------
@app.route("/donor/<int:donor_id>")
def view_donor(donor_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Donor WHERE D_id = :1", [donor_id])
    donor_cols = [c[0] for c in cursor.description]
    donor = dict(zip(donor_cols, cursor.fetchone()))

    cursor.execute("""
        SELECT a.App_id, a.App_date, a.App_time, a.App_status, b.BB_name
        FROM Appointment a
        JOIN Bloodbank b ON a.BB2_id = b.BB_id
        WHERE a.D1_id = :1
        ORDER BY a.App_date DESC
    """, [donor_id])
    app_cols = [c[0] for c in cursor.description]
    appointments = [dict(zip(app_cols, row)) for row in cursor.fetchall()]

    upcoming = [a for a in appointments if a["APP_STATUS"].lower() != "completed"]
    past = [a for a in appointments if a["APP_STATUS"].lower() == "completed"]

    cursor.close()
    conn.close()
    return render_template("donor.html", donor=donor, upcoming=upcoming, past=past)


# --------------------------------------------------------
# 🔹 BLOOD BANK DASHBOARD
# --------------------------------------------------------
@app.route("/bloodbank")
def bloodbank_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Bloodbank")
    bb_cols = [c[0] for c in cursor.description]
    banks = [dict(zip(bb_cols, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Employee WHERE BB1_id IS NOT NULL")
    emp_cols = [c[0] for c in cursor.description]
    employees = [dict(zip(emp_cols, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Donor WHERE BB3_id IS NOT NULL")
    donor_cols = [c[0] for c in cursor.description]
    donors = [dict(zip(donor_cols, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("bloodbank.html", banks=banks, employees=employees, donors=donors)


# --------------------------------------------------------
# 🔹 HOSPITAL DASHBOARD
# --------------------------------------------------------
@app.route("/hospital")
def hospital_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Hospital")
    h_cols = [c[0] for c in cursor.description]
    hospitals = [dict(zip(h_cols, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Bloodbank WHERE Hs1_id IS NOT NULL")
    bb_cols = [c[0] for c in cursor.description]
    banks = [dict(zip(bb_cols, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Ord WHERE Hs2_id IS NOT NULL")
    o_cols = [c[0] for c in cursor.description]
    orders = [dict(zip(o_cols, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("hospital.html", hospitals=hospitals, banks=banks, orders=orders)


# --------------------------------------------------------
# 🔹 FOUNDATION DASHBOARD
# --------------------------------------------------------
@app.route("/foundation")
def foundation_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Foundation")
    f_cols = [c[0] for c in cursor.description]
    foundations = [dict(zip(f_cols, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Hospital WHERE F1_id IS NOT NULL")
    h_cols = [c[0] for c in cursor.description]
    hospitals = [dict(zip(h_cols, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Bloodbank WHERE F2_id IS NOT NULL")
    bb_cols = [c[0] for c in cursor.description]
    banks = [dict(zip(bb_cols, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("foundation.html", foundations=foundations, hospitals=hospitals, banks=banks)


# --------------------------------------------------------
# 🔹 CUSTOMER DASHBOARD
# --------------------------------------------------------
@app.route("/customer")
def customer_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customer")
    c_cols = [c[0] for c in cursor.description]
    customers = [dict(zip(c_cols, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("customer.html", customers=customers)


# --------------------------------------------------------
# 🔹 INVOICE PAGE
# --------------------------------------------------------
@app.route("/invoice")
def invoice_page():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Invoice")
    inv_cols = [c[0] for c in cursor.description]
    invoices = [dict(zip(inv_cols, row)) for row in cursor.fetchall()]

    cursor.execute("""
        SELECT o.Or_id, o.Or_date, o.Or_status, h.Hs_name, c.C_name
        FROM Ord o
        JOIN Hospital h ON o.Hs2_id = h.Hs_id
        JOIN Customer c ON o.C2_id = c.C_id
        ORDER BY o.Or_date DESC
    """)
    ord_cols = [c[0] for c in cursor.description]
    orders = [dict(zip(ord_cols, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Transactionstab")
    t_cols = [c[0] for c in cursor.description]
    transactions = [dict(zip(t_cols, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("invoice.html", invoices=invoices, orders=orders, transactions=transactions)


# --------------------------------------------------------
# 🔹 VIEW DONOR AUDIT LOG
# --------------------------------------------------------
@app.route("/view_audit")
def view_audit():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Donor_Audit ORDER BY Registration_date DESC")
    cols = [c[0] for c in cursor.description]
    audits = [dict(zip(cols, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("audit.html", audits=audits)


# --------------------------------------------------------
# 🔹 ADMIN DASHBOARD
# --------------------------------------------------------
@app.route("/admin")
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = {}

    for name, table in [
        ("hospitals", "Hospital"),
        ("donors", "Donor"),
        ("bloodbanks", "Bloodbank"),
        ("customers", "Customer"),
        ("invoices", "Invoice"),
    ]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        data[name] = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return render_template("donor_board.html", stats=data)


# --------------------------------------------------------
# 🔹 TEST DATABASE CONNECTION
# --------------------------------------------------------
@app.route("/test_db")
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SYSDATE FROM dual")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return f"✅ Connected to Oracle! Current DB time: {result[0]}"
    except Exception as e:
        return f"❌ Database error: {e}"


# --------------------------------------------------------
# 🔹 RUN FLASK APP
# --------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
