from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os
import csv
from datetime import datetime

app = Flask(__name__)

DB_NAME = "expenses.db"

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

init_db()

@app.route("/")
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    expenses = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    chart_data = cursor.fetchall()

    conn.close()
    return render_template("index.html", expenses=expenses, total=total, chart_data=chart_data)

@app.route("/add", methods=["POST"])
@app.route("/add", methods=["POST"])
def add_expense():
    title = request.form.get("title")
    amount = float(request.form.get("amount"))  # ✅ fix
    category = request.form.get("category")
    date = request.form.get("date") or datetime.today().strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (title, amount, category, date) VALUES (?, ?, ?, ?)",
                   (title, amount, category, date))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/charts")
def charts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    chart_data = cursor.fetchall()
    conn.close()
    return render_template("charts.html", chart_data=chart_data)

@app.route("/barchart")
def barchart():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT substr(date, 1, 7) as month, SUM(amount) 
        FROM expenses GROUP BY month ORDER BY month
    """)
    bar_data = cursor.fetchall()
    conn.close()
    return render_template("barchart.html", bar_data=bar_data)

@app.route("/export/csv")
def export_csv():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    data = cursor.fetchall()
    conn.close()

    filename = "expenses.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Title", "Amount", "Category", "Date"])
        writer.writerows(data)

    return send_file(filename, as_attachment=True)

@app.route("/filter", methods=["GET"])
@app.route("/filter", methods=["GET"])
def filter_expenses():
    category = request.args.get("category", "All")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = "SELECT * FROM expenses WHERE 1=1"
    total_query = "SELECT SUM(amount) FROM expenses WHERE 1=1"
    params = []

    if category != "All":
        query += " AND category = ?"
        total_query += " AND category = ?"
        params.append(category)
    if start_date:
        query += " AND date >= ?"
        total_query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        total_query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date DESC"

    cursor.execute(query, params)
    expenses = cursor.fetchall()

    cursor.execute(total_query, params)
    total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    chart_data = cursor.fetchall()

    conn.close()
    return render_template("index.html", expenses=expenses, total=total, chart_data=chart_data,
                           category_filter=category, start_date=start_date, end_date=end_date)
@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title")
        amount = float(request.form.get("amount"))
        category = request.form.get("category")
        date = request.form.get("date")

        cursor.execute("""UPDATE expenses 
                          SET title = ?, amount = ?, category = ?, date = ? 
                          WHERE id = ?""",
                       (title, amount, category, date, expense_id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    # GET request → fetch existing data
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    expense = cursor.fetchone()
    conn.close()
    return render_template("edit.html", expense=expense)
    
@app.route('/download_csv')
def download_csv():
    conn = sqlite3.connect("expenses.db")
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    csv_path = os.path.join(os.getcwd(), "expenses.csv")
    df.to_csv(csv_path, index=False)
    conn.close()
    return send_file(csv_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
