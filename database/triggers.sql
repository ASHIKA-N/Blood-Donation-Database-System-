

------------------------------------------------------------
-- 🧹 Safe-Drop Utilities (allow re-execution)
------------------------------------------------------------
BEGIN FOR s IN (SELECT sequence_name FROM user_sequences WHERE sequence_name LIKE '%SEQ%')
LOOP EXECUTE IMMEDIATE 'DROP SEQUENCE '||s.sequence_name; END LOOP; END;
/
BEGIN FOR t IN (SELECT trigger_name FROM user_triggers WHERE trigger_name LIKE 'TRG_%')
LOOP EXECUTE IMMEDIATE 'DROP TRIGGER '||t.trigger_name; END LOOP; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE Donor_Audit CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE Appointment_Audit CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 1️⃣ Donor History Update after Completed Appointment
------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_update_donor_history
AFTER UPDATE OF App_status ON Appointment
FOR EACH ROW
BEGIN
    IF :NEW.App_status = 'Completed' AND :OLD.App_status <> 'Completed' THEN
        UPDATE Donor
        SET D_history = NVL(D_history, 0) + 1
        WHERE D_id = :NEW.D1_id;
    END IF;
END;
/

------------------------------------------------------------

------------------------------------------------------------
-- 2️⃣ Order Status Update when Invoice Created
------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_invoice_mark_order
AFTER INSERT ON Invoice
FOR EACH ROW
BEGIN
    UPDATE Ord
    SET Or_status = 'Billed'
    WHERE Or_id = :NEW.Or1_id;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 3️⃣ Invoice Status Update when Transaction Succeeds
------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_invoice_paid
AFTER INSERT ON Transactionstab
FOR EACH ROW
BEGIN
    IF :NEW.T_status = 'Success' THEN
        UPDATE Invoice
        SET In_status = 'Paid'
        WHERE In_id = :NEW.In1_id;
    END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 4️⃣ Appointment ID Auto-Increment
------------------------------------------------------------
CREATE SEQUENCE appointment_seq START WITH 601 INCREMENT BY 1 NOCACHE NOCYCLE;
/
CREATE OR REPLACE TRIGGER trg_appointment_id
BEFORE INSERT ON Appointment
FOR EACH ROW
BEGIN
  IF :NEW.App_id IS NULL THEN
    SELECT appointment_seq.NEXTVAL INTO :NEW.App_id FROM dual;
  END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 5️⃣ Donor ID Auto-Increment
------------------------------------------------------------
CREATE SEQUENCE donor_seq START WITH 501 INCREMENT BY 1 NOCACHE NOCYCLE;
/
CREATE OR REPLACE TRIGGER trg_donor_id
BEFORE INSERT ON Donor
FOR EACH ROW
BEGIN
  IF :NEW.D_id IS NULL THEN
    SELECT donor_seq.NEXTVAL INTO :NEW.D_id FROM dual;
  END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 6️⃣ BloodBank ID Auto-Increment
------------------------------------------------------------
CREATE SEQUENCE bloodbank_seq START WITH 301 INCREMENT BY 1 NOCACHE NOCYCLE;
/
CREATE OR REPLACE TRIGGER trg_bloodbank_id
BEFORE INSERT ON Bloodbank
FOR EACH ROW
BEGIN
  IF :NEW.BB_id IS NULL THEN
    SELECT bloodbank_seq.NEXTVAL INTO :NEW.BB_id FROM dual;
  END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 7️⃣ Customer ID Auto-Increment
------------------------------------------------------------
CREATE SEQUENCE customer_seq START WITH 401 INCREMENT BY 1 NOCACHE NOCYCLE;
/
CREATE OR REPLACE TRIGGER trg_customer_id
BEFORE INSERT ON Customer
FOR EACH ROW
BEGIN
  IF :NEW.C_id IS NULL THEN
    SELECT customer_seq.NEXTVAL INTO :NEW.C_id FROM dual;
  END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 8️⃣ Hospital ID Auto-Increment
