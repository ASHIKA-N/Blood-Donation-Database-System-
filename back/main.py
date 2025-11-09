from flask import Flask, render_template, request, redirect, url_for
import oracledb

# --------------------------------------------------------
# ⚙️ ORACLE CONNECTION
# --------------------------------------------------------
# Uncomment if you have Oracle Instant Client installed
# oracledb.init_oracle_client(lib_dir=r"C:\\instantclient_21_12")

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
# 🏠 INDEX PAGE
# --------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")




# --------------------------------------------------------
# 🧱 FOUNDATION DASHBOARD (ADD + VIEW)
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
        email = request.form.get("F_email")
        try:
            cursor.execute("""
                INSERT INTO Foundation (F_id, F_name, F_address, F_contact, F_email)
                VALUES (foundation_seq.NEXTVAL, :1, :2, :3, :4)
            """, (name, address, contact, email))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error adding foundation: {e}</h3>"

    cursor.execute("SELECT * FROM Foundation ORDER BY F_id")
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return render_template("foundation.html", headers=headers, data=rows)


# --------------------------------------------------------
# 🏥 HOSPITAL DASHBOARD
# --------------------------------------------------------
@app.route("/hospital", methods=["GET", "POST"])
def hospital_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form.get("Hs_name")
        address = request.form.get("Hs_address")
        contact = request.form.get("Hs_contact")
        f_id = request.form.get("F1_id")
        try:
            cursor.execute("""
                INSERT INTO Hospital (Hs_name, Hs_address, Hs_contact, F1_id)
                VALUES (:1, :2, :3, :4)
            """, (name, address, contact, f_id))
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
# 🩸 BLOOD BANK DASHBOARD
# --------------------------------------------------------
# --------------------------------------------------------
# 🩸 BLOOD BANK DASHBOARD (Add + View + Add Employee)
# --------------------------------------------------------
@app.route("/bloodbank", methods=["GET", "POST"])
def bloodbank_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🩸 ADD BLOOD BANK
    if request.method == "POST" and "BB_name" in request.form:
        name = request.form.get("BB_name")
        address = request.form.get("BB_address")
        contact = request.form.get("BB_contact")
        volume = request.form.get("BB_volume")
        btype = request.form.get("BB_type")
        f_id = request.form.get("F2_id")
        try:
            cursor.execute("""
                INSERT INTO Bloodbank (BB_id, BB_name, BB_address, BB_contact, BB_volume, BB_type, F2_id)
                VALUES (bloodbank_seq.NEXTVAL, :1, :2, :3, :4, :5, :6)
            """, (name, address, contact, volume, btype, f_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error adding blood bank: {e}</h3>"

    # 👥 ADD EMPLOYEE TO BLOOD BANK
    elif request.method == "POST" and "E_name" in request.form:
        e_name = request.form.get("E_name")
        e_address = request.form.get("E_address")
        e_contact = request.form.get("E_contact")
        e_designation = request.form.get("E_designation")
        e_exp = request.form.get("E_experience")
        bb_id = request.form.get("BB_id")
        try:
            cursor.execute("""
                INSERT INTO Employee (E_id, E_name, E_address, E_contact, E_designation, E_experience, BB1_id)
                VALUES (employee_seq.NEXTVAL, :1, :2, :3, :4, :5, :6)
            """, (e_name, e_address, e_contact, e_designation, e_exp, bb_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error adding employee: {e}</h3>"

    # 📋 FETCH BLOOD BANKS (for table + dropdown)
    cursor.execute("SELECT BB_id, BB_name FROM Bloodbank ORDER BY BB_id")
    bloodbanks = cursor.fetchall()

    cursor.execute("SELECT * FROM Bloodbank ORDER BY BB_id")
    banks = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

    # 🧍 FETCH EMPLOYEES LINKED TO BLOOD BANKS
    cursor.execute("""
        SELECT e.E_id, e.E_name, e.E_designation, e.E_experience, e.E_contact, b.BB_name
        FROM Employee e
        JOIN Bloodbank b ON e.BB1_id = b.BB_id
        ORDER BY e.E_id
    """)
    employees = cursor.fetchall()
    e_headers = [desc[0] for desc in cursor.description]

    cursor.close()
    conn.close()

    return render_template("bloodbank.html",
                           banks=banks,
                           bloodbanks=bloodbanks,
                           employees=employees,
                           e_headers=e_headers)

# --------------------------------------------------------
# 👨‍💼 EMPLOYEE DASHBOARD (Add + View)
# --------------------------------------------------------
@app.route("/employee", methods=["GET", "POST"])
def employee_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🩸 Fetch blood banks for dropdown
    cursor.execute("SELECT BB_id, BB_name FROM Bloodbank ORDER BY BB_id")
    bloodbanks = cursor.fetchall()

    # ➕ Add new employee to selected blood bank
    if request.method == "POST":
        name = request.form.get("E_name")
        address = request.form.get("E_address")
        contact = request.form.get("E_contact")
        age = request.form.get("E_age")
        designation = request.form.get("E_designation")
        exp = request.form.get("E_experience")
        bb_id = request.form.get("BB1_id")  # dropdown selection

        try:
            cursor.execute("""
                INSERT INTO Employee (E_id, E_name, E_address, E_contact, E_age, 
                                      E_designation, E_experience, BB1_id)
                VALUES (employee_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, :7)
            """, (name, address, contact, age, designation, exp, bb_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error adding employee: {e}</h3>"

    # 📊 Fetch employees grouped by blood bank
    cursor.execute("""
        SELECT b.BB_name, e.E_id, e.E_name, e.E_designation, e.E_experience, e.E_contact
        FROM Employee e
        JOIN Bloodbank b ON e.BB1_id = b.BB_id
        ORDER BY b.BB_name, e.E_id
    """)
    employees = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]

    # 👥 Group employees by blood bank name
    grouped_data = {}
    for row in employees:
        bb_name = row[0]
        grouped_data.setdefault(bb_name, []).append(row[1:])

    cursor.close()
    conn.close()

    return render_template(
        "employee.html",
        headers=headers[1:],          # skip BB_name column
        grouped_data=grouped_data,
        bloodbanks=bloodbanks
    )


# --------------------------------------------------------
# 🧍 DONOR DASHBOARD
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
# 📅 APPOINTMENT DASHBOARD
# --------------------------------------------------------
@app.route("/appointment", methods=["GET", "POST"])
def appointment_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        date = request.form.get("App_date")
        status = request.form.get("App_status")
        donor = request.form.get("D1_id")
        bb_id = request.form.get("BB2_id")
        try:
            cursor.execute("""
                INSERT INTO Appointment (App_date, App_time, App_status, D1_id, BB2_id)
                VALUES (TO_DATE(:1, 'YYYY-MM-DD'), SYSTIMESTAMP, :2, :3, :4)
            """, (date, status, donor, bb_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"<h3 style='color:red'>❌ Error scheduling appointment: {e}</h3>"

    cursor.execute("SELECT * FROM Appointment ORDER BY App_id")
    apps = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("appointment.html", appointments=apps)


# --------------------------------------------------------
# 👥 CUSTOMER DASHBOARD
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
# 🧾 ORDER DASHBOARD
# --------------------------------------------------------
@app.route("/order")
def order_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Ord ORDER BY Or_id")
    orders = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("order.html", orders=orders)


# --------------------------------------------------------
# 💵 INVOICE DASHBOARD
# --------------------------------------------------------
@app.route("/invoice")
def invoice_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Invoice ORDER BY In_id")
    invoices = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("invoice.html", invoices=invoices)


# --------------------------------------------------------
# 💳 TRANSACTION DASHBOARD
# --------------------------------------------------------
@app.route("/transaction")
def transaction_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Transactionstab ORDER BY T_id")
    txns = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("transaction.html", txns=txns)


# --------------------------------------------------------
# 🧮 ADMIN DASHBOARD
# --------------------------------------------------------
@app.route("/admin")
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Donor")
    donors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Hospital")
    hospitals = cursor.fetchone()[0]

    cursor.execute("SELECT NVL(SUM(BB_volume), 0) FROM Bloodbank")
    volume = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Appointment WHERE App_status = 'Completed'")
    completed = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        "admin.html",
        donors=donors,
        hospitals=hospitals,
        volume=volume,
        completed=completed
    )

# --------------------------------------------------------
# 🧭 ROLE SELECTION HANDLER
# --------------------------------------------------------
@app.route("/select_role", methods=["POST"])
def select_role():
    role = request.form.get("role")
    routes = {
        "admin": "admin_dashboard",
        "foundation": "foundation_dashboard",
        "hospital": "hospital_dashboard",
        "bloodbank": "bloodbank_dashboard",
        "employee": "employee_dashboard",
        "donor": "donor_dashboard",
        "customer": "customer_dashboard"
    }
    return redirect(url_for(routes.get(role, "index")))

# --------------------------------------------------------
# 🚀 RUN APP
# --------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
