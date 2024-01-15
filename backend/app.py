from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt
from icecream import ic

app = Flask(__name__) 
api = Api(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:SECRET@localhost/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['JWT_SECRET_KEY'] = 'Books4Loan'
jwt = JWTManager(app)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=120)
bcrypt = Bcrypt(app)


# =============== SQL Models ===============

# Book Model
class Book(db.Model):
    __tablename__ = 'Books'
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255))
    Author = db.Column(db.String(100))
    YearPublished = db.Column(db.Integer)
    Type = db.Column(db.Integer)

# Customer Model
class Customer(db.Model):
    __tablename__ = 'Customers'
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    City = db.Column(db.String(50))
    Age = db.Column(db.Integer)


# Loan Model
class Loan(db.Model):
    __tablename__ = 'Loans'
    Id = db.Column(db.Integer, primary_key=True)
    CustomerID = db.Column(db.Integer, db.ForeignKey('Customers.Id'))
    BookID = db.Column(db.Integer, db.ForeignKey('Books.Id'))
    Loandate = db.Column(db.Date)
    Returndate = db.Column(db.Date)

# =====

# User Model (Login) 
class User(db.Model):
    __tablename__ = 'Users'
    Id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.BOOLEAN, nullable=False)
    CustomerID = db.Column(db.Integer, db.ForeignKey('Customers.Id'))

# ==============================================

# Route for redirecting to the frontend pages without needing 
# to use live server on a different port (an alternative solution that avoids CORS Errors)
@app.route('/')
def landing_page():
    redirect_url = '/frontend/index.html'
    return render_template('redirect.html', redirect_url=redirect_url)

# Route for serving files in the 'frontend' folder
@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    return send_from_directory('../frontend', filename)

# =============== Registeration and Login ================

# Request parser for handling incoming JSON data
register_parser = reqparse.RequestParser()
register_parser.add_argument('Username', type=str, required=True, help='Username cannot be blank')
register_parser.add_argument('Password', type=str, required=True, help='Password cannot be blank')
register_parser.add_argument('Name', type=str, required=True, help='Name cannot be blank')
register_parser.add_argument('City', type=str, required=True, help='City cannot be blank')
register_parser.add_argument('Age', type=int, required=True, help='Age cannot be blank')

# User Registration
class UserRegistrationResource(Resource):
    def post(self):
        data = register_parser.parse_args()

        # Check if the username is already taken
        if User.query.filter_by(Username=data['Username']).first():
            return {'message': 'Username already taken'}, 400
        
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(data['Password']).decode('utf-8')

        new_customer = Customer(Name=data['Name'], City=data['City'], Age=data['Age'])
        db.session.add(new_customer)
        db.session.commit()

        new_user = User(Username=data['Username'], Password=hashed_password, is_admin=False, CustomerID=new_customer.Id)
        db.session.add(new_user)
        db.session.commit()
        ic(data['Username'], "registered successfully") # IC logging to logger.txt

        return {'message': 'User registered successfully'}, 201

# Add UserRegistrationResource to the API
api.add_resource(UserRegistrationResource, '/register')

# =====

# Request parser for handling incoming JSON data
login_parser = reqparse.RequestParser()
login_parser.add_argument('Username', type=str, required=True, help='Username cannot be blank')
login_parser.add_argument('Password', type=str, required=True, help='Password cannot be blank')
# User Login
class UserLoginResource(Resource):
    def post(self):
        data = login_parser.parse_args()

        if not data['Username'] or not data['Password']:
            return {'message': 'Username and password are required'}, 400

        user = User.query.filter_by(Username=data['Username']).first()
        customer = Customer.query.get(user.CustomerID)
        if customer is not None:
            customerName = customer.Name
        else:
            customerName = ''

        # Check if the user exists and the password is correct
        if user and bcrypt.check_password_hash(user.Password, data['Password']):
            # Create an access token
            access_token = create_access_token(identity=user.Id)
            
            # Log user login using icecream
            ic(data['Username'], "logged in successfully") # IC logging to logger.txt
            return {'access_token': access_token, 'message': 'Login successful', 'is_admin': user.is_admin, 'Name': customerName}
        return {'message': 'Invalid credentials'}, 401

