from flask import Flask, render_template, request, redirect, url_for, flash
import oracledb

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
# INDEX
# --------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------------
# FOUNDATION DASHBOARD (ADD + VIEW)
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
            cursor.execute(
                """
                INSERT INTO Foundation (F_id, F_name, F_address, F_contact, F_mail_id)
                VALUES (foundation_seq.NEXTVAL, :1, :2, :3, :4)
                """,
                (name, address, contact, email),
            )
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
# HOSPITAL DASHBOARD (ADD + VIEW + VIEW ORDERS)
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
            cursor.execute(
                """
                INSERT INTO Hospital (Hs_id, Hs_name, Hs_address, Hs_contact, F1_id)
                VALUES (hospital_seq.NEXTVAL, :1, :2, :3, :4)
                """,
                (name, address, contact, f_id),
            )
            conn.commit()
            flash("✅ Hospital added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding hospital: {e}")

    cursor.execute("SELECT * FROM Hospital ORDER BY Hs_id")
    hospitals = [
        dict(zip([c[0] for c in cursor.description], row))
        for row in cursor.fetchall()
    ]

    cursor.execute(
        """
        SELECT o.Or_id,
               h.Hs_name,
               c.C_name,
               b.BB_name,
               o.Or_type,
               o.Or_quantity,
               o.Or_status
        FROM Ord o
        JOIN Hospital h ON o.Hs2_id = h.Hs_id
        JOIN Customer c ON o.C2_id = c.C_id
        JOIN Bloodbank b ON o.BB4_id = b.BB_id
        ORDER BY o.Or_id
        """
    )
    orders = [
        dict(zip([c[0] for c in cursor.description], row))
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()
    return render_template("hospital.html", hospitals=hospitals, orders=orders)


# --------------------------------------------------------
# HOSPITAL PLACES BLOOD ORDER  (NO INVOICE HERE)
# --------------------------------------------------------
@app.route("/hospital_order", methods=["POST"])
def hospital_order():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        hs_id = request.form.get("Hs2_id")
        c_id = request.form.get("C2_id")
        bb_id = request.form.get("BB4_id")
        btype = request.form.get("Or_type")
        qty = float(request.form.get("Or_quantity"))

        cur.execute("SELECT order_seq.NEXTVAL FROM dual")
        order_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO Ord (
                Or_id, Or_date, Or_time, Or_quantity,
                Or_status, Or_type, C2_id, Hs2_id, BB4_id
            )
            VALUES (:1, SYSDATE, SYSTIMESTAMP, :2,
                    'Pending', :3, :4, :5, :6)
            """,
            (order_id, qty, btype, c_id, hs_id, bb_id),
        )

        conn.commit()
        flash(f"✅ Order #{order_id} placed successfully! Pending at Employee side.")

    except Exception as e:
        conn.rollback()
        flash(f"❌ Error placing hospital order: {e}")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("hospital_dashboard"))


# --------------------------------------------------------
# HOSPITAL PAYS INVOICE
# --------------------------------------------------------
@app.route("/hospital_payment", methods=["GET", "POST"])
def hospital_payment():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        invoice_id = request.form.get("In_id")
        amount = float(request.form.get("amount"))
        method = request.form.get("method")

        try:
            cur.execute(
                """
                INSERT INTO Transactionstab (T_id, T_date, T_time, T_mode, T_status, In1_id)
                VALUES (transaction_seq.NEXTVAL, SYSDATE, SYSTIMESTAMP, :1, 'Success', :2)
                """,
                (method, invoice_id),
            )

            cur.execute(
                "UPDATE Invoice SET In_status = 'Paid' WHERE In_id = :1",
                [invoice_id],
            )

            cur.execute(
                """
                UPDATE Ord
                SET Or_status = 'Completed'
                WHERE Or_id = (SELECT Or1_id FROM Invoice WHERE In_id = :1)
                """,
                [invoice_id],
            )

            conn.commit()
            flash(f"✅ Payment of ₹{amount} via {method} completed successfully!")

        except Exception as e:
            conn.rollback()
            flash(f"❌ Payment failed: {e}")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("hospital_payment"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT i.In_id, h.Hs_name, b.BB_name, i.In_amount, i.In_status
        FROM Invoice i
        JOIN Ord o ON i.Or1_id = o.Or_id
        JOIN Hospital h ON o.Hs2_id = h.Hs_id
        JOIN Bloodbank b ON o.BB4_id = b.BB_id
        ORDER BY i.In_id
        """
    )
    invoices = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()
    return render_template("hospital_payment.html", invoices=invoices, headers=headers)


