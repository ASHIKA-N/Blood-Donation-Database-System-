from flask import Flask, render_template, request, redirect, url_for, flash
import oracledb

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../front")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

app.static_folder = "../front"
app.secret_key = "aryams_secret"

# ======================================================
# ORACLE CONNECTION
# ======================================================
def get_db_connection():
    return oracledb.connect(
        user="root",
        password="Gt650101",
        dsn="localhost:1521/XEPDB1"
    )

# ======================================================
# HOME PAGE
# ======================================================
@app.route("/")
def index():
    return render_template("index.html")

# ======================================================
# ADMIN DASHBOARD
# ======================================================
@app.route("/admin")
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Donor")
    donors = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Hospital")
    hospitals = cur.fetchone()[0]

    cur.execute("SELECT NVL(SUM(BB_volume),0) FROM Bloodbank")
    volume = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM History")
    completed = cur.fetchone()[0]

    cur.execute("SELECT BB_id, BB_name FROM Bloodbank")
    bloodbanks = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "admin.html",
        donors=donors,
        hospitals=hospitals,
        volume=volume,
        completed=completed,
        bloodbanks=bloodbanks
    )

# ======================================================
# ADMIN — ADD FOUNDATION (INTERNAL)
# ======================================================
@app.route("/admin_add_foundation", methods=["POST"])
def admin_add_foundation():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO Foundation (F_id, F_name, F_address, F_contact, F_mail_id)
            VALUES (foundation_seq.NEXTVAL, :1, :2, :3, :4)
        """, [
            request.form["F_name"],
            request.form["F_address"],
            request.form["F_contact"],
            request.form["F_email"]
        ])
        conn.commit()
        flash("Foundation added successfully!")
    except Exception as e:
        conn.rollback()
        flash(f"Error: {e}")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("admin_dashboard"))

# ======================================================
# ADMIN — ADD HOSPITAL (F1_id = 1)
# ======================================================
@app.route("/add_hospital", methods=["POST"])
def add_hospital():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO Hospital (Hs_id, Hs_name, Hs_address, Hs_contact, F1_id)
            VALUES (hospital_seq.NEXTVAL, :1, :2, :3, 1)
        """, [
            request.form["Hs_name"],
            request.form["Hs_address"],
            request.form["Hs_contact"]
        ])
        conn.commit()
        flash("🏥 Hospital added successfully!")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Error adding hospital: {e}")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("admin_dashboard"))

# ======================================================
# ADMIN — ADD BLOOD BANK (F2_id = 1)
# ======================================================
@app.route("/add_bloodbank", methods=["POST"])
def add_bloodbank():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO Bloodbank (BB_id, BB_name, BB_address, BB_contact, BB_volume, F2_id)
            VALUES (bloodbank_seq.NEXTVAL, :1, :2, :3, :4, 1)
        """, [
            request.form["BB_name"],
            request.form["BB_address"],
            request.form["BB_contact"],
            request.form["BB_volume"]
        ])
        conn.commit()
        flash("🩸 Bloodbank added successfully!")
    except Exception as e:
        conn.rollback()
        flash(f"Error adding blood bank: {e}")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("admin_dashboard"))

# ======================================================
# ADMIN — ADD EMPLOYEE
# ======================================================
@app.route("/admin_add_employee", methods=["POST"])
def admin_add_employee():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO Employee
            (E_id, E_name, E_address, E_contact, E_age,
             E_designation, E_experience, BB1_id)
            VALUES (employee_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, :7)
        """, [
            request.form["E_name"],
            request.form["E_address"],
            request.form["E_contact"],
            request.form["E_age"],
            request.form["E_designation"],
            request.form["E_experience"],
            request.form["BB1_id"]
        ])

        conn.commit()
        flash("Employee added successfully!")

    except Exception as e:
        conn.rollback()
        flash(f"Error adding employee: {e}")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("admin_dashboard"))