# Add UserLoginResource to the API
api.add_resource(UserLoginResource, '/login')

# =====

# =============== Extra Users Functions ================

# Request parser for handling incoming JSON data
user_parser = reqparse.RequestParser()
user_parser.add_argument('Username', type=str, required=False)
user_parser.add_argument('Password', type=str, required=False)
user_parser.add_argument('is_admin', type=bool, required=True, help='is_admin cannot be blank')
user_parser.add_argument('CustomerID', type=int, required=False)

# Get specific User details for access check and messages (customername, username, is_admin)
class UserResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = db.session.get(User, current_user)
        customer = db.session.get(Customer, user.CustomerID)
        if customer is not None:
            customerName = customer.Name
        else:
            customerName = ''
        return {'Name': customerName, 'Username': user.Username, 'is_admin': user.is_admin}
    
    # updating users credentials and admin status (mainly for debug and promoting/demoting existing users as Admins via ThunderClient)
    @jwt_required()
    def put(self, user_id):
        current_user = get_jwt_identity()
        if not is_admin(current_user):
            return {'message': 'Only admins can edit users'}, 403
        user = db.session.get(User, user_id)
        
        if user:
            data = user_parser.parse_args()

            hashed_password = bcrypt.generate_password_hash(data['Password']).decode('utf-8')
            user.Username = data['Username']
            user.Password = hashed_password

            user.is_admin = data['is_admin']
            # user.CustomerID = data['CustomerID'] #being able to change customer ID for debug purposes
            db.session.commit()
            return {'message': 'user updated successfully'}
        else:
            return {'message': 'user not found'}, 404
        
    # deleting users
    @jwt_required()
    def delete(self, user_id):
        current_user = get_jwt_identity()
        if not is_admin(current_user):
            return {'message': 'Only admins can delete users'}, 403
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'user deleted successfully'}
        else:
            return {'message': 'user not found'}, 404
        

api.add_resource(UserResource, '/user','/user/<int:user_id>')

# =====================================


# Handle token expiration
@jwt_required()
def token_expired_callback():
    current_user = get_jwt_identity()
    return jsonify(message="Token has expired"), 401

def is_admin(current_user):
    user = User.query.get(current_user)
    return user.is_admin

# =====================================



# =============== Books Resource ===============
    
# Request parser for handling incoming JSON data
book_parser = reqparse.RequestParser()
book_parser.add_argument('Name', type=str, required=True, help='Name cannot be blank')
book_parser.add_argument('Author', type=str, required=True, help='Author cannot be blank')
book_parser.add_argument('YearPublished', type=int, required=True, help='YearPublished cannot be blank')
book_parser.add_argument('Type', type=int, required=True, help='Type cannot be blank')

