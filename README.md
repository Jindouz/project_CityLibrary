# Night City Library - Loan Management System

Night City Library is a web-based Loan Management System that enables users to manage book loans, customers, and books. The application is developed using Python with Flask for the backend and HTML, CSS, and JavaScript for the frontend.

## Features

- **User Authentication**: Users can log in to the system, and administrators have access to additional features.
- **Loan Management**: Users can loan books, view current loans, edit loan details, and delete loans.
- **Customer and Book Management**: Admins can manage customers and books, ensuring an up-to-date database.

## Project Structure

- **app.py**: The main Python file containing the Flask application, API routes, and database interactions.
- **templates folder**: Contains HTML files for various pages such as login, register, menu, and individual pages for managing loans, customers, and books.
- **static folder**: Holds static assets such as images, icons, and CSS files.

## How to Run

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/night-city-library.git

2. Install requirements:
    ```
    pip install -r requirements.txt
    ```

Run the application:

bash
Copy code
python app.py
The application will be accessible at http://127.0.0.1:5000.

## HTML Pages
login.html: User login page.
register.html: User registration page.
menu.html: Main menu for users with options based on user roles.
loans.html: Loan management page for users and admins.
customers.html: Customer management page for admins.
books.html: Book management page for admins.
404.html: Custom error page for handling 404 errors.
Dependencies
Flask: A web framework for Python.
Bootstrap: Front-end framework for building responsive and attractive web pages.
Axios: A promise-based HTTP client for making requests to the server.
Toastify: A simple, lightweight, and responsive toast notification library.
Contributing
Contributions are welcome! If you find a bug or have an enhancement in mind, please open an issue or submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE.md file for details.