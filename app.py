import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

# =========================================================
# FLASK APP
# =========================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="statics"
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================================================
# USER TABLE
# =========================================================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20)
    )

    role = db.Column(
        db.String(20),
        default="user",
        nullable=False
    )


# =========================================================
# BOOK TABLE
# =========================================================

class Book(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    book_name = db.Column(
        db.String(100),
        nullable=False
    )

    author = db.Column(
        db.String(100),
        nullable=False
    )

    category = db.Column(
        db.String(100)
    )

    quantity = db.Column(
        db.Integer,
        default=1
    )


# =========================================================
# STUDENT TABLE
# =========================================================

class Student(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    roll_no = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(100)
    )

    phone = db.Column(
        db.String(20)
    )

    course = db.Column(
        db.String(100)
    )


# =========================================================
# ISSUE BOOK TABLE
# =========================================================

class IssueBook(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        nullable=False
    )

    issue_date = db.Column(
        db.String(50),
        nullable=False
    )

    return_date = db.Column(
        db.String(50),
        nullable=True
    )

    status = db.Column(
        db.String(50),
        default="Issued"
    )


# =========================================================
# DATABASE UPDATE
# =========================================================

def update_database():

    with app.app_context():

        db.create_all()

        try:

            # =================================================
            # ISSUE BOOK TABLE
            # =================================================

            result = db.session.execute(
                text("PRAGMA table_info(issue_book)")
            )

            issue_columns = [
                row[1]
                for row in result
            ]

            if "return_date" not in issue_columns:

                db.session.execute(
                    text(
                        "ALTER TABLE issue_book "
                        "ADD COLUMN return_date VARCHAR(50)"
                    )
                )

                print("return_date column added")


            # =================================================
            # USER TABLE
            # =================================================

            result = db.session.execute(
                text("PRAGMA table_info(user)")
            )

            user_columns = [
                row[1]
                for row in result
            ]


            # =================================================
            # ADD ROLE COLUMN
            # =================================================

            if "role" not in user_columns:

                db.session.execute(
                    text(
                        "ALTER TABLE user "
                        "ADD COLUMN role VARCHAR(20) "
                        "DEFAULT 'user'"
                    )
                )

                print("role column added")


            # =================================================
            # ADD PHONE COLUMN
            # =================================================

            if "phone" not in user_columns:

                db.session.execute(
                    text(
                        "ALTER TABLE user "
                        "ADD COLUMN phone VARCHAR(20)"
                    )
                )

                print("phone column added")


            # =================================================
            # FIX NULL ROLES
            # =================================================

            db.session.execute(
                text(
                    "UPDATE user "
                    "SET role = 'user' "
                    "WHERE role IS NULL"
                )
            )


            db.session.commit()

            print("Database ready")


        except Exception as e:

            db.session.rollback()

            print(
                "Database update error:",
                e
            )


# =========================================================
# ADMIN REQUIRED
# =========================================================

def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            return redirect("/login")


        if session.get("user_role") != "admin":

            return "Access Denied - Admin Only", 403


        return function(*args, **kwargs)


    return wrapper


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        phone = request.form.get(
            "phone",
            ""
        ).strip()


        # -------------------------------------------------
        # BASIC VALIDATION
        # -------------------------------------------------

        if not name or not email or not password:

            return "Name, email and password are required"


        # -------------------------------------------------
        # PASSWORD CHECK
        # -------------------------------------------------

        if password != confirm_password:

            return "Passwords do not match"


        # -------------------------------------------------
        # EMAIL CHECK
        # -------------------------------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            return "Email already registered"


        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        phone=phone,
        role="user"

        )


        db.session.add(user)

        db.session.commit()


        return redirect("/login")


    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        user = User.query.filter_by(
            email=email
        ).first()


        # -------------------------------------------------
        # LOGIN CHECK
        # -------------------------------------------------

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id

            session["user_name"] = user.name

            session["user_email"] = user.email

            session["user_role"] = user.role
          


            return redirect("/dashboard")


        return render_template(

            "login.html",

            error="Invalid email or password"

        )


    return render_template(
        "login.html"
    )


