#include <iostream>
#include <sql.h>
#include <sqlext.h>
using namespace std;

int main() {
    SQLHENV env;
    SQLHDBC dbc;
    SQLHSTMT stmt;
    SQLRETURN ret;

    // Allocate environment handle
    SQLAllocHandle(SQL_HANDLE_ENV, SQL_NULL_HANDLE, &env);
    SQLSetEnvAttr(env, SQL_ATTR_ODBC_VERSION, (void*)SQL_OV_ODBC3, 0);

    // Allocate connection handle
    SQLAllocHandle(SQL_HANDLE_DBC, env, &dbc);

    // Connect to Oracle via DSN (set up in ODBC Data Sources)
    SQLCHAR connStr[] = "DSN=OracleDB;UID=system;PWD=yourpassword;";
    ret = SQLDriverConnect(dbc, NULL, connStr, SQL_NTS, NULL, 0, NULL, SQL_DRIVER_NOPROMPT);

    if (SQL_SUCCEEDED(ret)) {
        cout << "✅ Connected to Oracle successfully!\n";
        SQLAllocHandle(SQL_HANDLE_STMT, dbc, &stmt);

        // Run a query
        SQLExecDirect(stmt, (SQLCHAR*)"SELECT D_name, D_age FROM Donor", SQL_NTS);
        char name[50];
        int age;
        while (SQLFetch(stmt) == SQL_SUCCESS) {
            SQLGetData(stmt, 1, SQL_C_CHAR, name, sizeof(name), NULL);
            SQLGetData(stmt, 2, SQL_C_LONG, &age, 0, NULL);
            cout << name << " (" << age << ")\n";
        }

        SQLFreeHandle(SQL_HANDLE_STMT, stmt);
        SQLDisconnect(dbc);
    } else {
        cout << "❌ Connection failed.\n";
    }

    SQLFreeHandle(SQL_HANDLE_DBC, dbc);
    SQLFreeHandle(SQL_HANDLE_ENV, env);
    return 0;
}
