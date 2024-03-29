# Night City Library (Project) - Loan Management System

1. [Introduction](#introduction)
2. [How to Run](#how-to-run)
3. [Features](#features)
4. [Project Structure](#project-structure)
5. [Python Packages](#python-packages)
6. [API Endpoints](#api-endpoints)
7. [File Uploads](#file-uploads)
8. [Icecream Logger](#icecream-logger)
9. [HTML Pages](#html-pages)
10. [Author](#author)

## Introduction <a name="introduction"></a>

Night City Library is a web-based Loan Management System that enables users and admins to manage book loans. The application is developed using Python with Flask_RESTful and Flask_SQLAlchemy for the backend and HTML, CSS (Bootstrap), and JavaScript (with Axios, Toastify) for the frontend.

## How to Run <a name="how-to-run"></a>

1. Clone the repository:

   ```
   git clone https://github.com/Jindouz/project_CityLibrary.git
   ```

2. Start Virtual Environment:
    ```
    python -m virtualenv env
    ```

3. Install requirements:
    ```
    pip install -r requirements.txt
    ```

4. Run the application:

    ```
    cd backend
    python app.py
    The application will be accessible at http://127.0.0.1:5000 as default. (or whichever address your Flask runs on)

    The default page "index.html" will redirect the user to the login page to login/register first before allowing access.
    ```


## Features <a name="features"></a>

- **User Authentication**: Users can log in to the system (JWT Protected, 2 Hours Session Token), and admins have access to additional features (full CRUD in their own menu). 

- **Login Required**: The app will redirect the user to login or register a new account if he tries to access restricted pages. 

- **Loan Management**: Users can loan available books, view current loans, and return loans and if a loan is late it is highlighted for them. 

- **Customer and Book Management**: Admins can manage customers, books and loans.

- **Search by Name**: Users can search for books by name.  (and also for Customers if Admin)  

- **Cascade Deletion**: 
    - When an Admin deletes a customer in the customers HTML page it also deletes the associated user account and all of his loans. 
    - When deleting a book it also deletes its book image and its associated loans. 

- **Book Image Upload**: Admins have the option to upload an image to each new book they add. Editing a book with a new book image will replace the old image and its path. Deleting a book that has an image will also delete the image from the uploads folder.

- **Toastify Notifications**: Toastify will notify the user for most actions made on each HTML page, including welcome messages, errors and access restrictions.

## Project Structure <a name="project-structure"></a>

- **backend/app.py**: The main Python file containing the Flask application, API routes, and database interactions.
- **frontend folder**: Contains HTML files for various pages such as login, register, menu, and individual pages for managing loans, customers, and books.
- **uploads/img**: Folder for storing uploaded images.
- **logger.txt**: Log file for storing ICECREAM logs.

## Python Packages <a name="python-packages"></a>

- Flask
- Flask-RESTful
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-Bcrypt
- Icecream
- Werkzeug

## API Endpoints <a name="api-endpoints"></a>
- **User (and Customer) Registration: /register** (POST)
- **User Login: /login** (POST)
- **User Details: /user** (GET), **/user/<user_id>** (PUT, DELETE)
- **User Loans: /user/loans** (GET), **/user/loans/<loan_id>** (POST, DELETE)  
-
- **Books: /books** (GET, POST), **/books/<book_id>** (GET, PUT, DELETE)
- **Customers: /customers** (GET, POST), **/customers/<customer_id>** (GET, PUT, DELETE)
- **Loans: /loans** (GET, POST), **/loans/<loan_id>** (GET, PUT, DELETE)
-  
- **Upload Image: /upload_image** (POST)

## File Uploads <a name="file-uploads"></a>
- Upload book images (10MB max, restricted to JPG and PNG file types) when adding books. (saved to the backend, deleted when deleting associated book)

## Icecream Logger <a name="icecream-logger"></a>
- ICECREAM is used for logging. Logs are written to the logger.txt file.

## HTML Pages <a name="html-pages"></a>
- **login.html:** User login page.  
- **register.html:** User registration page.  
- **index.html:** Main loan page based on logged in user.  
- **menu.html:** Main menu for admins with links to admin pages.  
- **loans.html:** Loan management page for admins.  
- **customers.html:** Customer management page for admins.  
- **books.html:** Book management page for admins.  

## Author <a name="author"></a>
This project was created by Maor S.