# --------------------------------------------------------
# DONOR DASHBOARD
# --------------------------------------------------------
@app.route("/donor", methods=["GET", "POST"])
def donor_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    # Add new donor
    if request.method == "POST":
        try:
            cur.execute("""
                INSERT INTO Donor (
                    D_id, D_name, D_contact, D_address,
                    D_age, D_gender, D_bloodtype, BB3_id
                )
                VALUES (
                    donor_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, :7
                )
            """, [
                request.form["D_name"],
                request.form["D_contact"],
                request.form["D_address"],
                request.form["D_age"],
                request.form["D_gender"],
                request.form["D_bloodtype"],
                request.form["BB3_id"]
            ])

            conn.commit()
            flash("Donor registered successfully!")

        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")

    # Fetch dropdown data
    cur.execute("SELECT BB_id, BB_name FROM Bloodbank ORDER BY BB_id")
    bloodbanks = cur.fetchall()

    # Fetch donor table
    cur.execute("SELECT * FROM Donor ORDER BY D_id")
    donors = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return render_template(
        "donor.html",
        donors=donors,
        headers=headers,
        bloodbanks=bloodbanks
    )
#--customer--
@app.route("/customer", methods=["GET", "POST"])
def customer_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    # FETCH HOSPITALS FOR DROPDOWN
    cur.execute("SELECT Hs_id, Hs_name FROM Hospital ORDER BY Hs_id")
    hospitals = cur.fetchall()

    # ADD CUSTOMER
    if request.method == "POST":
        try:
            cur.execute("""
                INSERT INTO Customer (
                    C_id, C_name, C_contact, C_gender,
                    C_history, C_address, Hs1_id
                )
                VALUES (
                    customer_seq.NEXTVAL, :1, :2, :3, :4, :5, :6
                )
            """, [
                request.form["C_name"],
                request.form["C_contact"],
                request.form["C_gender"],
                "New",
                request.form["C_address"],
                request.form["Hs1_id"] or None
            ])
            conn.commit()
            flash("Customer added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"Error adding customer: {e}")
        return redirect(url_for("customer_dashboard"))

    # FETCH CUSTOMERS (CONVERT TO DICT)
    cur.execute("""
        SELECT c.C_id, c.C_name, c.C_contact, c.C_gender,
               c.C_history, c.C_address,
               h.Hs_name
        FROM Customer c
        LEFT JOIN Hospital h ON c.Hs1_id = h.Hs_id
        ORDER BY c.C_id
    """)
    rows = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    customers = [dict(zip(headers, row)) for row in rows]

    cur.close()
    conn.close()

    return render_template(
        "customer.html",
        customers=customers,
        headers=headers,
        hospitals=hospitals
    )

# ======================================================
# HOSPITAL DASHBOARD (ADD + PLACE ORDER + AUTO CUSTOMER)
# ======================================================
# ======================================================
# HOSPITAL DASHBOARD (ADD + PLACE ORDER + AUTO-FILL)
# ======================================================
@app.route("/hospital", methods=["GET", "POST"])
def hospital_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    # ---------------------------------------------------
    # ADD NEW HOSPITAL
    # ---------------------------------------------------
    if request.method == "POST" and "Hs_name" in request.form:
        try:
            cur.execute("""
                INSERT INTO Hospital (Hs_id, Hs_name, Hs_address, Hs_contact, F1_id)
                VALUES (hospital_seq.NEXTVAL, :1, :2, :3, 1)
            """, [
                request.form["Hs_name"],
                request.form["Hs_address"],
                request.form["Hs_contact"]
            ])
            conn.commit()
            flash("🏥 Hospital added successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding hospital: {e}", "danger")

    # ---------------------------------------------------
    # FETCH HOSPITAL LIST
    # ---------------------------------------------------
    cur.execute("SELECT Hs_id, Hs_name, Hs_address, Hs_contact FROM Hospital ORDER BY Hs_id")
    hospitals = cur.fetchall()

    # ---------------------------------------------------
    # FETCH BLOODBANK LIST
    # ---------------------------------------------------
    cur.execute("SELECT BB_id, BB_name FROM Bloodbank ORDER BY BB_id")
    bloodbanks = cur.fetchall()

    # ---------------------------------------------------
    # FETCH CUSTOMERS + THEIR HOSPITAL
    # ---------------------------------------------------
    cur.execute("""
        SELECT 
            C.C_id, C.C_name, C.C_contact, C.C_gender, C.C_address,
            H.Hs_id, H.Hs_name
        FROM Customer C
        LEFT JOIN Hospital H ON C.Hs1_id = H.Hs_id
        ORDER BY C.C_id
    """)
    customers = cur.fetchall()

    # ---------------------------------------------------
    # FETCH ORDERS
    # ---------------------------------------------------
    cur.execute("""
        SELECT O.Or_id, H.Hs_name, C.C_name, B.BB_name,
               O.Or_type, O.Or_quantity, O.Or_status
        FROM Ord O
        JOIN Hospital H ON O.Hs2_id = H.Hs_id
        JOIN Customer C ON O.C2_id = C.C_id
        JOIN Bloodbank B ON O.BB4_id = B.BB_id
        ORDER BY O.Or_id
    """)
    orders = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "hospital.html",
        hospitals=hospitals,
        bloodbanks=bloodbanks,
        customers=customers,
        orders=orders
    )