------------------------------------------------------------
CREATE SEQUENCE hospital_seq START WITH 101 INCREMENT BY 1 NOCACHE NOCYCLE;
/
CREATE OR REPLACE TRIGGER trg_hospital_id
BEFORE INSERT ON Hospital
FOR EACH ROW
BEGIN
  IF :NEW.Hs_id IS NULL THEN
    SELECT hospital_seq.NEXTVAL INTO :NEW.Hs_id FROM dual;
  END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 9️⃣ Employee ID Auto-Increment
------------------------------------------------------------
CREATE SEQUENCE employee_seq START WITH 201 INCREMENT BY 1 NOCACHE NOCYCLE;
/
CREATE OR REPLACE TRIGGER trg_employee_id
BEFORE INSERT ON Employee
FOR EACH ROW
BEGIN
  IF :NEW.E_id IS NULL THEN
    SELECT employee_seq.NEXTVAL INTO :NEW.E_id FROM dual;
  END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 🔟 Order ID Auto-Increment
------------------------------------------------------------
CREATE SEQUENCE ord_seq START WITH 701 INCREMENT BY 1 NOCACHE NOCYCLE;
/
CREATE OR REPLACE TRIGGER trg_ord_id
BEFORE INSERT ON Ord
FOR EACH ROW
BEGIN
  IF :NEW.Or_id IS NULL THEN
    SELECT ord_seq.NEXTVAL INTO :NEW.Or_id FROM dual;
  END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 1️⃣1️⃣ Invoice ID Auto-Increment
------------------------------------------------------------
CREATE SEQUENCE invoice_seq START WITH 801 INCREMENT BY 1 NOCACHE NOCYCLE;
/
CREATE OR REPLACE TRIGGER trg_invoice_id
BEFORE INSERT ON Invoice
FOR EACH ROW
BEGIN
  IF :NEW.In_id IS NULL THEN
    SELECT invoice_seq.NEXTVAL INTO :NEW.In_id FROM dual;
  END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 1️⃣2️⃣ Transaction ID Auto-Increment
------------------------------------------------------------
CREATE SEQUENCE transaction_seq START WITH 901 INCREMENT BY 1 NOCACHE NOCYCLE;
/
CREATE OR REPLACE TRIGGER trg_transaction_id
BEFORE INSERT ON Transactionstab
FOR EACH ROW
BEGIN
  IF :NEW.T_id IS NULL THEN
    SELECT transaction_seq.NEXTVAL INTO :NEW.T_id FROM dual;
  END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 1️⃣3️⃣ Default Status for Orders
------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_default_order_status
BEFORE INSERT ON Ord
FOR EACH ROW
BEGIN
  IF :NEW.Or_status IS NULL THEN
    :NEW.Or_status := 'Pending';
  END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 1️⃣4️⃣ Validate Donor Age & Donation Limit
------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_prevent_invalid_donation
BEFORE INSERT OR UPDATE ON Appointment
FOR EACH ROW
DECLARE
    v_age Donor.D_age%TYPE;
    v_history Donor.D_history%TYPE;
BEGIN
    SELECT D_age, D_history INTO v_age, v_history
    FROM Donor WHERE D_id = :NEW.D1_id;

    IF v_age < 18 OR v_age > 65 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Donor age not eligible.');
    END IF;

    IF v_history >= 10 THEN
        RAISE_APPLICATION_ERROR(-20002, 'Donor has reached max donation limit.');
    END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 1️⃣5️⃣ Update BloodBank Stock on Donation Completion
------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_update_blood_stock
AFTER UPDATE OF App_status ON Appointment
FOR EACH ROW
WHEN (NEW.App_status = 'Completed' AND OLD.App_status != 'Completed')
BEGIN
    UPDATE Bloodbank
    SET BB_volume = NVL(BB_volume,0) + 1
    WHERE BB_id = :NEW.BB2_id;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 1️⃣6️⃣ Prevent Duplicate Donor Registrations
------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_prevent_duplicate_donor
BEFORE INSERT ON Donor
FOR EACH ROW
DECLARE v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM Donor WHERE D_contact = :NEW.D_contact;
    IF v_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20003, 'Duplicate donor contact detected.');
    END IF;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 1️⃣7️⃣ Donor Registration Audit
