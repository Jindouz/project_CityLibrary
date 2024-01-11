from datetime import datetime, timedelta
from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
api = Api(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:SECRET@localhost/restaurant'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# =============== Models ===============
# Book Model
class Book(db.Model):
    __tablename__ = 'Books'
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    Author = db.Column(db.String)
    YearPublished = db.Column(db.Integer)
    Type = db.Column(db.Integer)

# Customer Model
class Customer(db.Model):
    __tablename__ = 'Customers'
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    City = db.Column(db.String)
    Age = db.Column(db.Integer)

# Loan Model
class Loan(db.Model):
    __tablename__ = 'Loans'
    Id = db.Column(db.Integer, primary_key=True)
    CustomerID = db.Column(db.Integer, db.ForeignKey('Customers.Id'))
    BookID = db.Column(db.Integer, db.ForeignKey('Books.Id'))
    Loandate = db.Column(db.Date)
    Returndate = db.Column(db.Date)
# ==============================================



# =============== Book Resource ===============
    
# Request parser for handling incoming JSON data
book_parser = reqparse.RequestParser()
book_parser.add_argument('Name', type=str, required=True, help='Name cannot be blank')
book_parser.add_argument('Author', type=str, required=True, help='Author cannot be blank')
book_parser.add_argument('YearPublished', type=int, required=True, help='YearPublished cannot be blank')
book_parser.add_argument('Type', type=int, required=True, help='Type cannot be blank')

# Book Resource Class CRUD
class BookResource(Resource):
    def get(self, book_id=None):
        if book_id:
            book = db.session.get(Book, book_id) # Get book by ID
            if book:
                return {'Id': book.Id, 'Name': book.Name, 'Author': book.Author,
                        'YearPublished': book.YearPublished, 'Type': book.Type}
            else:
                return {'message': 'Book not found'}, 404
        else:
            books = Book.query.all() # Get all books
            books_data = [{'Id': book.Id, 'Name': book.Name, 'Author': book.Author,
                           'YearPublished': book.YearPublished, 'Type': book.Type} for book in books]
            return {'books': books_data}

    def post(self):
        data = book_parser.parse_args()
        # Validate the book type (restricted to 1, 2, and 3)
        if data['Type'] not in {1, 2, 3}:
            return {'message': 'Invalid book type. Supported types are 1, 2, and 3.'}, 400
        new_book = Book(**data)
        db.session.add(new_book)
        db.session.commit()
        return {'message': 'Book added successfully'}, 201

    def put(self, book_id):
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

    def delete(self, book_id):
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



# ============== Customer Resource ===============

# Request parser for handling incoming JSON data
customer_parser = reqparse.RequestParser()
customer_parser.add_argument('Name', type=str, required=True, help='Name cannot be blank')
customer_parser.add_argument('City', type=str, required=True, help='City cannot be blank')
customer_parser.add_argument('Age', type=int, required=True, help='Age cannot be blank')

# Customer Resource Class CRUD
class CustomerResource(Resource):
    def get(self, customer_id=None):
        if customer_id:
            customer = db.session.get(Customer, customer_id) # Get customer by ID
            if customer:
                return {'Id': customer.Id, 'Name': customer.Name, 'City': customer.City, 'Age': customer.Age}
            else:
                return {'message': 'Customer not found'}, 404
        else:
            customers = Customer.query.all() # Get all customers
            customers_data = [{'Id': customer.Id, 'Name': customer.Name, 'City': customer.City, 'Age': customer.Age}
                              for customer in customers]
            return {'customers': customers_data}

    def post(self):
        data = customer_parser.parse_args()
        new_customer = Customer(**data)
        db.session.add(new_customer)
        db.session.commit()
        return {'message': 'Customer added successfully'}, 201

    def put(self, customer_id):
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

    def delete(self, customer_id):
        customer = db.session.get(Customer, customer_id)
        if customer:
            db.session.delete(customer)
            db.session.commit()
            return {'message': 'Customer deleted successfully'}
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



# ============= Loan Resource ===============

# Request parser for handling incoming JSON data
loan_parser = reqparse.RequestParser()
loan_parser.add_argument('CustomerID', type=int, required=True, help='CustomerID cannot be blank')
loan_parser.add_argument('BookID', type=int, required=True, help='BookID cannot be blank')
loan_parser.add_argument('Loandate', type=str, required=True, help='Loandate cannot be blank (format: YYYY-MM-DD)')
loan_parser.add_argument('Returndate', type=str, required=False)

# Loan Resource Class CRUD
class LoanResource(Resource):
    def get(self, loan_id=None):
        if loan_id:
            loan = db.session.get(Loan, loan_id) # Get loan by ID
            if loan:
                loan_data = {'Id': loan.Id, 'CustomerID': loan.CustomerID, 'BookID': loan.BookID,
                             'Loandate': loan.Loandate.strftime('%Y-%m-%d'),
                             'Returndate': loan.Returndate.strftime('%Y-%m-%d')}
                return {'loan': loan_data}
            else:
                return {'message': 'Loan not found'}, 404
        else:
            loans = Loan.query.all() # Get all loans
            loans_data = [{'Id': loan.Id, 'CustomerID': loan.CustomerID, 'BookID': loan.BookID,
                           'Loandate': loan.Loandate.strftime('%Y-%m-%d'),
                           'Returndate': loan.Returndate.strftime('%Y-%m-%d')}
                          for loan in loans]
            return {'loans': loans_data}

    def post(self):
        data = loan_parser.parse_args()
        
        # Convert the date strings to Python date objects
        data['Loandate'] = datetime.strptime(data['Loandate'], '%Y-%m-%d').date()

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
            return response_data, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error: {str(e)}'}, 500


    def put(self, loan_id):
        loan = db.session.get(Loan, loan_id)
        if loan:
            data = loan_parser.parse_args()
            
            # Convert the date strings to Python date objects
            data['Loandate'] = datetime.strptime(data['Loandate'], '%Y-%m-%d').date()

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
                return {'message': 'Loan updated successfully'}
            except Exception as e:
                db.session.rollback()
                return {'message': f'Error: {str(e)}'}, 500
        else:
            return {'message': 'Loan not found'}, 404

    def delete(self, loan_id):
        loan = db.session.get(Loan, loan_id)
        if loan:
            db.session.delete(loan)
            db.session.commit()
            return {'message': 'Loan deleted successfully'}
        else:
            return {'message': 'Loan not found'}, 404

# Add LoanResource to the API
api.add_resource(LoanResource, '/loans', '/loans/<int:loan_id>')

# ======================================




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