@app.route("/hospital_order", methods=["POST"])
def hospital_order():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Hospital + Bloodbank
        hs_id = request.form["Hs2_id"]
        bb_id = request.form["BB4_id"]
        qty = float(request.form["Or_quantity"])
        btype = request.form["Or_type"]

        # Patient
        c_name = request.form["C_name"]
        c_contact = request.form["C_contact"]
        c_gender = request.form["C_gender"]
        c_address = request.form["C_address"]

        # --------------------------------------
        # 1️⃣ CREATE CUSTOMER
        # --------------------------------------
        cur.execute("SELECT customer_seq.NEXTVAL FROM dual")
        new_cid = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO Customer (
                C_id, C_name, C_contact, C_gender,
                C_address, C_history, Hs1_id
            ) VALUES (:1,:2,:3,:4,:5,'New',:6)
        """, [new_cid, c_name, c_contact, c_gender, c_address, hs_id])

        # --------------------------------------
        # 2️⃣ CREATE ORDER
        # --------------------------------------
        cur.execute("SELECT order_seq.NEXTVAL FROM dual")
        new_oid = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO Ord (
                Or_id, Or_date, Or_time, Or_quantity,
                Or_status, Or_type, C2_id, Hs2_id, BB4_id
            ) VALUES (
                :1, SYSDATE, SYSTIMESTAMP, :2,
                'Pending', :3, :4, :5, :6
            )
        """, [new_oid, qty, btype, new_cid, hs_id, bb_id])

        # --------------------------------------
        # 3️⃣ AUTO-GENERATE INVOICE
        # --------------------------------------
        price_chart = {
            "A+": 25, "A-": 25, "B+": 25, "B-": 25,
            "AB+": 30, "AB-": 30, "O+": 20, "O-": 35
        }

        amount = qty * price_chart[btype]

        cur.execute("SELECT invoice_seq.NEXTVAL FROM dual")
        inv_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO Invoice (
                In_id, In_date, In_time, In_amount,
                In_status, Or1_id
            ) VALUES (
                :1, SYSDATE, SYSTIMESTAMP, :2,
                'Generated', :3
            )
        """, [inv_id, amount, new_oid])

        # Update order status
        cur.execute("UPDATE Ord SET Or_status='Invoiced' WHERE Or_id=:1", [new_oid])

        conn.commit()
        flash(f"Order #{new_oid} placed successfully! Invoice #{inv_id} auto-generated.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error placing order: {e}", "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("hospital_dashboard"))
@app.route("/create_invoice", methods=["POST"])
def create_invoice():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        order_id = request.form["Or_id"]

        price_chart = {
            "A+": 25, "A-": 25, "B+": 25, "B-": 25,
            "AB+": 30, "AB-": 30, "O+": 20, "O-": 35
        }

        cur.execute("""
            SELECT Or_quantity, Or_type
            FROM Ord
            WHERE Or_id = :1
        """, [order_id])
        row = cur.fetchone()

        qty, btype = row
        amount = float(qty) * price_chart[btype]

        cur.execute("SELECT invoice_seq.NEXTVAL FROM dual")
        inv_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO Invoice (
                In_id, In_date, In_time,
                In_amount, In_status, Or1_id
            ) VALUES (
                :1, SYSDATE, SYSTIMESTAMP,
                :2, 'Generated', :3
            )
        """, [inv_id, amount, order_id])

        cur.execute("""
            UPDATE Ord SET Or_status='Invoiced'
            WHERE Or_id=:1
        """, [order_id])

        conn.commit()
        flash(f"Invoice #{inv_id} generated!", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Invoice Error: {e}", "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("employee_dashboard"))
