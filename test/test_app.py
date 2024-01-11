import unittest
from flask_testing import TestCase
from app import app, db, Book, Customer, Loan

class TestYourApp(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use an in-memory database for testing
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_book(self):
        response = self.client.post('/books', json={'Name': 'Test Book', 'Author': 'Test Author', 'YearPublished': 2022, 'Type': 1})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Book added successfully')

    def test_get_books(self):
        # Add a test book to the database
        test_book = Book(Name='Test Book', Author='Test Author', YearPublished=2022, Type=1)
        db.session.add(test_book)
        db.session.commit()

        response = self.client.get('/books')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['books']), 1)

    def test_add_customer(self):
        response = self.client.post('/customers', json={'Name': 'Test Customer', 'City': 'Test City', 'Age': 25})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Customer added successfully')

    def test_get_customers(self):
        # Add a test customer to the database
        test_customer = Customer(Name='Test Customer', City='Test City', Age=25)
        db.session.add(test_customer)
        db.session.commit()

        response = self.client.get('/customers')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['customers']), 1)

    def test_add_loan(self):
        # Add a test book and customer to the database
        test_book = Book(Name='Test Book', Author='Test Author', YearPublished=2022, Type=1)
        test_customer = Customer(Name='Test Customer', City='Test City', Age=25)
        db.session.add_all([test_book, test_customer])
        db.session.commit()

        response = self.client.post('/loans', json={'CustomerID': test_customer.Id, 'BookID': test_book.Id, 'Loandate': '2022-01-01'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Book loaned successfully')

if __name__ == '__main__':
    unittest.main()
