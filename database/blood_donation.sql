--------------------------------------------------------
-- FOUNDATION TABLE
--------------------------------------------------------
CREATE TABLE Foundation (
    F_id      NUMBER(10),
    F_name    VARCHAR2(15),
    F_address VARCHAR2(255),
    F_contact NUMBER(10),
    F_mail_id VARCHAR2(50),
    PRIMARY KEY(F_id)
);

--------------------------------------------------------
-- HOSPITAL TABLE
--------------------------------------------------------
CREATE TABLE Hospital (
    Hs_id      NUMBER(10),
    Hs_name    VARCHAR2(15),
    Hs_address VARCHAR2(255),
    Hs_contact NUMBER(10),
    F1_id      NUMBER(10),
    PRIMARY KEY(Hs_id),
    CONSTRAINT fk_hospital_foundation
        FOREIGN KEY (F1_id) REFERENCES Foundation(F_id)
);

--------------------------------------------------------
-- BLOOD BANK TABLE
--------------------------------------------------------
CREATE TABLE Bloodbank (
    BB_id      NUMBER(10),
    BB_name    VARCHAR2(15),
    BB_address VARCHAR2(255),
    BB_contact NUMBER(10),
    BB_volume  NUMBER(5),
    BB_type    VARCHAR2(2),
    Hs1_id     NUMBER(10),
    F2_id      NUMBER(10),
    PRIMARY KEY(BB_id),
    CONSTRAINT fk_bloodbank_foundation FOREIGN KEY (F2_id) REFERENCES Foundation(F_id),
    CONSTRAINT fk_bloodbank_hospital FOREIGN KEY (Hs1_id) REFERENCES Hospital(Hs_id)
);

--------------------------------------------------------
-- EMPLOYEE TABLE
--------------------------------------------------------
CREATE TABLE Employee (
    E_id          NUMBER(10),
    E_name        VARCHAR2(15),
    E_address     VARCHAR2(255),
    E_contact     NUMBER(10),
    E_age         NUMBER(2),
    E_designation VARCHAR2(10),
    E_experience  NUMBER(2),
    BB1_id        NUMBER(10),
    PRIMARY KEY(E_id),
    CONSTRAINT fk_employee_bloodbank FOREIGN KEY (BB1_id) REFERENCES Bloodbank(BB_id)
);

--------------------------------------------------------
-- DONOR TABLE
--------------------------------------------------------
CREATE TABLE Donor (
    D_id      NUMBER(10),
    D_name    VARCHAR2(15),
    D_contact NUMBER(10),
    D_address VARCHAR2(255),
    D_age     NUMBER(3),
    D_gender  VARCHAR2(6),
    D_history NUMBER(10),
    BB3_id    NUMBER(10),
    App1_id   NUMBER(10),
    PRIMARY KEY(D_id),
    CONSTRAINT fk_donor_bloodbank FOREIGN KEY (BB3_id) REFERENCES Bloodbank(BB_id)
);

--------------------------------------------------------
-- CUSTOMER TABLE
--------------------------------------------------------
CREATE TABLE Customer (
    C_id      NUMBER(10),
    C_name    VARCHAR2(15),
    C_address VARCHAR2(255),
    C_contact NUMBER(10),
    C_gender  VARCHAR2(6),
    C_history VARCHAR2(50),
    PRIMARY KEY(C_id)
);


--------------------------------------------------------
-- APPOINTMENT TABLE (FINAL)
--------------------------------------------------------
CREATE TABLE Appointment (
    App_id        NUMBER(10),
    App_date      DATE DEFAULT SYSDATE,
    App_time      TIMESTAMP DEFAULT SYSTIMESTAMP,
    App_status    VARCHAR2(20) DEFAULT 'Pending',
    D1_id         NUMBER(10),
    BB2_id        NUMBER(10),
    E2_id         NUMBER(10),
    C1_id         NUMBER(10),
    PRIMARY KEY (App_id),
    CONSTRAINT fk_appointment_donor 
        FOREIGN KEY (D1_id) REFERENCES Donor(D_id),
    CONSTRAINT fk_appointment_bloodbank 
        FOREIGN KEY (BB2_id) REFERENCES Bloodbank(BB_id),
    CONSTRAINT fk_appointment_employee 
        FOREIGN KEY (E2_id) REFERENCES Employee(E_id),
    CONSTRAINT fk_appointment_customer 
        FOREIGN KEY (C1_id) REFERENCES Customer(C_id)
);


--------------------------------------------------------
-- ORDER TABLE
--------------------------------------------------------
CREATE TABLE Ord (
    Or_id       NUMBER(10),
    Or_date     DATE,
    Or_time     TIMESTAMP,
    Or_quantity NUMBER(10),
    Or_status   VARCHAR2(10),
    Or_type     VARCHAR2(3),
    C2_id       NUMBER(10),
    Hs2_id      NUMBER(10),
    BB4_id      NUMBER(10),
    PRIMARY KEY(Or_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (C2_id) REFERENCES Customer(C_id),
    CONSTRAINT fk_orders_hospital FOREIGN KEY (Hs2_id) REFERENCES Hospital(Hs_id),
    CONSTRAINT fk_orders_bloodbank FOREIGN KEY (BB4_id) REFERENCES Bloodbank(BB_id)
);

--------------------------------------------------------
-- INVOICE TABLE
--------------------------------------------------------
CREATE TABLE Invoice (
    In_id     NUMBER(10),
    In_date   DATE,
    In_time   TIMESTAMP,
    In_amount NUMBER(10),
    In_status VARCHAR2(50),
    Or1_id    NUMBER(10),
    PRIMARY KEY(In_id),
    CONSTRAINT fk_invoice_ord FOREIGN KEY (Or1_id) REFERENCES Ord(Or_id)
);

--------------------------------------------------------
-- TRANSACTION TABLE
--------------------------------------------------------
CREATE TABLE Transactionstab (
    T_id     NUMBER(10),
    T_date   DATE,
    T_time   TIMESTAMP,
    T_mode   VARCHAR2(10),
    T_status VARCHAR2(10),
    In1_id   NUMBER(10),
    PRIMARY KEY(T_id),
    CONSTRAINT fk_transaction_invoice FOREIGN KEY (In1_id) REFERENCES Invoice(In_id)
);

COMMIT;
/