# =========================================================
# PROFILE / BIO DATA
# =========================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user_id" not in session:

        return redirect("/login")


    # -----------------------------------------------------
    # CURRENT USER
    # -----------------------------------------------------

    user = User.query.get(
        session.get("user_id")
    )


    if not user:

        session.clear()

        return redirect("/login")


    # =====================================================
    # UPDATE PROFILE
    # =====================================================

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not name or not email:

            student = None

            if user.role != "admin":

                student = Student.query.filter_by(
                    email=user.email
                ).first()


            return render_template(

                "profile.html",

                user=user,

                student=student,

                role=user.role,

                error="Name and Email are required."

            )


        # -------------------------------------------------
        # EMAIL DUPLICATE CHECK
        # -------------------------------------------------

        existing_user = User.query.filter(

            User.email == email,

            User.id != user.id

        ).first()


        if existing_user:

            student = None

            if user.role != "admin":

                student = Student.query.filter_by(
                    email=user.email
                ).first()


            return render_template(

                "profile.html",

                user=user,

                student=student,

                role=user.role,

                error="This email is already registered."

            )


        # -------------------------------------------------
        # SAVE OLD EMAIL
        # -------------------------------------------------

        old_email = user.email


        # -------------------------------------------------
        # UPDATE USER
        # -------------------------------------------------

        user.name = name

        user.email = email

        user.phone = phone


        # -------------------------------------------------
        # UPDATE PASSWORD
        # -------------------------------------------------

        if password:
            user.password = generate_password_hash(password)

        # -------------------------------------------------
        # UPDATE STUDENT RECORD
        # -------------------------------------------------

        if user.role != "admin":

            student = Student.query.filter_by(
                email=old_email
            ).first()


            if student:

                student.email = email

                student.name = name

                student.phone = phone


        db.session.commit()


        # -------------------------------------------------
        # UPDATE SESSION
        # -------------------------------------------------

        session["user_name"] = user.name

        session["user_email"] = user.email

        session["user_role"] = user.role


        return redirect("/profile")


    # =====================================================
    # GET PROFILE
    # =====================================================

    student = None


    if user.role != "admin":

        student = Student.query.filter_by(
            email=user.email
        ).first()


    return render_template(

        "profile.html",

        user=user,

        student=student,

        role=user.role

    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user_id" not in session:

        return redirect("/login")


    # =====================================================
    # COMMON DATA
    # =====================================================

    total_books = Book.query.count()


    # -----------------------------------------------------
    # BOOK MAP
    # -----------------------------------------------------

    all_books = Book.query.all()

    book_map = {

        book.id: book

        for book in all_books

    }


    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    if session.get("user_role") == "admin":

        total_students = Student.query.count()


        total_issued = IssueBook.query.filter_by(
            status="Issued"
        ).count()


        total_returned = IssueBook.query.filter_by(
            status="Returned"
        ).count()


        return render_template(

            "dashboard.html",

            name=session.get("user_name"),

            role="admin",

            total_books=total_books,

            total_students=total_students,

            total_issued=total_issued,

            total_returned=total_returned,

            student=None,

            my_issued=[],

            my_returned=[],

            my_issued_count=0,

            my_returned_count=0,

            book_map=book_map

        )


    # =====================================================
    # USER / STUDENT DASHBOARD
    # =====================================================

    student = Student.query.filter_by(

        email=session.get("user_email")

    ).first()


    my_issued = []

    my_returned = []


    if student:

        my_issued = IssueBook.query.filter_by(

            student_id=student.id,

            status="Issued"

        ).all()


        my_returned = IssueBook.query.filter_by(

            student_id=student.id,

            status="Returned"

        ).all()


    my_issued_count = len(
        my_issued
    )

    my_returned_count = len(
        my_returned
    )


    return render_template(

        "dashboard.html",

        name=session.get("user_name"),

        role="user",

        total_books=total_books,

        total_students=0,

        total_issued=0,

        total_returned=0,

        student=student,

        my_issued=my_issued,

        my_returned=my_returned,

        my_issued_count=my_issued_count,

        my_returned_count=my_returned_count,

        book_map=book_map

    )


# =========================================================
# BOOKS
# =========================================================

@app.route("/books")
def books():

    if "user_id" not in session:

        return redirect("/login")


    search = request.args.get(
        "search",
        ""
    ).strip()


    category = request.args.get(
        "category",
        ""
    ).strip()


    query = Book.query


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        query = query.filter(

            db.or_(

                Book.book_name.ilike(
                    f"%{search}%"
                ),

                Book.author.ilike(
                    f"%{search}%"
                ),

                Book.category.ilike(
                    f"%{search}%"
                )

            )

        )


    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    if category:

        query = query.filter_by(
            category=category
        )


    all_books = query.all()


    # -----------------------------------------------------
    # CATEGORIES
    # -----------------------------------------------------

    categories = db.session.query(
        Book.category
    ).distinct().all()


    categories = [

        item[0]

        for item in categories

        if item[0]

    ]


    return render_template(

        "books.html",

        books=all_books,

        categories=categories,

        search=search,

        selected_category=category,

        role=session.get("user_role"),

        name=session.get("user_name")

    )


# =========================================================
# MY BOOKS
# =========================================================

@app.route("/my_books")
def my_books():

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user_id" not in session:

        return redirect("/login")


    # -----------------------------------------------------
    # ADMIN CHECK
    # -----------------------------------------------------

    if session.get("user_role") == "admin":

        return redirect("/dashboard")


    # -----------------------------------------------------
    # FIND STUDENT
    # -----------------------------------------------------

    student = Student.query.filter_by(

        email=session.get("user_email")

    ).first()


    # -----------------------------------------------------
    # STUDENT NOT LINKED
    # -----------------------------------------------------

    if not student:

        return render_template(

            "my_books.html",

            student=None,

            issued_books=[],

            returned_books=[],

            book_map={}

        )


    # -----------------------------------------------------
    # ISSUED BOOKS
    # -----------------------------------------------------

    issued_books = IssueBook.query.filter_by(

        student_id=student.id,

        status="Issued"

    ).all()


    # -----------------------------------------------------
    # RETURNED BOOKS
    # -----------------------------------------------------

    returned_books = IssueBook.query.filter_by(

        student_id=student.id,

        status="Returned"

    ).all()


    # -----------------------------------------------------
    # BOOK MAP
    # -----------------------------------------------------

    all_books = Book.query.all()


    book_map = {

        book.id: book

        for book in all_books

    }


    return render_template(

        "my_books.html",

        student=student,

        issued_books=issued_books,

        returned_books=returned_books,

        book_map=book_map

    )


# =========================================================
# ADD BOOK - ADMIN
# =========================================================

@app.route(
    "/add_book",
    methods=["GET", "POST"]
)
@admin_required
def add_book():

    if request.method == "POST":

        book = Book(

            book_name=request.form.get(
                "book_name",
                ""
            ).strip(),

            author=request.form.get(
                "author",
                ""
            ).strip(),

            category=request.form.get(
                "category",
                ""
            ).strip(),

            quantity=int(
                request.form.get(
                    "quantity",
                    1
                )
            )

        )


        db.session.add(book)

        db.session.commit()


        return redirect("/books")


    return render_template(
        "add_book.html"
    )


# =========================================================
# EDIT BOOK - ADMIN
# =========================================================

@app.route(
    "/edit_book/<int:id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_book(id):

    book = Book.query.get(id)


    if not book:

        return "Book not found"


    if request.method == "POST":

        book.book_name = request.form.get(
            "book_name",
            ""
        ).strip()

        book.author = request.form.get(
            "author",
            ""
        ).strip()

        book.category = request.form.get(
            "category",
            ""
        ).strip()

        book.quantity = int(
            request.form.get(
                "quantity",
                1
            )
        )


        db.session.commit()


        return redirect("/books")


    return render_template(

        "edit_book.html",

        book=book

    )


# =========================================================
# DELETE BOOK - ADMIN
# =========================================================

@app.route(
    "/delete_book/<int:id>"
)
@admin_required
def delete_book(id):

    book = Book.query.get(id)


    if book:

        # -------------------------------------------------
        # CHECK ACTIVE ISSUE
        # -------------------------------------------------

        active_issue = IssueBook.query.filter_by(

            book_id=book.id,

            status="Issued"

        ).first()


        if active_issue:

            return (
                "This book is currently issued. "
                "Return the book before deleting it."
            )


        db.session.delete(book)

        db.session.commit()


    return redirect("/books")


# =========================================================
# STUDENTS - ADMIN ONLY
# =========================================================

@app.route("/students")
@admin_required
def students():

    all_students = Student.query.all()


    return render_template(

        "students.html",

        students=all_students,

        role=session.get("user_role"),

        name=session.get("user_name")

    )


# =========================================================
# ADD / LINK STUDENT - ADMIN
# =========================================================

@app.route(
    "/add_student",
    methods=["GET", "POST"]
)
@admin_required
def add_student():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        roll_no = request.form.get(
            "roll_no",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        course = request.form.get(
            "course",
            ""
        ).strip()


        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not name or not roll_no or not email:

            return "Name, Roll Number and Email are required"


        # =================================================
        # ROLL NUMBER CHECK
        # =================================================

        existing_student = Student.query.filter_by(

            roll_no=roll_no

        ).first()


        if existing_student:

            return "Roll number already registered"


        # =================================================
        # STUDENT EMAIL CHECK
        # =================================================

        existing_student_email = Student.query.filter_by(

            email=email

        ).first()


        if existing_student_email:

            return "This email is already linked with another student"


        # =================================================
        # FIND USER ACCOUNT
        # =================================================

        user = User.query.filter_by(

            email=email

        ).first()


        # =================================================
        # CREATE STUDENT RECORD
        # =================================================

        student = Student(

            name=name,

            roll_no=roll_no,

            email=email,

            phone=phone,

            course=course

        )


        db.session.add(student)


        # =================================================
        # LINK USER ACCOUNT
        # =================================================

        if user:

            # ---------------------------------------------
            # UPDATE USER WITH LIBRARIAN DATA
            # ---------------------------------------------

            user.name = name

            user.email = email

            user.phone = phone

            # IMPORTANT:
            # Do not change user password here.
            # Student keeps the password used during login.

            print(
                "Student account linked with User ID:",
                user.id
            )

        else:

            # -------------------------------------------------
            # NO USER ACCOUNT FOUND
            # -------------------------------------------------
            #
            # We still create the Student record.
            # Student can later register using the same email.
            #

            print(
                "No registered User found for:",
                email
            )


        db.session.commit()


        return redirect("/students")


    return render_template(
        "add_student.html"
    )


# =========================================================
# EDIT STUDENT - ADMIN
# =========================================================

@app.route(
    "/edit_student/<int:id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_student(id):

    student = Student.query.get(id)


    if not student:

        return "Student not found"


    if request.method == "POST":

        # -------------------------------------------------
        # SAVE OLD EMAIL
        # -------------------------------------------------

        old_email = student.email


        # -------------------------------------------------
        # GET NEW DATA
        # -------------------------------------------------

        new_name = request.form.get(
            "name",
            ""
        ).strip()

        new_roll_no = request.form.get(
            "roll_no",
            ""
        ).strip()

        new_email = request.form.get(
            "email",
            ""
        ).strip()

        new_phone = request.form.get(
            "phone",
            ""
        ).strip()

        new_course = request.form.get(
            "course",
            ""
        ).strip()


        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not new_name or not new_roll_no or not new_email:

            return "Name, Roll Number and Email are required"


        # =================================================
        # ROLL NUMBER DUPLICATE CHECK
        # =================================================

        duplicate_roll = Student.query.filter(

            Student.roll_no == new_roll_no,

            Student.id != student.id

        ).first()


        if duplicate_roll:

            return "Roll number already registered"


        # =================================================
        # EMAIL DUPLICATE CHECK IN STUDENT TABLE
        # =================================================

        duplicate_student_email = Student.query.filter(

            Student.email == new_email,

            Student.id != student.id

        ).first()


        if duplicate_student_email:

            return "This email is already linked with another student"


        # =================================================
        # FIND USER
        # =================================================

        user = None


        # -------------------------------------------------
        # FIRST TRY OLD EMAIL
        # -------------------------------------------------

        if old_email:

            user = User.query.filter_by(

                email=old_email

            ).first()


        # -------------------------------------------------
        # IF OLD EMAIL NOT FOUND,
        # TRY NEW EMAIL
        # -------------------------------------------------

        if not user and new_email:

            user = User.query.filter_by(

                email=new_email

            ).first()


        # =================================================
        # UPDATE STUDENT
        # =================================================

        student.name = new_name

        student.roll_no = new_roll_no

        student.email = new_email

        student.phone = new_phone

        student.course = new_course


        # =================================================
        # UPDATE LINKED USER
        # =================================================

        if user:

            user.name = new_name

            user.email = new_email

            user.phone = new_phone

            print(
                "User profile synchronized:",
                user.id
            )


        db.session.commit()


        # =================================================
        # IF CURRENTLY LOGGED-IN USER IS THIS USER
        # UPDATE SESSION
        # =================================================

        if user and session.get("user_id") == user.id:

            session["user_name"] = user.name

            session["user_email"] = user.email


        return redirect("/students")


    return render_template(

        "edit_student.html",

        student=student

    )


# =========================================================
# DELETE STUDENT - ADMIN
# =========================================================

@app.route(
    "/delete_student/<int:id>"
)
@admin_required
def delete_student(id):

    student = Student.query.get(id)


    if student:

        # -------------------------------------------------
        # CHECK ACTIVE BOOKS
        # -------------------------------------------------

        active_issue = IssueBook.query.filter_by(

            student_id=student.id,

            status="Issued"

        ).first()


        if active_issue:

            return (
                "This student currently has issued books. "
                "Return all books before deleting the student."
            )


        db.session.delete(student)

        db.session.commit()


    return redirect("/students")


# =========================================================
# ISSUE BOOK - ADMIN
# =========================================================

@app.route(
    "/issue_book",
    methods=["GET", "POST"]
)
@admin_required
def issue_book():

    students = Student.query.all()

    books = Book.query.all()


    if request.method == "POST":

        student_id = request.form.get(
            "student_id"
        )

        book_id = request.form.get(
            "book_id"
        )


        student = Student.query.get(
            student_id
        )

        book = Book.query.get(
            book_id
        )


        # -------------------------------------------------
        # STUDENT CHECK
        # -------------------------------------------------

        if not student:

            return "Student not found"


        # -------------------------------------------------
        # BOOK CHECK
        # -------------------------------------------------

        if not book:

            return "Book not found"


        # -------------------------------------------------
        # QUANTITY CHECK
        # -------------------------------------------------

        if book.quantity <= 0:

            return "Book not available"


        # -------------------------------------------------
        # CHECK DUPLICATE ACTIVE ISSUE
        # -------------------------------------------------

        existing_issue = IssueBook.query.filter_by(

            student_id=student.id,

            book_id=book.id,

            status="Issued"

        ).first()


        if existing_issue:

            return (
                "This book is already issued "
                "to this student."
            )


        # -------------------------------------------------
        # ISSUE RECORD
        # -------------------------------------------------

        issue = IssueBook(

            student_id=student.id,

            book_id=book.id,

            issue_date=datetime.now().strftime(
                "%d-%m-%Y"
            ),

            status="Issued"

        )


        # -------------------------------------------------
        # REDUCE BOOK QUANTITY
        # -------------------------------------------------

        book.quantity -= 1


        db.session.add(issue)

        db.session.commit()


        return redirect("/issue_book")


    return render_template(

        "issue.html",

        students=students,

        books=books

    )


# =========================================================
# RETURN BOOK - ADMIN
# =========================================================

@app.route(
    "/return_book",
    methods=["GET", "POST"]
)
@admin_required
def return_book():

    if request.method == "POST":

        issue_id = request.form.get(
            "issue_id"
        )


        issue = IssueBook.query.get(
            issue_id
        )


        # -------------------------------------------------
        # ISSUE CHECK
        # -------------------------------------------------

        if not issue:

            return "Issue record not found"


        # -------------------------------------------------
        # ALREADY RETURNED CHECK
        # -------------------------------------------------

        if issue.status != "Issued":

            return "This book has already been returned"


        # -------------------------------------------------
        # BOOK
        # -------------------------------------------------

        book = Book.query.get(
            issue.book_id
        )


        if not book:

            return "Book not found"


        # -------------------------------------------------
        # RETURN BOOK
        # -------------------------------------------------

        book.quantity += 1

        issue.status = "Returned"

        issue.return_date = datetime.now().strftime(
            "%d-%m-%Y"
        )


        db.session.commit()


        return redirect("/return_book")


    # -----------------------------------------------------
    # GET CURRENTLY ISSUED BOOKS
    # -----------------------------------------------------

    issued_books = IssueBook.query.filter_by(

        status="Issued"

    ).all()


    return render_template(

        "return.html",

        issued_books=issued_books

    )


# =========================================================
# STUDENT HISTORY - ADMIN ONLY
# =========================================================

@app.route("/student_history")
@admin_required
def student_history():

    # -----------------------------------------------------
    # ALL STUDENTS
    # -----------------------------------------------------

    students = Student.query.all()


    # -----------------------------------------------------
    # SELECTED STUDENT
    # -----------------------------------------------------

    student_id = request.args.get(
        "student_id"
    )


    selected_student = None

    issued_books = []

    returned_books = []


    # -----------------------------------------------------
    # FIND SELECTED STUDENT
    # -----------------------------------------------------

    if student_id:

        try:

            selected_student = Student.query.get(
                int(student_id)
            )

        except (
            ValueError,
            TypeError
        ):

            selected_student = None


        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        if selected_student:

            issued_books = IssueBook.query.filter_by(

                student_id=selected_student.id,

                status="Issued"

            ).all()


            returned_books = IssueBook.query.filter_by(

                student_id=selected_student.id,

                status="Returned"

            ).all()


    # -----------------------------------------------------
    # BOOK MAP
    # -----------------------------------------------------

    all_books = Book.query.all()


    book_map = {

        book.id: book

        for book in all_books

    }


    return render_template(

        "student_history.html",

        students=students,

        selected_student=selected_student,

        issued_books=issued_books,

        returned_books=returned_books,

        book_map=book_map,

        role=session.get("user_role"),

        name=session.get("user_name")

    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    update_database()

    app.run(
    host="0.0.0.0",
    port=5000,
    debug=False
)