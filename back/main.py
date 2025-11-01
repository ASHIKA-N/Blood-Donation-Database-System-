from flask import Flask, render_template, request, redirect, url_for
import oracledb
import os

# Force thin mode (no Oracle client config required)
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



# ------------------------------------------
# 🔹 FLASK CONFIGURATION
# ------------------------------------------
app = Flask(__name__, template_folder="../front")
app.static_folder = "../front"


# ------------------------------------------
# 🔹 INDEX (ROLE SELECTION)
# ------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------------------
# 🔹 ROLE HANDLER
# ------------------------------------------
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


# ------------------------------------------
# 🔹 LOGIN PAGE
# ------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        # Redirect to selected dashboard
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


# ------------------------------------------
# 🔹 DONOR DASHBOARD
# ------------------------------------------
@app.route("/donor")
def donor_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Donor")
    columns = [col[0] for col in cursor.description]
    donors = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("donor.html", donors=donors)


# ------------------------------------------
# 🔹 BLOOD BANK DASHBOARD
# ------------------------------------------
@app.route("/bloodbank")
def bloodbank_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Bloodbank")
    columns = [col[0] for col in cursor.description]
    banks = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Employee WHERE BB1_id IS NOT NULL")
    employees = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Donor WHERE BB3_id IS NOT NULL")
    donors = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("bloodbank.html", banks=banks, employees=employees, donors=donors)


# ------------------------------------------
# 🔹 HOSPITAL DASHBOARD
# ------------------------------------------
@app.route("/hospital")
def hospital_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Hospital")
    columns = [col[0] for col in cursor.description]
    hospitals = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Bloodbank WHERE Hs1_id IS NOT NULL")
    banks = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Ord WHERE Hs2_id IS NOT NULL")
    orders = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("hospital.html", hospitals=hospitals, banks=banks, orders=orders)


# ------------------------------------------
# 🔹 FOUNDATION DASHBOARD
# ------------------------------------------
@app.route("/foundation")
def foundation_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Foundation")
    columns = [col[0] for col in cursor.description]
    foundations = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Hospital WHERE F1_id IS NOT NULL")
    hospitals = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Bloodbank WHERE F2_id IS NOT NULL")
    banks = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("foundation.html", foundations=foundations, hospitals=hospitals, banks=banks)


# ------------------------------------------
# 🔹 CUSTOMER DASHBOARD
# ------------------------------------------
@app.route("/customer")
def customer_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customer")
    columns = [col[0] for col in cursor.description]
    customers = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("customer.html", customers=customers)


# ------------------------------------------
# 🔹 INVOICE PAGE
# ------------------------------------------
@app.route("/invoice")
def invoice_page():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Invoice")
    columns = [col[0] for col in cursor.description]
    invoices = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.execute("""
        SELECT o.Or_id, o.Or_date, o.Or_status, h.Hs_name, c.C_name
        FROM Ord o
        JOIN Hospital h ON o.Hs2_id = h.Hs_id
        JOIN Customer c ON o.C2_id = c.C_id
        ORDER BY o.Or_date DESC
    """)
    orders = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM Transactionstab")
    transactions = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return render_template("invoice.html", invoices=invoices, orders=orders, transactions=transactions)


# ------------------------------------------
# 🔹 ADMIN DASHBOARD
# ------------------------------------------
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


# ------------------------------------------
# 🔹 RUN FLASK APP
# ------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
# ------------------------------------------
# 🔹 TEST DATABASE CONNECTION (Optional)
# ------------------------------------------
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
