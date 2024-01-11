# ABOUT THIS APP

Thunder Client CRUD Testing:

Books:
{
    "Name": "Sample Book",
    "Author": "John Doe",
    "YearPublished": 2022,
    "Type": 1
}

Customers:
{
    "Name": "John Doe",
    "City": "Cityville",
    "Age": 30
}

Loans:
{
    "CustomerID": 2,
    "BookID": 2,
    "Loandate": "09-01-2024"
}

Register and Login:
{
    "Username": "1",
    "Password": "1",
    "is_admin": True
}

Registration of User + Customer:
{
    "Username": "userwaga",
    "Password": "123",
    "Name": "waga",
    "City": "NYC",
    "Age": 22
}

Get access token after logging in and put it in Auth/Header in Thunder Client:

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDgxNjkzNSwianRpIjoiMmYzZjM1ZDMtOTE0Yi00N2I0LTlhNTUtNGFkOTNiN2IyZGZlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzA0ODE2OTM1LCJjc3JmIjoiMTMxZjQ5ZGMtYTY0OC00YzFjLWIyOTItNWE3N2ExMmI1YjBmIiwiZXhwIjoxNzA0ODE4NzM1fQ.wr-uAb_pHMv0wqTq1yeP3rJeeUY17ea5T7eGb4ZFfDY

Success Login Example:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDgxNjkzNSwianRpIjoiMmYzZjM1ZDMtOTE0Yi00N2I0LTlhNTUtNGFkOTNiN2IyZGZlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzA0ODE2OTM1LCJjc3JmIjoiMTMxZjQ5ZGMtYTY0OC00YzFjLWIyOTItNWE3N2ExMmI1YjBmIiwiZXhwIjoxNzA0ODE4NzM1fQ.wr-uAb_pHMv0wqTq1yeP3rJeeUY17ea5T7eGb4ZFfDY",
  "message": "Login successful"
}



## TO DO in GUI HTML:
* Loan dropbox selection in GUI?
Loan for 10 Days
Loan for 5 Days
Loan for 2 Days

Secure Storage:
Store the access token securely in your client application. Avoid exposing it in public places or hardcoding it in your code.
Consider using secure storage mechanisms, such as secure cookies or a secure local storage, depending on your application's architecture.

Make it so expired loans are in an expired loans chart and make their background column line colored light red?

Make the dropdown selection box procedural and hide the next dropdown box and submit button until after all fields are made?

Choose a book to loan:
Choose for how long:


Admin section (for testing):
CRUD Books
CRUD Customers
CRUD Loans

User section:
Login as a customer and manage loaning books.

## Extras:
* add to both the readme and the top of the app comments about what the app does
* mention that query.get has been replaced with session.get because of an sqlalchemy update

* V check that all returns are JSON - They are, flask-RESTful makes sure they return JSON by default.



## TO DO in test_app:
- irrelevant for now - fix the backend/app.py path
- irrelevant for now - make it so it wont delete the database after each test and edit out or fix the tempfile