@app.route("/generate_invoice/<int:order_id>")
def generate_invoice(order_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT Or_quantity, Or_type
            FROM Ord WHERE Or_id=:1
        """, [order_id])

        row = cur.fetchone()
        qty, btype = row

        amount = float(qty) * 2     # simple model

        cur.execute("SELECT invoice_seq.NEXTVAL FROM dual")
        inv_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO Invoice (
                In_id, In_date, In_time,
                In_amount, In_status, Or1_id
            ) VALUES (
                :1, SYSDATE, SYSTIMESTAMP,
                :2, 'Generated', :3
            )
        """, [inv_id, amount, order_id])

        cur.execute("UPDATE Ord SET Or_status='Invoiced' WHERE Or_id=:1", [order_id])

        conn.commit()
        flash(f"Invoice #{inv_id} created!", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error generating invoice: {e}", "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("employee_dashboard"))


@app.route("/get_customer/<int:cid>")
def get_customer(cid):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            C.C_contact, C.C_gender, C.C_address,
            H.Hs_id, B.BB_id
        FROM Customer C
        LEFT JOIN Hospital H ON C.Hs1_id = H.Hs_id
        LEFT JOIN Bloodbank B ON H.Hs_id = B.Hs3_id
        WHERE C.C_id = :1
    """,[cid])

    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return {
            "contact": row[0],
            "gender": row[1],
            "address": row[2],
            "hospital_id": row[3],
            "bloodbank_id": row[4]
        }
    else:
        return {}

@app.route("/get_customer_by_name/<name>")
def get_customer_by_name(name):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            C.C_id, C.C_name, C.C_contact, C.C_gender, C.C_address,
            H.Hs_id, H.Hs_name,
            B.BB_id, B.BB_name
        FROM Customer C
        LEFT JOIN Hospital H ON C.Hs1_id = H.Hs_id
        LEFT JOIN Bloodbank B ON H.Hs_id = B.Hs3_id
        WHERE LOWER(C.C_name) LIKE LOWER(:1)
    """, ['%' + name + '%'])

    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return {
            "cid": row[0],
            "name": row[1],
            "contact": row[2],
            "gender": row[3],
            "address": row[4],
            "hospital_id": row[5],
            "hospital": row[6],
            "bloodbank_id": row[7],
            "bloodbank": row[8]
        }
    return {}

# ======================================================
# BLOOD BANK DASHBOARD (FINAL WORKING VERSION)
# ======================================================
@app.route("/bloodbank", methods=["GET", "POST"])
def bloodbank_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    # --------------------------------------
    # ADD BLOOD BANK (AUTO F2_id = 1)
    # --------------------------------------
    if request.method == "POST":
        try:
            cur.execute("""
                INSERT INTO Bloodbank (
                    BB_id, BB_name, BB_address, BB_contact, BB_volume, F2_id
                )
                VALUES (bloodbank_seq.NEXTVAL, :1, :2, :3, :4, 1)
            """, [
                request.form["BB_name"],
                request.form["BB_address"],
                request.form["BB_contact"],
                request.form["BB_volume"]
            ])
            conn.commit()
            flash("✅ Bloodbank added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding bloodbank: {e}")

    # -----------------------------------------------------
    # 1️⃣ FETCH ALL BLOODBANKS FOR VIEW TABLE
    # -----------------------------------------------------
    cur.execute("SELECT * FROM Bloodbank ORDER BY BB_id")
    banks = [
        dict(zip([col[0] for col in cur.description], row))
        for row in cur.fetchall()
    ]
    headers = [col[0] for col in cur.description]

    # -----------------------------------------------------
    # 2️⃣ FETCH BLOODBANK LIST FOR EMPLOYEE DROPDOWN
    # -----------------------------------------------------
    cur.execute("SELECT BB_id, BB_name FROM Bloodbank ORDER BY BB_id")
    bloodbanks = cur.fetchall()

    # -----------------------------------------------------
    # 3️⃣ FETCH EMPLOYEES MAPPED TO BLOODBANKS
    # -----------------------------------------------------
    cur.execute("""
        SELECT e.E_id, e.E_name, e.E_designation, 
               e.E_experience, e.E_contact, b.BB_name
        FROM Employee e
        JOIN Bloodbank b ON e.BB1_id = b.BB_id
        ORDER BY e.E_id
    """)
    employees = cur.fetchall()
    e_headers = [col[0] for col in cur.description]

    cur.close()
    conn.close()

    return render_template(
        "bloodbank.html",
        banks=banks,
        headers=headers,
        bloodbanks=bloodbanks,   # FIXED
        employees=employees,
        e_headers=e_headers
    )

