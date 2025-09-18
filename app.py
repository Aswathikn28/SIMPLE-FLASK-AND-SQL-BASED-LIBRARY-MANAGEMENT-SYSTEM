from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="user10",          
    password="pass1",  
    database="db2"
)
cur = conn.cursor(dictionary=True)

# Home Page - List all books
@app.route('/')
def index():
    search = request.args.get('search')
    if search:
        cur.execute("SELECT * FROM Books WHERE title LIKE %s OR author LIKE %s", (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("SELECT * FROM Books")
    books = cur.fetchall()
    return render_template('index.html', books=books)

# Add Book
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        cur.execute("INSERT INTO Books (title, author) VALUES (%s, %s)", (title, author))
        conn.commit()
        return redirect('/')
    return render_template('add_book.html')

# Borrow Book
@app.route('/borrow/<int:book_id>', methods=['GET', 'POST'])
def borrow_book(book_id):
    if request.method == 'POST':
        member_name = request.form['name']
        member_email = request.form['email']

        # Add member
        cur.execute("INSERT INTO Members (name, email) VALUES (%s, %s)", (member_name, member_email))
        conn.commit()
        member_id = cur.lastrowid

        # Borrow book
        cur.execute("UPDATE Books SET available=0 WHERE book_id=%s", (book_id,))
        cur.execute("INSERT INTO Borrow_Records (book_id, member_id) VALUES (%s, %s)", (book_id, member_id))
        conn.commit()
        return redirect('/')
    return render_template('borrow_book.html', book_id=book_id)

# Return Book Page
# @app.route('/return', methods=['GET', 'POST'])
# def return_page():
#     message = ""
#     if request.method == 'POST':
#         book_id = request.form['book_id']

#         # Check if book is borrowed
#         cur.execute("SELECT record_id, borrow_date FROM Borrow_Records WHERE book_id=%s AND return_date IS NULL", (book_id,))
#         record = cur.fetchone()
#         if record:
#             record_id = record['record_id']
#             borrow_date = record['borrow_date']
#             return_date = datetime.now().date()

#             # Update borrow record
#             cur.execute("UPDATE Borrow_Records SET return_date=%s WHERE record_id=%s", (return_date, record_id))
#             # Update book availability
#             cur.execute("UPDATE Books SET available=1 WHERE book_id=%s", (book_id,))
#             conn.commit()

#             # Calculate late fee (7 days allowed)
#             if isinstance(borrow_date, str):
#                 borrow_date_obj = datetime.strptime(borrow_date, "%Y-%m-%d").date()
#             else:
#                 borrow_date_obj = borrow_date
#             late_days = (return_date - borrow_date_obj - timedelta(days=7)).days
#             fee = max(0, late_days)
#             message = f"Book returned successfully! Late fee: ${fee}"
#         else:
#             message = "Invalid Book ID or book not borrowed."
#     return render_template('return_book.html', message=message)


@app.route('/return/<int:book_id>')
def return_direct(book_id):
    # Check if book is borrowed
    cur.execute("SELECT record_id, borrow_date FROM Borrow_Records WHERE book_id=%s AND return_date IS NULL", (book_id,))
    record = cur.fetchone()
    if record:
        record_id = record['record_id']
        borrow_date = record['borrow_date']
        return_date = datetime.now().date()

        # Update record and book availability
        cur.execute("UPDATE Borrow_Records SET return_date=%s WHERE record_id=%s", (return_date, record_id))
        cur.execute("UPDATE Books SET available=1 WHERE book_id=%s", (book_id,))
        conn.commit()
    return redirect('/')


# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
