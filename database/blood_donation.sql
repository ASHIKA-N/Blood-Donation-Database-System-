
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE Transactionstab CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE Invoice CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE Ord CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE Appointment CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE Donor CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE Customer CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE Employee CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE BloodStock CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE Bloodbank CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE Hospital CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE Foundation CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE History CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

------------------------------------------------------------
-- 1️⃣ FOUNDATION TABLE
------------------------------------------------------------
CREATE TABLE Foundation (
    F_id      NUMBER PRIMARY KEY,
    F_name    VARCHAR2(50),
    F_address VARCHAR2(255),
    F_contact VARCHAR2(15),
    F_mail_id VARCHAR2(50)
);

CREATE SEQUENCE foundation_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 2️⃣ HOSPITAL TABLE
------------------------------------------------------------
CREATE TABLE Hospital (
    Hs_id      NUMBER PRIMARY KEY,
    Hs_name    VARCHAR2(50),
    Hs_address VARCHAR2(255),
    Hs_contact VARCHAR2(15),
    F1_id      NUMBER,
    CONSTRAINT fk_hospital_foundation
        FOREIGN KEY (F1_id) REFERENCES Foundation(F_id)
);

CREATE SEQUENCE hospital_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 3️⃣ BLOOD BANK TABLE
------------------------------------------------------------
CREATE TABLE Bloodbank (
    BB_id      NUMBER PRIMARY KEY,
    BB_name    VARCHAR2(50),
    BB_address VARCHAR2(255),
    BB_contact VARCHAR2(15),
    BB_volume  NUMBER,
    F2_id      NUMBER,
    CONSTRAINT fk_bloodbank_foundation
        FOREIGN KEY (F2_id) REFERENCES Foundation(F_id)
);

CREATE SEQUENCE bloodbank_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 4️⃣ BLOOD STOCK TABLE
------------------------------------------------------------
CREATE TABLE BloodStock (
    BS_id      NUMBER PRIMARY KEY,
    BB_id      NUMBER,
    Blood_type VARCHAR2(5),
    Quantity   NUMBER,
    CONSTRAINT fk_stock_bloodbank
        FOREIGN KEY (BB_id) REFERENCES Bloodbank(BB_id)
);

CREATE SEQUENCE bloodstock_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 5️⃣ EMPLOYEE TABLE
------------------------------------------------------------
CREATE TABLE Employee (
    E_id          NUMBER PRIMARY KEY,
    E_name        VARCHAR2(50),
    E_address     VARCHAR2(255),
    E_contact     VARCHAR2(15),
    E_age         NUMBER,
    E_designation VARCHAR2(20),
    E_experience  NUMBER,
    BB1_id        NUMBER,
    CONSTRAINT fk_employee_bloodbank
        FOREIGN KEY (BB1_id) REFERENCES Bloodbank(BB_id)
);

CREATE SEQUENCE employee_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 6️⃣ DONOR TABLE
------------------------------------------------------------
CREATE TABLE Donor (
    D_id         NUMBER PRIMARY KEY,
    D_name       VARCHAR2(50),
    D_contact    VARCHAR2(15),
    D_address    VARCHAR2(255),
    D_age        NUMBER,
    D_gender     VARCHAR2(10),
    D_bloodtype  VARCHAR2(5),
    D_history    NUMBER DEFAULT 0,
    BB3_id       NUMBER,
    CONSTRAINT fk_donor_bloodbank 
        FOREIGN KEY (BB3_id) REFERENCES Bloodbank(BB_id)
);

CREATE SEQUENCE donor_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 7️⃣ CUSTOMER TABLE (with FK to HOSPITAL)
------------------------------------------------------------
CREATE TABLE Customer (
    C_id      NUMBER PRIMARY KEY,
    C_name    VARCHAR2(50),
    C_address VARCHAR2(255),
    C_contact VARCHAR2(15),
    C_gender  VARCHAR2(10),
    C_history VARCHAR2(50),
    Hs1_id    NUMBER,
    CONSTRAINT fk_customer_hospital
        FOREIGN KEY (Hs1_id) REFERENCES Hospital(Hs_id)
        ON DELETE SET NULL
);
ALTER TABLE Customer ADD Hs1_id NUMBER(10);
ALTER TABLE Customer ADD CONSTRAINT fk_customer_hospital
    FOREIGN KEY (Hs1_id) REFERENCES Hospital(Hs_id);