# --------------------------------------------------------
# EMPLOYEE DASHBOARD (FULL WORKING)
# --------------------------------------------------------
# ======================================================
# EMPLOYEE DASHBOARD (ADD EMPLOYEE + VIEW ORDERS + INVOICE)
# ======================================================
@app.route("/employee", methods=["GET", "POST"])
def employee_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    # ---------------------------------------------------------
    # ADD NEW EMPLOYEE
    # ---------------------------------------------------------
    if request.method == "POST" and "E_name" in request.form:
        try:
            cur.execute("SELECT employee_seq.NEXTVAL FROM dual")
            new_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO Employee (
                    E_id, E_name, E_contact, E_address,
                    E_age, E_designation, E_experience, BB1_id
                ) VALUES (:1,:2,:3,:4,:5,:6,:7,:8)
            """, [
                new_id,
                request.form["E_name"],
                request.form["E_contact"],
                request.form["E_address"],
                request.form["E_age"],
                request.form["E_designation"],
                request.form["E_experience"],
                request.form["BB1_id"]
            ])

            conn.commit()
            flash("Employee added successfully!", "success")

        except Exception as e:
            conn.rollback()
            flash(f"Error adding employee: {e}", "danger")

        return redirect(url_for("employee_dashboard"))

    # ---------------------------------------------------------
    # FETCH EMPLOYEES
    # ---------------------------------------------------------
    cur.execute("SELECT * FROM Employee ORDER BY E_id")
    employees = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    # BLOODBANKS
    cur.execute("SELECT BB_id, BB_name FROM Bloodbank")
    bloodbanks = cur.fetchall()

    # ---------------------------------------------------------
    # FETCH ORDERS (THIS WAS MISSING → FIXED)
    # ---------------------------------------------------------
    cur.execute("""
        SELECT 
            O.Or_id,               -- 0
            C.C_name,              -- 1
            H.Hs_name,             -- 2
            B.BB_name,             -- 3
            O.Or_type,             -- 4
            O.Or_quantity,         -- 5
            O.Or_status            -- 6
        FROM Ord O
        JOIN Customer C ON O.C2_id = C.C_id
        JOIN Hospital H ON O.Hs2_id = H.Hs_id
        JOIN Bloodbank B ON O.BB4_id = B.BB_id
        ORDER BY O.Or_id
    """)
    orders = cur.fetchall()
    o_headers = ["Order ID", "Customer", "Hospital", "Blood Bank",
                 "Blood Type", "Quantity", "Status"]

    cur.close()
    conn.close()

    return render_template(
        "employee.html",
        employees=employees,
        headers=headers,
        bloodbanks=bloodbanks,
        orders=orders,
        o_headers=o_headers
    )



# ======================================================
# APPOINTMENTS PAGE (CREATE + VIEW)
# ======================================================
@app.route("/appointments", methods=["GET", "POST"])
def appointments_page():
    conn = get_db_connection()
    cur = conn.cursor()

    # ===================================================================
    # 1️⃣ CREATE NEW APPOINTMENT
    # ===================================================================
    if request.method == "POST" and "App_status" not in request.form:
        try:
            cur.execute("""
                INSERT INTO Appointment (
                    App_id, App_date, App_status,
                    D1_id, C1_id, E2_id, BB2_id
                )
                VALUES (
                    appointment_seq.NEXTVAL,
                    TO_DATE(:1, 'YYYY-MM-DD'),
                    'Pending',
                    :2, :3, :4, :5
                )
            """, [
                request.form["App_date"],
                request.form["D1_id"],
                request.form["C1_id"],
                request.form["E2_id"],
                request.form["BB2_id"]
            ])
            conn.commit()
            flash("Appointment created successfully!", "success")

        except Exception as e:
            conn.rollback()
            flash(f"❌ Error creating appointment: {e}", "danger")

    # ===================================================================
    # 2️⃣ MARK APPOINTMENT AS COMPLETED
    # ===================================================================
    if request.method == "POST" and "App_status" in request.form:

        app_id = request.form["App_id"]

        try:
            # Update status → Completed
            cur.execute("""
                UPDATE Appointment SET App_status='Completed'
                WHERE App_id=:1
            """, [app_id])
            conn.commit()

            # Fetch all linked data
            cur.execute("""
                SELECT
                    D.D_id, D.D_name, D.D_contact, D.D_address, D.D_gender, 
                    D.D_age, D.D_bloodtype,
                    C.C_id, C.C_name, C.C_contact, C.C_address,
                    H.Hs_name, H.Hs_contact, H.Hs_address,
                    B.BB_id, B.BB_name,
                    A.App_date
                FROM Appointment A
                JOIN Donor D ON A.D1_id = D.D_id
                JOIN Customer C ON A.C1_id = C.C_id
                LEFT JOIN Hospital H ON C.Hs1_id = H.Hs_id
                JOIN Bloodbank B ON A.BB2_id = B.BB_id
                WHERE A.App_id=:1
            """, [app_id])

            rec = cur.fetchone()

            if rec:
                donor_id = rec[0]
                customer_id = rec[7]
                bloodbank_id = rec[14]
                app_date = rec[16]

                # ----------------------------------------------------------
                # 2A. Insert into History (FIXED → EXACT 14 VALUES)
                # ----------------------------------------------------------
                cur.execute("""
                    INSERT INTO History (
                        D_name, D_contact, D_address, D_gender, D_age, D_bloodtype,
                        C_name, C_contact, C_address,
                        Hs_name, Hs_contact, Hs_address,
                        BB_name,
                        Donation_date, Archived_on
                    ) VALUES (
                        :1,:2,:3,:4,:5,:6,
                        :7,:8,:9,
                        :10,:11,:12,
                        :13,
                        :14, SYSTIMESTAMP
                    )
                """, [
                    rec[1], rec[2], rec[3], rec[4], rec[5], rec[6],      # Donor
                    rec[8], rec[9], rec[10],                              # Customer
                    rec[11], rec[12], rec[13],                            # Hospital
                    rec[15],                                              # Bloodbank name
                    app_date                                              # Donation date
                ])

                # ----------------------------------------------------------
                # 2B. Add 450 ml to blood bank
                # ----------------------------------------------------------
                cur.execute("""
                    UPDATE Bloodbank SET BB_volume = BB_volume + 450
                    WHERE BB_id=:1
                """, [bloodbank_id])

                # ----------------------------------------------------------
                # 2C. Increase donor history count
                # ----------------------------------------------------------
                cur.execute("""
                    UPDATE Donor SET D_history = D_history + 1
                    WHERE D_id=:1
                """, [donor_id])

                # ----------------------------------------------------------
                # 2D. DELETE completed appointment (VERY IMPORTANT)
                # ----------------------------------------------------------
                cur.execute("DELETE FROM Appointment WHERE App_id=:1", [app_id])

                # ----------------------------------------------------------
                # 2E. Delete donor if no more appointments
                # ----------------------------------------------------------
                cur.execute("""
                    SELECT COUNT(*) FROM Appointment WHERE D1_id=:1
                """, [donor_id])
                if cur.fetchone()[0] == 0:
                    cur.execute("DELETE FROM Donor WHERE D_id=:1", [donor_id])

                # ----------------------------------------------------------
                # 2F. Delete customer only if unused everywhere
                # ----------------------------------------------------------
                cur.execute("""
                    SELECT COUNT(*) FROM Appointment WHERE C1_id=:1
                """, [customer_id])
                app_count = cur.fetchone()[0]

                cur.execute("""
                    SELECT COUNT(*) FROM Ord WHERE C2_id=:1
                """, [customer_id])
                order_count = cur.fetchone()[0]

                if app_count == 0 and order_count == 0:
                    cur.execute("DELETE FROM Customer WHERE C_id=:1", [customer_id])

                conn.commit()
                flash("✔ Donation Completed — Archived Successfully!", "success")

        except Exception as e:
            conn.rollback()
            flash(f"❌ Error: {e}", "danger")

    # ===================================================================
    # 3️⃣ FETCH DROPDOWNS
    # ===================================================================
    cur.execute("SELECT D_id, D_name FROM Donor")
    donors = cur.fetchall()

    cur.execute("SELECT C_id, C_name FROM Customer")
    customers = cur.fetchall()

    cur.execute("SELECT E_id, E_name FROM Employee")
    employees = cur.fetchall()

    cur.execute("SELECT BB_id, BB_name FROM Bloodbank")
    bloodbanks = cur.fetchall()

    # ===================================================================
    # 4️⃣ FETCH ALL APPOINTMENTS
    # ===================================================================
    cur.execute("""
        SELECT A.App_id, D.D_name, C.C_name, B.BB_name, E.E_name,
               A.App_date, A.App_status
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

    return render_template(
        "appointments.html",
        donors=donors,
        customers=customers,
        employees=employees,
        bloodbanks=bloodbanks,
        appointments=appointments
    )