# --------------------------------------------------------
# BLOOD BANK DASHBOARD
# --------------------------------------------------------
@app.route("/bloodbank", methods=["GET", "POST"])
def bloodbank_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST" and "BB_name" in request.form:
        name = request.form.get("BB_name")
        address = request.form.get("BB_address")
        contact = request.form.get("BB_contact")
        volume = request.form.get("BB_volume")
        btype = request.form.get("BB_type")
        f_id = request.form.get("F2_id")
        try:
            cursor.execute(
                """
                INSERT INTO Bloodbank (BB_id, BB_name, BB_address, BB_contact,
                                       BB_volume, BB_type, F2_id)
                VALUES (bloodbank_seq.NEXTVAL, :1, :2, :3, :4, :5, :6)
                """,
                (name, address, contact, volume, btype, f_id),
            )
            conn.commit()
            flash("✅ Blood bank added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding blood bank: {e}")

    cursor.execute("SELECT BB_id, BB_name FROM Bloodbank ORDER BY BB_id")
    bloodbanks = cursor.fetchall()

    cursor.execute("SELECT * FROM Bloodbank ORDER BY BB_id")
    banks = [
        dict(zip([c[0] for c in cursor.description], row))
        for row in cursor.fetchall()
    ]

    cursor.execute(
        """
        SELECT e.E_id, e.E_name, e.E_designation, e.E_experience, e.E_contact, b.BB_name
        FROM Employee e
        JOIN Bloodbank b ON e.BB1_id = b.BB_id
        ORDER BY e.E_id
        """
    )
    employees = cursor.fetchall()
    e_headers = [desc[0] for desc in cursor.description]

    cursor.close()
    conn.close()

    return render_template(
        "bloodbank.html",
        banks=banks,
        bloodbanks=bloodbanks,
        employees=employees,
        e_headers=e_headers,
    )