CREATE SEQUENCE customer_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 8️⃣ APPOINTMENT TABLE
------------------------------------------------------------
CREATE TABLE Appointment (
    App_id        NUMBER PRIMARY KEY,
    App_date      DATE DEFAULT SYSDATE,
    App_time      TIMESTAMP DEFAULT SYSTIMESTAMP,
    App_status    VARCHAR2(20) DEFAULT 'Pending',
    D1_id         NUMBER,
    BB2_id        NUMBER,
    E2_id         NUMBER,
    C1_id         NUMBER,
    CONSTRAINT fk_appointment_donor 
        FOREIGN KEY (D1_id) REFERENCES Donor(D_id),
    CONSTRAINT fk_appointment_bloodbank 
        FOREIGN KEY (BB2_id) REFERENCES Bloodbank(BB_id),
    CONSTRAINT fk_appointment_employee 
        FOREIGN KEY (E2_id) REFERENCES Employee(E_id),
    CONSTRAINT fk_appointment_customer 
        FOREIGN KEY (C1_id) REFERENCES Customer(C_id)
);

CREATE SEQUENCE appointment_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 9️⃣ ORDER TABLE
------------------------------------------------------------
CREATE TABLE Ord (
    Or_id       NUMBER PRIMARY KEY,
    Or_date     DATE,
    Or_time     TIMESTAMP,
    Or_quantity NUMBER,
    Or_status   VARCHAR2(20),
    Or_type     VARCHAR2(5),
    C2_id       NUMBER,
    Hs2_id      NUMBER,
    BB4_id      NUMBER,
    CONSTRAINT fk_orders_customer FOREIGN KEY (C2_id) REFERENCES Customer(C_id),
    CONSTRAINT fk_orders_hospital FOREIGN KEY (Hs2_id) REFERENCES Hospital(Hs_id),
    CONSTRAINT fk_orders_bloodbank FOREIGN KEY (BB4_id) REFERENCES Bloodbank(BB_id)
);

CREATE SEQUENCE order_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 🔟 INVOICE TABLE
------------------------------------------------------------
CREATE TABLE Invoice (
    In_id     NUMBER PRIMARY KEY,
    In_date   DATE,
    In_time   TIMESTAMP,
    In_amount NUMBER,
    In_status VARCHAR2(20),
    Or1_id    NUMBER,
    CONSTRAINT fk_invoice_ord
        FOREIGN KEY (Or1_id) REFERENCES Ord(Or_id)
);

CREATE SEQUENCE invoice_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 1️⃣1️⃣ TRANSACTION TABLE
------------------------------------------------------------
CREATE TABLE Transactionstab (
    T_id     NUMBER PRIMARY KEY,
    T_date   DATE,
    T_time   TIMESTAMP,
    T_mode   VARCHAR2(20),
    T_status VARCHAR2(20),
    In1_id   NUMBER,
    CONSTRAINT fk_transaction_invoice 
        FOREIGN KEY (In1_id) REFERENCES Invoice(In_id)
);

CREATE SEQUENCE transaction_seq START WITH 1 INCREMENT BY 1;

------------------------------------------------------------
-- 1️⃣2️⃣ HISTORY TABLE
------------------------------------------------------------
CREATE TABLE History (
    H_id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    D_name VARCHAR2(50),
    D_contact VARCHAR2(15),
    D_address VARCHAR2(255),
    D_gender VARCHAR2(10),
    D_age NUMBER,
    D_bloodtype VARCHAR2(5),
    C_name VARCHAR2(50),
    C_contact VARCHAR2(15),
    C_address VARCHAR2(255),
    Hs_name VARCHAR2(50),
    Hs_contact VARCHAR2(15),
    Hs_address VARCHAR2(255),
    BB_name VARCHAR2(50),
    Donation_date DATE,
    Archived_on TIMESTAMP
);

------------------------------------------------------------
-- ✅ END OF FILE
------------------------------------------------------------

COMMIT;
