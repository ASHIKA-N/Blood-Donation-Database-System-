from flask import Flask, render_template, request, redirect, url_for, flash
import oracledb

# --------------------------------------------------------
# ⚙️ ORACLE CONNECTION
# --------------------------------------------------------
# Uncomment if you have Oracle Instant Client installed
# oracledb.init_oracle_client(lib_dir=r"C:\\instantclient_21_12")

app = Flask(__name__, template_folder="../front")
app.static_folder = "../front"
app.secret_key = "supersecretkey"


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

    if request.method == "POST":
        name = request.form.get("F_name")
        address = request.form.get("F_address")
        contact = request.form.get("F_contact")
        email = request.form.get("F_email")
        try:
            cursor.execute("""
                INSERT INTO Foundation (F_id, F_name, F_address, F_contact, F_mail_id)
                VALUES (foundation_seq.NEXTVAL, :1, :2, :3, :4)
            """, (name, address, contact, email))
            conn.commit()
            flash("✅ Foundation added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding foundation: {e}")

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
                INSERT INTO Hospital (Hs_id, Hs_name, Hs_address, Hs_contact, F1_id)
                VALUES (hospital_seq.NEXTVAL, :1, :2, :3, :4)
            """, (name, address, contact, f_id))
            conn.commit()
            flash("✅ Hospital added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding hospital: {e}")

    cursor.execute("SELECT * FROM Hospital ORDER BY Hs_id")
    hospitals = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("hospital.html", hospitals=hospitals)


# --------------------------------------------------------
# 🩸 BLOOD BANK DASHBOARD (Add + View)
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
            flash("✅ Blood bank added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding blood bank: {e}")

    # 📋 FETCH BLOOD BANKS (for dropdown + display)
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
# ➕ ADD EMPLOYEE TO BLOOD BANK
# --------------------------------------------------------
@app.route("/add_employee", methods=["POST"])
def add_employee():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        e_name = request.form.get("E_name")
        e_address = request.form.get("E_address")
        e_contact = request.form.get("E_contact")
        e_age = request.form.get("E_age")
        e_designation = request.form.get("E_designation")
        e_exp = request.form.get("E_experience")
        bb_id = request.form.get("BB1_id")

        cursor.execute("""
            INSERT INTO Employee (E_id, E_name, E_address, E_contact, E_age,
                                  E_designation, E_experience, BB1_id)
            VALUES (employee_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, :7)
        """, (e_name, e_address, e_contact, e_age, e_designation, e_exp, bb_id))
        conn.commit()
        flash("✅ Employee added successfully!")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error adding employee: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("bloodbank_dashboard"))


# --------------------------------------------------------
# 👨‍💼 EMPLOYEE DASHBOARD
# --------------------------------------------------------
@app.route("/employee", methods=["GET", "POST"])
def employee_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    # --- Schedule Appointment ---
    if request.method == "POST" and "D1_id" in request.form:
        cur.execute("""
            INSERT INTO Appointment (App_id, App_date, App_status, D1_id, C1_id, E2_id, BB2_id)
            VALUES (appointment_seq.NEXTVAL, TO_DATE(:1, 'YYYY-MM-DD'), 'Pending', :2, :3, :4, :5)
        """, [
            request.form["App_date"],
            request.form["D1_id"],
            request.form["C1_id"],
            request.form["E2_id"],
            request.form["BB2_id"]
        ])
        conn.commit()
        flash("✅ Appointment scheduled successfully!")

    # --- Update Status ---
    if request.method == "POST" and "App_status" in request.form:
        cur.execute("""
            UPDATE Appointment SET App_status = :1 WHERE App_id = :2
        """, [request.form["App_status"], request.form["App_id"]])
        conn.commit()
        flash("✅ Appointment marked completed!")

    # --- Fetch dropdown data ---
    cur.execute("SELECT E_id, E_name, BB1_id FROM Employee ORDER BY E_id")
    employees = cur.fetchall()

    cur.execute("SELECT BB_id, BB_name FROM Bloodbank ORDER BY BB_id")
    bloodbanks = cur.fetchall()

    cur.execute("SELECT D_id, D_name, D_contact FROM Donor ORDER BY D_id")
    donors = cur.fetchall()

    cur.execute("SELECT C_id, C_name, C_contact FROM Customer ORDER BY C_id")
    customers = cur.fetchall()

    # --- Fetch appointments ---
    cur.execute("""
        SELECT A.App_id, D.D_name, C.C_name, B.BB_name, E.E_name, A.App_date, A.App_status
        FROM Appointment A
        JOIN Donor D ON A.D1_id = D.D_id
        JOIN Customer C ON A.C1_id = C.C_id
        JOIN Employee E ON A.E2_id = E.E_id
        JOIN Bloodbank B ON A.BB2_id = B.BB_id
        ORDER BY A.App_id
    """)
    appointments = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("employee.html",
                           employees=employees,
                           bloodbanks=bloodbanks,
                           donors=donors,
                           customers=customers,
                           appointments=appointments)


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
                INSERT INTO Donor (D_id, D_name, D_contact, D_address, D_age, D_gender, D_history, BB3_id)
                VALUES (donor_seq.NEXTVAL, :1, :2, :3, :4, :5, 0, :6)
            """, (name, contact, address, age, gender, bb_id))
            conn.commit()
            flash("✅ Donor added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding donor: {e}")

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
                INSERT INTO Appointment (App_id, App_date, App_time, App_status, D1_id, BB2_id)
                VALUES (appointment_seq.NEXTVAL, TO_DATE(:1, 'YYYY-MM-DD'), SYSTIMESTAMP, :2, :3, :4)
            """, (date, status, donor, bb_id))
            conn.commit()
            flash("✅ Appointment scheduled successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error scheduling appointment: {e}")

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
                INSERT INTO Customer (C_id, C_name, C_address, C_contact, C_gender, C_history)
                VALUES (customer_seq.NEXTVAL, :1, :2, :3, :4, :5)
            """, (name, address, contact, gender, history))
            conn.commit()
            flash("✅ Customer added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding customer: {e}")

    cursor.execute("SELECT * FROM Customer ORDER BY C_id")
    customers = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("customer.html", customers=customers)


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
# 🧭 ROLE SELECTION HANDLER (✅ FINAL ONE)
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
