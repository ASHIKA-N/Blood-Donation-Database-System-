

CREATE TABLE Foundation(
    F_id      NUMBER(10),
    F_name    VARCHAR2(15),
    F_address VARCHAR2(255),
    F_contact NUMBER(10),
    F_mail_id VARCHAR2(50),
    PRIMARY KEY(F_id)
);

CREATE TABLE Hospital(
    Hs_id      NUMBER(10),
    Hs_name    VARCHAR2(15),
    Hs_address VARCHAR2(255),
    Hs_contact NUMBER(10),
    PRIMARY KEY(Hs_id)
);

CREATE TABLE Employee(
    E_id          NUMBER(10),
    E_name        VARCHAR2(15),
    E_address     VARCHAR2(255),
    E_contact     NUMBER(10),
    E_age         NUMBER(2),
    E_designation VARCHAR2(10),
    E_experience  NUMBER(2),
    PRIMARY KEY(E_id)
);
ALTER TABLE EMPLOYEE ADD BB1_id number(10);
CREATE TABLE Bloodbank(
    BB_id      NUMBER(10),
    BB_name    VARCHAR2(15),
    BB_address VARCHAR2(255),
    BB_contact NUMBER(10),
    BB_volume  NUMBER(5),
    BB_type    VARCHAR2(2),
    PRIMARY KEY(BB_id)
);

CREATE TABLE Customer(
    C_id      NUMBER(10),
    C_name    VARCHAR2(15),
    C_address VARCHAR2(255),
    C_contact NUMBER(10),
    C_gender  VARCHAR2(6),
    C_history VARCHAR2(50),
    PRIMARY KEY(C_id)
);

CREATE TABLE Ord(
    Or_id       NUMBER(10),
    Or_date     DATE,
    Or_time     TIMESTAMP,
    Or_quantity NUMBER(10),
    Or_status   VARCHAR2(10),
    Or_type     VARCHAR2(3),
    PRIMARY KEY(Or_id)
);

CREATE TABLE Appointment(
    App_id     NUMBER(10),
    App_date   DATE,
    App_time   TIMESTAMP,
    App_status VARCHAR2(10),
    PRIMARY KEY(App_id)
);
ALTER TABLE APPOINTMENT ADD  D1_id number(10);

ALTER TABLE APPOINTMENT ADD  BB2_id number(10);
CREATE TABLE Donor(
    D_id      NUMBER(10),
    D_name    VARCHAR2(15),
    D_contact NUMBER(10),
    D_address VARCHAR2(255),
    D_age     NUMBER(3),
    D_gender  VARCHAR2(6),
    D_history NUMBER(10),
    PRIMARY KEY(D_id)
);
ALTER TABLE Donor ADD (BB3_id NUMBER(10), App1_id NUMBER(10));

CREATE TABLE Invoice(
    In_id     NUMBER(10),
    In_date   DATE,
    In_time   TIMESTAMP,
    In_amount NUMBER(10),
    In_status VARCHAR2(50),
    PRIMARY KEY(In_id)
);

CREATE TABLE Transactionstab(
    T_id     NUMBER(10),
    T_date   DATE,
    T_time   TIMESTAMP,
    T_mode   VARCHAR2(10),
    T_status VARCHAR2(10),
    PRIMARY KEY(T_id)
);

 ALTER TABLE HOSPITAL ADD f1_id number(10);
 ALTER TABLE HOSPITAL ADD c1_id number(10);
ALTER TABLE BLOODBANK ADD HS1_id number(10);
 ALTER TABLE BLOODBANK ADD F2_id number(10);

ALTER TABLE ORD ADD  C2_id number(10);
ALTER TABLE ORD ADD  HS2_id number(10);


ALTER TABLE INVOICE ADD  OR1_id number(10);
ALTER TABLE TRANSACTIONSTAB ADD  IN1_id number(10);

ALTER TABLE ORD ADD BB4_ID NUMBER(10);
 ALTER TABLE Hospital ADD CONSTRAINT fk_hospital_foundation FOREIGN KEY (F1_id) REFERENCES Foundation(F_id);
ALTER TABLE Hospital ADD CONSTRAINT fk_hospital_customer FOREIGN KEY (C1_id) REFERENCES Customer(C_id);
 ALTER TABLE Employee ADD CONSTRAINT fk_employee_bloodbank FOREIGN KEY (BB1_id) REFERENCES Bloodbank(BB_id);

 ALTER TABLE Bloodbank ADD CONSTRAINT fk_bloodbank_foundation FOREIGN KEY (F2_id) REFERENCES Foundation(F_id);
ALTER TABLE Bloodbank ADD CONSTRAINT fk_bloodbank_hospital FOREIGN KEY (Hs1_id) REFERENCES Hospital(Hs_id);

ALTER TABLE Ord ADD CONSTRAINT fk_orders_customer FOREIGN KEY (C2_id) REFERENCES Customer(C_id);
ALTER TABLE Ord ADD CONSTRAINT fk_orders_hospital FOREIGN KEY (Hs2_id) REFERENCES Hospital(Hs_id);
 
ALTER TABLE Appointment ADD CONSTRAINT fk_appointment_donor FOREIGN KEY (D1_id) REFERENCES Donor(D_id);
--ALTER TABLE Appointment ADD CONSTRAINT fk_appointment_bloodbank FOREIGN KEY (BB2_id) REFERENCES Bloodbank(BB_id);
ALTER TABLE Donor ADD CONSTRAINT fk_donor_bloodbank FOREIGN KEY (BB3_id) REFERENCES Bloodbank(BB_id);
--ALTER TABLE Donor ADD CONSTRAINT fk_donor_appointment FOREIGN KEY (App1_id) REFERENCES Appointment(App_id);--
 ALTER TABLE Invoice ADD CONSTRAINT fk_invoice_ord FOREIGN KEY (Or1_id) REFERENCES Ord(Or_id);

ALTER TABLE Transactionstab ADD CONSTRAINT fk_transaction_invoice FOREIGN KEY (In1_id) REFERENCES Invoice(In_id);
--ALTER TABLE CUSTOMER MODIFY C_HISTORY VARCHAR2(50);


ALTER TABLE ORD ADD CONSTRAINT fk_orders_BLOODBANK FOREIGN KEY(BB4_ID) REFERENCES Bloodbank(BB_ID);
COMMIT;
/
