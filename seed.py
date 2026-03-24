from app import create_app
from extensions import db
from models.user import User
from models.book import Book
from utils.qr_service import generate_qr

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database tables created.")

    # Admin user
    admin = User(name='Admin', email='admin@lms.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    # Students
    students_data = [
        ('Hari Kumar', 'student1@lms.com'),
        ('Priya Sharma', 'student2@lms.com'),
        ('Rahul Verma', 'student3@lms.com'),
        ('Ananya Patel', 'student4@lms.com'),
        ('Vikram Singh', 'student5@lms.com'),
    ]
    for name, email in students_data:
        s = User(name=name, email=email, role='student')
        s.set_password('student123')
        db.session.add(s)

    # Books
    books_data = [
        ('Introduction to Algorithms', 'Thomas H. Cormen', 'Technology', '9780262033848', 3,
         'Comprehensive textbook on algorithms covering sorting, searching, graph algorithms and more.'),
        ('Clean Code', 'Robert C. Martin', 'Technology', '9780132350884', 2,
         'A handbook of agile software craftsmanship for writing clean, maintainable code.'),
        ('Python Crash Course', 'Eric Matthes', 'Technology', '9781593279288', 4,
         'A hands-on, project-based introduction to Python programming.'),
        ('Artificial Intelligence: A Modern Approach', 'Stuart Russell', 'Artificial Intelligence', '9780134610993', 2,
         'The leading textbook in AI, covering intelligent agents, search, and machine learning.'),
        ('Deep Learning', 'Ian Goodfellow', 'Artificial Intelligence', '9780262035613', 2,
         'Comprehensive resource on deep learning covering theory and practical techniques.'),
        ('Machine Learning Yearning', 'Andrew Ng', 'Artificial Intelligence', '9781234567890', 3,
         'Technical strategy guide for ML practitioners on structuring ML projects.'),
        ('Database System Concepts', 'Abraham Silberschatz', 'Database', '9780078022159', 3,
         'Foundational text on database design, SQL, and transaction management.'),
        ('Operating System Concepts', 'Abraham Silberschatz', 'Operating Systems', '9781119800361', 2,
         'Classic textbook covering process management, memory, and file systems.'),
        ('Computer Networks', 'Andrew Tanenbaum', 'Networking', '9780132126953', 3,
         'Comprehensive guide to computer networking from physical layer to application layer.'),
        ('The Pragmatic Programmer', 'David Thomas', 'Technology', '9780135957059', 2,
         'Classic guide to software development covering tips and best practices.'),
        ('Design Patterns', 'Erich Gamma', 'Technology', '9780201633610', 2,
         'Gang of Four classic on reusable object-oriented software design patterns.'),
        ('Data Structures Using C', 'Reema Thareja', 'Data Structures', '9780198099307', 4,
         'Comprehensive guide to data structures implementation in C programming.'),
        ('Discrete Mathematics', 'Kenneth Rosen', 'Mathematics', '9780073383095', 3,
         'Standard textbook for discrete math covering logic, sets, and graph theory.'),
        ('Linear Algebra and Its Applications', 'Gilbert Strang', 'Mathematics', '9780030105678', 2,
         'Clear introduction to linear algebra with real-world applications.'),
        ('Probability and Statistics', 'Jay Devore', 'Mathematics', '9781305251809', 3,
         'Engineering and sciences focused probability and statistics textbook.'),
        ('Software Engineering', 'Ian Sommerville', 'Technology', '9780133943030', 2,
         'Comprehensive introduction to software engineering methodologies and practices.'),
        ('Cryptography and Network Security', 'William Stallings', 'Cybersecurity', '9780134444284', 2,
         'Principles and practice of cryptography and network security.'),
        ('Ethical Hacking', 'Matt Walker', 'Cybersecurity', '9781260454550', 3,
         'CEH certification guide covering penetration testing and security assessment.'),
        ('Web Development with Django', 'Ben Shaw', 'Web Development', '9781839212505', 3,
         'Practical guide to building web applications using Django framework.'),
        ('JavaScript: The Good Parts', 'Douglas Crockford', 'Web Development', '9780596517748', 2,
         'Concise guide to the best features of JavaScript for elegant programming.'),
    ]

    for title, author, category, isbn, qty, desc in books_data:
        book = Book(title=title, author=author, category=category,
                    isbn=isbn, quantity=qty, description=desc)
        db.session.add(book)

    db.session.commit()
    print(f"Added {len(students_data)} students and {len(books_data)} books.")

    # Generate QR codes
    books = Book.query.all()
    for book in books:
        book.qr_code_path = generate_qr(book)
    db.session.commit()
    print(f"Generated QR codes for {len(books)} books.")

    # Create some sample issued books
    from datetime import datetime, timedelta
    from models.issued_book import IssuedBook

    sample_issues = [
        (1, 2, -20, -6, 'returned'),   # Book 1, Student 2 (Hari), returned
        (3, 2, -10, 4, 'issued'),       # Book 3, Student 2, currently issued
        (5, 2, -30, -16, 'returned'),   # Book 5, Student 2, returned late
        (4, 3, -15, -1, 'issued'),      # Book 4, Student 3 (Priya), overdue
        (7, 3, -5, 9, 'issued'),        # Book 7, Student 3, currently issued
        (2, 4, -25, -11, 'returned'),   # Book 2, Student 4 (Rahul), returned
        (10, 4, -8, 6, 'issued'),       # Book 10, Student 4, currently issued
        (6, 5, -18, -4, 'issued'),      # Book 6, Student 5 (Ananya), overdue
        (12, 5, -3, 11, 'issued'),      # Book 12, Student 5, recently issued
        (9, 6, -12, 2, 'issued'),       # Book 9, Student 6 (Vikram), due soon
    ]

    now = datetime.utcnow()
    for book_id, user_id, issue_offset, due_offset, status in sample_issues:
        issue_date = now + timedelta(days=issue_offset)
        due_date = now + timedelta(days=due_offset)

        issued = IssuedBook(
            book_id=book_id, user_id=user_id,
            issue_date=issue_date, due_date=due_date,
            status='issued'
        )

        if status == 'returned':
            issued.return_date = due_date + timedelta(days=2)
            issued.status = 'returned'
            if issued.return_date > due_date:
                overdue_days = (issued.return_date - due_date).days
                issued.fine = overdue_days * 5
            else:
                issued.fine = 0

        db.session.add(issued)

    db.session.commit()

    # Update overdue statuses
    from utils.fine_calculator import update_overdue_statuses
    update_overdue_statuses()
    print("Created sample issue records and updated overdue statuses.")

    print("\n--- Seed Complete ---")
    print("Admin login: admin@lms.com / admin123")
    print("Student login: student1@lms.com / student123")
    print("Run: python3 app.py")