------------------------------------------------------------
CREATE TABLE Donor_Audit (
    Audit_id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    D_id NUMBER, D_name VARCHAR2(15), D_contact NUMBER(10),
    D_address VARCHAR2(255), D_age NUMBER(3), D_gender VARCHAR2(6),
    D_history NUMBER(10), BB3_id NUMBER(10), App1_id NUMBER(10),
    Registration_date TIMESTAMP DEFAULT SYSTIMESTAMP
);
/
CREATE OR REPLACE TRIGGER trg_donor_audit
AFTER INSERT ON Donor
FOR EACH ROW
BEGIN
    INSERT INTO Donor_Audit (D_id,D_name,D_contact,D_address,D_age,D_gender,
                             D_history,BB3_id,App1_id)
    VALUES (:NEW.D_id,:NEW.D_name,:NEW.D_contact,:NEW.D_address,
            :NEW.D_age,:NEW.D_gender,:NEW.D_history,:NEW.BB3_id,:NEW.App1_id);
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 1️⃣8️⃣ Appointment Status Audit
------------------------------------------------------------
CREATE TABLE Appointment_Audit (
    Audit_id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    App_id NUMBER, Old_status VARCHAR2(10),
    New_status VARCHAR2(10),
    Updated_at TIMESTAMP DEFAULT SYSTIMESTAMP
);
/
CREATE OR REPLACE TRIGGER trg_appointment_audit
AFTER UPDATE OF App_status ON Appointment
FOR EACH ROW
BEGIN
    INSERT INTO Appointment_Audit (App_id,Old_status,New_status)
    VALUES (:OLD.App_id,:OLD.App_status,:NEW.App_status);
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 1️⃣9️⃣ Update Hospital Order Count
------------------------------------------------------------
BEGIN EXECUTE IMMEDIATE 'ALTER TABLE Hospital DROP COLUMN Hs_order_count';
EXCEPTION WHEN OTHERS THEN NULL; END;
/
ALTER TABLE Hospital ADD (Hs_order_count NUMBER DEFAULT 0);
/
CREATE OR REPLACE TRIGGER trg_update_hospital_orders
AFTER INSERT ON Ord
FOR EACH ROW
BEGIN
    UPDATE Hospital
    SET Hs_order_count = NVL(Hs_order_count,0) + 1
    WHERE Hs_id = :NEW.Hs2_id;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 2️⃣0️⃣ Auto-delete Appointments on Donor Deletion
------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_delete_appointments_on_donor_delete
AFTER DELETE ON Donor
FOR EACH ROW
BEGIN
    DELETE FROM Appointment WHERE D1_id = :OLD.D_id;
END;
/
------------------------------------------------------------

------------------------------------------------------------
-- 2️⃣1️⃣ Auto-set Timestamps for Invoice & Transaction
------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_auto_invoice_time
BEFORE INSERT ON Invoice
FOR EACH ROW
BEGIN
    IF :NEW.In_date IS NULL THEN :NEW.In_date := SYSDATE; END IF;
    IF :NEW.In_time IS NULL THEN :NEW.In_time := SYSTIMESTAMP; END IF;
END;
/
CREATE OR REPLACE TRIGGER trg_auto_transaction_time
BEFORE INSERT ON Transactionstab
FOR EACH ROW
BEGIN
    IF :NEW.T_date IS NULL THEN :NEW.T_date := SYSDATE; END IF;
    IF :NEW.T_time IS NULL THEN :NEW.T_time := SYSTIMESTAMP; END IF;
END;
/

CREATE SEQUENCE appointment_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER trg_appointment_id
BEFORE INSERT ON Appointment
FOR EACH ROW
BEGIN
    IF :NEW.App_id IS NULL THEN
        SELECT appointment_seq.NEXTVAL INTO :NEW.App_id FROM dual;
    END IF;
END;
/
CREATE SEQUENCE foundation_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE hospital_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE bloodbank_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE employee_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE donor_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE customer_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE appointment_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE order_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE invoice_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE transaction_seq START WITH 1 INCREMENT BY 1;



COMMIT;



------------------------------------------------------------

COMMIT;
------------------------------------------------------------
-- ✅ END OF COMPLETE TRIGGERS.SQL
------------------------------------------------------------