# Books CRUD
class BookResource(Resource):
    @jwt_required()
    def get(self, book_id=None):
        current_user = get_jwt_identity()
        if book_id:
            book = db.session.get(Book, book_id) # Get book by ID
            if book:
                return {'Id': book.Id, 'Name': book.Name, 'Author': book.Author,
                        'YearPublished': book.YearPublished, 'Type': book.Type}
            else:
                return {'message': 'Book not found'}, 404
        else:
            if 'search' in request.args:
                search_query = request.args.get('search').strip()
                books = Book.query.filter(Book.Name.ilike(f'%{search_query}%')).all()
            else:
                books = Book.query.all() # Get all books
            books_data = [{'Id': book.Id, 'Name': book.Name, 'Author': book.Author,
                           'YearPublished': book.YearPublished, 'Type': book.Type} for book in books]
            return {'books': books_data}

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if not is_admin(current_user):
            return {'message': 'Only admins can add books'}, 403
        data = book_parser.parse_args()
        # Validate the book type (restricted to 1, 2, and 3)
        if data['Type'] not in {1, 2, 3}:
            return {'message': 'Invalid book type. Supported types are 1, 2, and 3.'}, 400
        new_book = Book(**data)
        db.session.add(new_book)
        db.session.commit()
        return {'message': 'Book added successfully'}, 201

    @jwt_required()
    def put(self, book_id):
        current_user = get_jwt_identity()
        if not is_admin(current_user):
            return {'message': 'Only admins can add books'}, 403
        book = db.session.get(Book, book_id)
        if book:
            data = book_parser.parse_args()
            # Validate the book type (restricted to 1, 2, and 3)
            if data['Type'] not in {1, 2, 3}:
                return {'message': 'Invalid book type. Supported types are 1, 2, and 3.'}, 400
            book.Name = data['Name']
            book.Author = data['Author']
            book.YearPublished = data['YearPublished']
            book.Type = data['Type']
            db.session.commit()
            return {'message': 'Book updated successfully'}
        else:
            return {'message': 'Book not found'}, 404

    @jwt_required()
    def delete(self, book_id):
        current_user = get_jwt_identity()
        if not is_admin(current_user):
            return {'message': 'Only admins can add books'}, 403
        book = db.session.get(Book, book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return {'message': 'Book deleted successfully'}
        else:
            return {'message': 'Book not found'}, 404

# Add BookResource to the API
api.add_resource(BookResource, '/books', '/books/<int:book_id>')

# ======================================



# ============== Customers Resource ===============

# Request parser for handling incoming JSON data
customer_parser = reqparse.RequestParser()
customer_parser.add_argument('Name', type=str, required=True, help='Name cannot be blank')
customer_parser.add_argument('City', type=str, required=True, help='City cannot be blank')
customer_parser.add_argument('Age', type=int, required=True, help='Age cannot be blank')

# Customers CRUD
class CustomerResource(Resource):
    # GET customers function (also using a join query with the users table)
    @jwt_required()
    def get(self, customer_id=None):
        current_user = get_jwt_identity()

        if customer_id:
            customer = db.session.get(Customer, customer_id)  # Get customer by ID

            if customer:
                user = User.query.filter_by(CustomerID=customer.Id).first()
                username = user.Username if user else None
                isAdmin = user.is_admin if user else None # Get user's admin status and username else set them to None (for debug)
                return {'Id': customer.Id, 'Name': customer.Name, 'City': customer.City, 'Age': customer.Age, 'Username': username, 'is_admin': isAdmin}
            else:
                return {'message': 'Customer not found'}, 404
        else:
            customers_data = []
            if 'search' in request.args:
                search_query = request.args.get('search').strip()
                customers = Customer.query.filter(Customer.Name.ilike(f'%{search_query}%')).all()
            else:
                customers = Customer.query.all()  # Get all customers

            for customer in customers:
                user = User.query.filter_by(CustomerID=customer.Id).first()
                username = user.Username if user else None
                isAdmin = user.is_admin if user else None
                customers_data.append({
                    'Id': customer.Id,
                    'Name': customer.Name,
                    'City': customer.City,
                    'Age': customer.Age,
                    'Username': username,
                    'is_admin': isAdmin
                })

            return {'customers': customers_data}
        

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        data = customer_parser.parse_args()
        new_customer = Customer(**data)
        db.session.add(new_customer)
        db.session.commit()
        return {'message': 'Customer added successfully'}, 201

    @jwt_required()
    def put(self, customer_id):
        current_user = get_jwt_identity()
        customer = db.session.get(Customer, customer_id)
        if customer:
            data = customer_parser.parse_args()
            customer.Name = data['Name']
            customer.City = data['City']
            customer.Age = data['Age']
            db.session.commit()
            return {'message': 'Customer updated successfully'}
        else:
            return {'message': 'Customer not found'}, 404


    # delete customer and related user
    @jwt_required()
    def delete(self, customer_id):
        current_user = get_jwt_identity()
        customer = db.session.get(Customer, customer_id)

        if customer:
            # Get the related user
            user = User.query.filter_by(CustomerID=customer.Id).first()

            if user:
                db.session.delete(user)  # Delete the related user
                db.session.commit()

            db.session.delete(customer)  # Delete the customer
            db.session.commit()

            ic(current_user, "used Customers DELETE.")  # IC logging to logger.txt
            return {'message': 'Customer and User deleted successfully'}
        else:
            return {'message': 'Customer not found'}, 404

# Add CustomerResource to the API
api.add_resource(CustomerResource, '/customers', '/customers/<int:customer_id>')

# ======================================



# === Book Type Functions - Calculate return date by loan days (Type 1: 10 days, Type 2: 5 days, Type 3: 2 days) ===
def get_max_loan_days(book_type):
    if book_type == 1:
        return 10
    elif book_type == 2:
        return 5
    elif book_type == 3:
        return 2
    else:
        raise ValueError("Invalid book type. Supported types are 1, 2, and 3.")

def calculate_return_date(book_type):
    max_loan_days = get_max_loan_days(book_type)
    return datetime.now() + timedelta(days=max_loan_days)

# ===========================================



# ============= Loans Resource ===============

# Request parser for handling incoming JSON data
loan_parser = reqparse.RequestParser()
loan_parser.add_argument('CustomerID', type=int, required=True, help='CustomerID cannot be blank')
loan_parser.add_argument('BookID', type=int, required=True, help='BookID cannot be blank')
loan_parser.add_argument('Loandate', type=str, required=True, help='Loandate cannot be blank (format: DD-MM-YYYY)')
loan_parser.add_argument('Returndate', type=str, required=False)

# Loans CRUD
class LoanResource(Resource):
    # GET loans function (also using a join query with the customers and books table)
    @jwt_required()
    def get(self, loan_id=None):
        current_user = get_jwt_identity()

        if loan_id:
            loan = db.session.get(Loan, loan_id) # Get loan by ID

            if loan:
                customer = db.session.query(Customer).filter_by(Id=loan.CustomerID).first()
                book = db.session.query(Book).filter_by(Id=loan.BookID).first()
                customerName = customer.Name if customer else None
                bookName = book.Name if book else None # Get customer name and book name if they exist else set them to None (for debug)
                loan_data = {'Id': loan.Id, 'CustomerID': loan.CustomerID, 'BookID': loan.BookID,
                             'Loandate': loan.Loandate.strftime('%d-%m-%Y'),
                             'Returndate': loan.Returndate.strftime('%d-%m-%Y'),
                             'customerName': customerName, 'bookName': bookName}
               
                return {'loan': loan_data}
            else:
                return {'message': 'Loan not found'}, 404
        else:
            loans = Loan.query.all() # Get all loans
            loans_data = []

            for loan in loans: 
                customer = db.session.get(Customer, loan.CustomerID)
                book = db.session.get(Book, loan.BookID)
                customerName = customer.Name if customer else None
                bookName = book.Name if book else None
                loans_data.append({
                    'Id': loan.Id, 'CustomerID': loan.CustomerID, 'BookID': loan.BookID,
                    'Loandate': loan.Loandate.strftime('%d-%m-%Y'),
                    'Returndate': loan.Returndate.strftime('%d-%m-%Y'),
                    'customerName': customerName, 'bookName': bookName })
                             
            return {'loans': loans_data}

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        data = loan_parser.parse_args()
        
        # Convert the date strings to Python date objects
        data['Loandate'] = datetime.strptime(data['Loandate'], '%d-%m-%Y').date()

        # Check if the customer with the given CustomerID exists
        customer = db.session.get(Customer, data['CustomerID'])
        if not customer:
            return {'message': 'Customer not found'}, 404

        # Check if the book with the given BookID exists
        book = db.session.get(Book, data['BookID'])
        if not book:
            return {'message': 'Book not found'}, 404

        # Check if a loan with the same BookID and CustomerID already exists
        existing_loan = Loan.query.filter_by(BookID=data['BookID'], CustomerID=data['CustomerID']).first()
        if existing_loan:
            return {'message': 'A loan for this book and customer already exists'}, 409  # Conflict

        # Calculate the return date based on the book type by calling the calculate_return_date function
        data['Returndate'] = calculate_return_date(book.Type)

        new_loan = Loan(**data)

        try:
            db.session.add(new_loan)
            db.session.commit()

            # Get the ID of the created loan
            loan_id = new_loan.Id

            # Return the loan_id in the response
            response_data = {'message': 'Book loaned successfully', 'loan_id': loan_id}
            ic(current_user, "used Loans POST.") # IC logging to logger.txt
            return response_data, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error: {str(e)}'}, 500

    @jwt_required()
    def put(self, loan_id):
        current_user = get_jwt_identity()
        loan = db.session.get(Loan, loan_id)
        if loan:
            data = loan_parser.parse_args()
            
            # Convert the date strings to Python date objects
            data['Loandate'] = datetime.strptime(data['Loandate'], '%d-%m-%Y').date()

            # Check if the customer with the given CustomerID exists
            customer = db.session.get(Customer, data['CustomerID'])
            if not customer:
                return {'message': 'Customer not found'}, 404

            # Check if the book with the given BookID exists
            book = db.session.get(Book, data['BookID'])
            if not book:
                return {'message': 'Book not found'}, 404

            # Check if the updated combination of CustomerID and BookID already exists
            existing_loan = Loan.query.filter(
                Loan.Id != loan_id,
                Loan.CustomerID == data['CustomerID'],
                Loan.BookID == data['BookID']
            ).first()

            if existing_loan:
                return {'message': 'Cannot update: This book is already loaned to the same customer'}, 409  # Conflict

            # Calculate the return date based on the book type
            data['Returndate'] = calculate_return_date(book.Type)

            # Update the specified attributes
            loan.CustomerID = data['CustomerID']
            loan.BookID = data['BookID']
            loan.Loandate = data['Loandate']
            loan.Returndate = data['Returndate']

            try:
                db.session.commit()
                ic(current_user, "used Loans PUT.") # IC logging to logger.txt
                return {'message': 'Loan updated successfully'}
            except Exception as e:
                db.session.rollback()
                return {'message': f'Error: {str(e)}'}, 500
        else:
            return {'message': 'Loan not found'}, 404

    @jwt_required()
    def delete(self, loan_id):
        current_user = get_jwt_identity()
        loan = db.session.get(Loan, loan_id)
        if loan:
            db.session.delete(loan)
            db.session.commit()
            ic(current_user, "used Loans DELETE.") # IC logging to logger.txt
            return {'message': 'Loan deleted successfully'}
        else:
            return {'message': 'Loan not found'}, 404
        
# Add LoanResource to the API
api.add_resource(LoanResource, '/loans', '/loans/<int:loan_id>')

# ======================================

# User Loans by CustomerID
class UserLoanResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        loans = Loan.query.filter_by(CustomerID=user.CustomerID).all()
        for loan in loans:
            ic(loan.BookID) # IC logging to logger.txt
        return loans

api.add_resource(UserLoanResource, '/user/loans')



# ========= Icecream logger ============
def write_to_file(*args):
    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    with open('logger.txt', 'a+') as file:
        file.write(f'{timestamp} | {" ".join(str(arg) for arg in args)}\n')

ic.configureOutput(outputFunction=write_to_file)
# ======================================





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