# --------------------------------------------------------
# ADD EMPLOYEE TO BLOOD BANK
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

        cursor.execute(
            """
            INSERT INTO Employee (E_id, E_name, E_address, E_contact, E_age,
                                  E_designation, E_experience, BB1_id)
            VALUES (employee_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, :7)
            """,
            (e_name, e_address, e_contact, e_age, e_designation, e_exp, bb_id),
        )
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
# EMPLOYEE DASHBOARD
# --------------------------------------------------------
@app.route("/employee", methods=["GET", "POST"])
def employee_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    # 1) Schedule Appointment
    if request.method == "POST" and "D1_id" in request.form:
        cur.execute(
            """
            INSERT INTO Appointment (App_id, App_date, App_status,
                                     D1_id, C1_id, E2_id, BB2_id)
            VALUES (appointment_seq.NEXTVAL, TO_DATE(:1, 'YYYY-MM-DD'),
                    'Pending', :2, :3, :4, :5)
            """,
            [
                request.form["App_date"],
                request.form["D1_id"],
                request.form["C1_id"],
                request.form["E2_id"],
                request.form["BB2_id"],
            ],
        )
        conn.commit()
        flash("✅ Appointment scheduled successfully!")

    # 2) Mark Appointment as Completed & Archive
    if request.method == "POST" and "App_status" in request.form:
        app_id = request.form["App_id"]
        new_status = request.form["App_status"]

        try:
            cur.execute(
                "UPDATE Appointment SET App_status = :1 WHERE App_id = :2",
                [new_status, app_id],
            )
            conn.commit()

            if new_status.lower() == "completed":
                # Fetch donor + customer + hospital info
                cur.execute(
                    """
                    SELECT
                        D.D_name, D.D_contact, D.D_address, D.D_gender, D.D_age,
                        C.C_name, C.C_contact, C.C_address,
                        H.Hs_name, H.Hs_contact, H.Hs_address,
                        A.App_date
                    FROM Appointment A
                    JOIN Donor D ON A.D1_id = D.D_id
                    JOIN Customer C ON A.C1_id = C.C_id
                    LEFT JOIN Hospital H ON C.C_id = H.Hs_id
                    WHERE A.App_id = :1
                    """,
                    [app_id],
                )
                rec = cur.fetchone()

                if rec:
                    # Insert into History
                    cur.execute(
                        """
                        INSERT INTO History (
                            D_name, D_contact, D_address, D_gender, D_age,
                            C_name, C_contact, C_address,
                            Hs_name, Hs_contact, Hs_address,
                            Donation_date, Archived_on
                        ) VALUES (
                            :1,:2,:3,:4,:5,
                            :6,:7,:8,
                            :9,:10,:11,
                            :12, SYSTIMESTAMP
                        )
                        """,
                        rec,
                    )

                    # SOFT ARCHIVE → do not delete anything!

                    conn.commit()
                    flash("✅ Donation completed — archived to history!")

        except Exception as e:
            conn.rollback()
            flash(f"❌ Error completing appointment: {e}")

    # 3) Fetch dropdown data
    cur.execute("SELECT E_id, E_name, BB1_id FROM Employee ORDER BY E_id")
    employees = cur.fetchall()

    cur.execute("SELECT BB_id, BB_name FROM Bloodbank ORDER BY BB_id")
    bloodbanks = cur.fetchall()

    cur.execute("SELECT D_id, D_name, D_contact FROM Donor ORDER BY D_id")
    donors = cur.fetchall()

    cur.execute("SELECT C_id, C_name, C_contact FROM Customer ORDER BY C_id")
    customers = cur.fetchall()

    # Appointment list
    cur.execute(
        """
        SELECT A.App_id, D.D_name, C.C_name, B.BB_name, E.E_name,
               A.App_date, A.App_status
        FROM Appointment A
        JOIN Donor D ON A.D1_id = D.D_id
        JOIN Customer C ON A.C1_id = C.C_id
        JOIN Employee E ON A.E2_id = E.E_id
        JOIN Bloodbank B ON A.BB2_id = B.BB_id
        ORDER BY A.App_id
        """
    )
    appointments = cur.fetchall()

    # Pending orders
    cur.execute(
        """
        SELECT
            o.Or_id,
            CASE
                WHEN c.C_name IS NOT NULL THEN c.C_name
                WHEN h.Hs_name IS NOT NULL THEN h.Hs_name
                ELSE 'Unknown Requester'
            END AS Requester_Name,
            b.BB_name,
            o.Or_type,
            o.Or_quantity,
            o.Or_status
        FROM Ord o
        LEFT JOIN Customer c ON o.C2_id = c.C_id
        LEFT JOIN Hospital h ON o.Hs2_id = h.Hs_id
        JOIN Bloodbank b ON o.BB4_id = b.BB_id
        WHERE o.Or_status = 'Pending'
        ORDER BY o.Or_id
        """
    )
    orders = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "employee.html",
        employees=employees,
        bloodbanks=bloodbanks,
        donors=donors,
        customers=customers,
        appointments=appointments,
        orders=orders,
    )