# ======================================================
# CUSTOMER PAYMENT
# ======================================================
@app.route("/customer_payment", methods=["GET", "POST"])
def customer_payment():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        inv_id = request.form["In_id"]
        mode = request.form["method"]

        try:
            cur.execute("""
                INSERT INTO Transactionstab (
                    T_id, T_date, T_time, T_mode, T_status, In1_id
                ) VALUES (
                    transaction_seq.NEXTVAL,
                    SYSDATE, SYSTIMESTAMP, :1, 'Success', :2
                )
            """, [mode, inv_id])

            cur.execute("UPDATE Invoice SET In_status='Paid' WHERE In_id=:1", [inv_id])

            cur.execute("""
                UPDATE Ord 
                SET Or_status='Completed'
                WHERE Or_id = (SELECT Or1_id FROM Invoice WHERE In_id=:1)
            """, [inv_id])

            conn.commit()
            flash("Payment completed!", "success")

        except Exception as e:
            conn.rollback()
            flash(f"Payment error: {e}", "danger")

        return redirect(url_for("customer_payment"))

    cur.execute("""
        SELECT i.In_id, c.C_name, b.BB_name, i.In_amount, i.In_status
        FROM Invoice i
        JOIN Ord o ON i.Or1_id = o.Or_id
        JOIN Customer c ON o.C2_id = c.C_id
        JOIN Bloodbank b ON o.BB4_id = b.BB_id
    """)
    invoices = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return render_template("customer_payment.html", invoices=invoices, headers=headers)