# --------------------------------------------------------
# DONOR DASHBOARD
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
            cursor.execute(
                """
                INSERT INTO Donor (
                    D_id, D_name, D_contact, D_address,
                    D_age, D_gender, D_history, BB3_id
                )
                VALUES (donor_seq.NEXTVAL, :1, :2, :3, :4, :5, 0, :6)
                """,
                (name, contact, address, age, gender, bb_id),
            )
            conn.commit()
            flash("✅ Donor added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding donor: {e}")

    cursor.execute("SELECT * FROM Donor ORDER BY D_id")
    donors = [
        dict(zip([c[0] for c in cursor.description], row))
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()
    return render_template("donor.html", donors=donors)


# --------------------------------------------------------
# EMPLOYEE GENERATES INVOICE (BOTH CUSTOMER + HOSPITAL ORDERS)
# --------------------------------------------------------
@app.route("/create_invoice", methods=["POST"])
def create_invoice():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        order_id = request.form.get("Or_id")
        price_chart = {"A+": 25, "B+": 25, "AB+": 30, "O+": 20, "O-": 35}

        cur.execute(
            "SELECT Or_quantity, Or_type FROM Ord WHERE Or_id = :1", [order_id]
        )
        result = cur.fetchone()
        if not result:
            flash("❌ Invalid Order ID.")
            return redirect(url_for("employee_dashboard"))

        qty, btype = result
        total = float(qty) * price_chart.get(btype, 25)

        cur.execute("SELECT invoice_seq.NEXTVAL FROM dual")
        invoice_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO Invoice (In_id, In_date, In_time, In_amount, In_status, Or1_id)
            VALUES (:1, SYSDATE, SYSTIMESTAMP, :2, 'Generated', :3)
            """,
            (invoice_id, total, order_id),
        )

        cur.execute(
            "UPDATE Ord SET Or_status = 'Invoiced' WHERE Or_id = :1",
            [order_id],
        )

        conn.commit()
        flash(f"✅ Invoice #{invoice_id} generated for Order #{order_id} | ₹{total}")

    except Exception as e:
        conn.rollback()
        flash(f"❌ Error creating invoice: {e}")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("employee_dashboard"))


# --------------------------------------------------------
# CUSTOMER DASHBOARD
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
            cursor.execute(
                """
                INSERT INTO Customer (C_id, C_name, C_address,
                                      C_contact, C_gender, C_history)
                VALUES (customer_seq.NEXTVAL, :1, :2, :3, :4, :5)
                """,
                (name, address, contact, gender, history),
            )
            conn.commit()
            flash("✅ Customer added successfully!")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding customer: {e}")

    cursor.execute("SELECT * FROM Customer ORDER BY C_id")
    customers = [
        dict(zip([c[0] for c in cursor.description], row))
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()
    return render_template("customer.html", customers=customers)


# --------------------------------------------------------
# CUSTOMER CREATES BLOOD REQUEST
# --------------------------------------------------------
@app.route("/create_order", methods=["POST"])
def create_order():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        c_id = request.form.get("C2_id")
        bb_id = request.form.get("BB4_id")
        btype = request.form.get("Or_type")
        quantity = float(request.form.get("Or_quantity"))

        cur.execute("SELECT order_seq.NEXTVAL FROM dual")
        order_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO Ord (Or_id, Or_date, Or_time, Or_quantity,
                             Or_status, Or_type, C2_id, BB4_id)
            VALUES (:1, SYSDATE, SYSTIMESTAMP, :2,
                    'Pending', :3, :4, :5)
            """,
            (order_id, quantity, btype, c_id, bb_id),
        )
        conn.commit()
        flash(f"🩸 Blood request (Order #{order_id}) sent to Blood Bank!")

    except Exception as e:
        conn.rollback()
        flash(f"❌ Error creating order: {e}")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("customer_dashboard"))