@app.route("/pay_invoice/<int:inv_id>")
def pay_invoice(inv_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Insert payment transaction
        cur.execute("""
            INSERT INTO Transactionstab (
                T_id, T_date, T_time, T_mode, T_status, In1_id
            ) VALUES (
                transaction_seq.NEXTVAL,
                SYSDATE, SYSTIMESTAMP,
                'Online', 'Success', :1
            )
        """, [inv_id])

        # Update invoice → Paid
        cur.execute("""
            UPDATE Invoice
            SET In_status='Paid'
            WHERE In_id=:1
        """, [inv_id])

        # Update order connected to invoice → Completed
        cur.execute("""
            UPDATE Ord
            SET Or_status='Completed'
            WHERE Or_id = (SELECT Or1_id FROM Invoice WHERE In_id=:1)
        """, [inv_id])

        conn.commit()
        flash("💰 Payment Successful!", "success")

    except Exception as e:
        conn.rollback()
        flash(f"❌ Payment Error: {e}", "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(request.referrer or "/")


@app.route("/get_bank/<int:emp_id>")
def get_bank(emp_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.BB_id, b.BB_name
        FROM Employee e
        JOIN Bloodbank b ON e.BB1_id = b.BB_id
        WHERE e.E_id = :1
    """, [emp_id])

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return {"BB_id": row[0], "BB_name": row[1]}
    else:
        return {"error": "Not found"}
@app.route("/history")
def history_page():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch in correct order based on your History table
    cur.execute("""
        SELECT 
            D_name,        -- 0
            D_contact,     -- 1
            D_address,     -- 2
            D_gender,      -- 3
            D_age,         -- 4
            D_bloodtype,   -- 5
            C_name,        -- 6
            C_contact,     -- 7
            C_address,     -- 8
            Hs_name,       -- 9
            Hs_contact,    -- 10
            Hs_address,    -- 11
            BB_name,       -- 12
            Donation_date, -- 13
            Archived_on    -- 14
        FROM History
        ORDER BY Archived_on DESC
    """)

    rows = cur.fetchall()
    headers = [col[0] for col in cur.description]

    cur.close()
    conn.close()

    return render_template(
        "history.html",
        history=rows,
        headers=headers
    )

# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    app.run(debug=True)