# --------------------------------------------------------
# CUSTOMER PAYMENT PAGE
# --------------------------------------------------------
@app.route("/customer_payment", methods=["GET", "POST"])
def customer_payment():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        invoice_id = request.form.get("In_id")
        amount = float(request.form.get("amount"))
        method = request.form.get("method")

        try:
            cur.execute(
                """
                INSERT INTO Transactionstab (T_id, T_date, T_time, T_mode, T_status, In1_id)
                VALUES (transaction_seq.NEXTVAL, SYSDATE, SYSTIMESTAMP, :1, 'Success', :2)
                """,
                (method, invoice_id),
            )

            cur.execute(
                "UPDATE Invoice SET In_status = 'Paid' WHERE In_id = :1",
                [invoice_id],
            )

            cur.execute(
                """
                UPDATE Ord SET Or_status = 'Completed'
                WHERE Or_id = (SELECT Or1_id FROM Invoice WHERE In_id = :1)
                """,
                [invoice_id],
            )

            conn.commit()
            flash(f"✅ Payment of ₹{amount} via {method} completed successfully!")

        except Exception as e:
            conn.rollback()
            flash(f"❌ Payment failed: {e}")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("customer_payment"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT i.In_id,
               c.C_name,
               b.BB_name,
               i.In_amount,
               i.In_status
        FROM Invoice i
        JOIN Ord o ON i.Or1_id = o.Or_id
        JOIN Customer c ON o.C2_id = c.C_id
        JOIN Bloodbank b ON o.BB4_id = b.BB_id
        WHERE o.C2_id IS NOT NULL
        ORDER BY i.In_id
        """
    )
    invoices = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()
    return render_template("customer_payment.html", invoices=invoices, headers=headers)


# --------------------------------------------------------
# ADMIN DASHBOARD
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

    cursor.execute("SELECT COUNT(*) FROM History")
    completed = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        "admin.html",
        donors=donors,
        hospitals=hospitals,
        volume=volume,
        completed=completed,
    )


# --------------------------------------------------------
# DONATION HISTORY PAGE
# --------------------------------------------------------
@app.route("/history")
def view_history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT H_id, D_name, D_contact,
               C_name, C_contact,
               Hs_name,
               Donation_date, Archived_on
        FROM History
        ORDER BY H_id DESC
        """
    )
    records = cur.fetchall()
    headers = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return render_template("history.html", headers=headers, records=records)


# --------------------------------------------------------
# ROLE SELECTION HANDLER
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
        "customer": "customer_dashboard",
    }
    return redirect(url_for(routes.get(role, "index")))


# --------------------------------------------------------
# GENERIC ORDER PAYMENT PAGE (OPTIONAL EXTRA)
# --------------------------------------------------------
@app.route("/order_payment", methods=["GET", "POST"])
def order_payment():
    conn = get_db_connection()
    cur = conn.cursor()

    price_chart = {"A+": 25, "B+": 25, "AB+": 30, "O+": 20, "O-": 35}

    if request.method == "POST":
        order_id = request.form.get("order_id")
        payment_mode = request.form.get("T_mode")

        try:
            cur.execute(
                "SELECT Or_id, Or_type, Or_quantity, Or_status FROM Ord WHERE Or_id = :1",
                [order_id],
            )
            order = cur.fetchone()

            if not order:
                flash("❌ Invalid Order ID.")
                conn.close()
                return redirect(url_for("order_payment"))

            or_id, or_type, or_quantity, or_status = order

            if or_status == "Paid":
                flash("⚠️ This order is already paid.")
                conn.close()
                return redirect(url_for("order_payment"))

            total = float(or_quantity) * price_chart.get(or_type, 25)

            cur.execute("SELECT invoice_seq.NEXTVAL FROM dual")
            invoice_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO Invoice (In_id, In_date, In_time, In_amount, In_status, Or1_id)
                VALUES (:1, SYSDATE, SYSTIMESTAMP, :2, 'Paid', :3)
                """,
                (invoice_id, total, or_id),
            )

            cur.execute(
                """
                INSERT INTO Transactionstab (T_id, T_date, T_time, T_mode, T_status, In1_id)
                VALUES (transaction_seq.NEXTVAL, SYSDATE, SYSTIMESTAMP, :1, 'Success', :2)
                """,
                (payment_mode, invoice_id),
            )

            cur.execute(
                "UPDATE Ord SET Or_status = 'Paid' WHERE Or_id = :1",
                [order_id],
            )

            conn.commit()
            flash(
                f"✅ Payment successful! ₹{total} paid for Order #{order_id} via {payment_mode}."
            )

        except Exception as e:
            conn.rollback()
            flash(f"❌ Error during payment: {e}")

    cur.execute(
        """
        SELECT o.Or_id, o.Or_type, o.Or_quantity, o.Or_status,
               i.In_id, i.In_amount, t.T_mode, t.T_status
        FROM Ord o
        LEFT JOIN Invoice i ON i.Or1_id = o.Or_id
        LEFT JOIN Transactionstab t ON t.In1_id = i.In_id
        ORDER BY o.Or_id
        """
    )
    records = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()
    return render_template("order_payment.html", headers=headers, records=records)


# --------------------------------------------------------
# RUN
# --------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
