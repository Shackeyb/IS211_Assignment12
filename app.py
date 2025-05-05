from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Database connection
def get_db():
    conn = sqlite3.connect('hw13.db')
    conn.row_factory = sqlite3.Row
    return conn


# Part II: Login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Part III: Dashboard

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db()
    students = conn.execute('SELECT * FROM students').fetchall()
    quizzes = conn.execute('SELECT * FROM quizzes').fetchall()
    return render_template('dashboard.html', students=students, quizzes=quizzes)


# Part IV: Add Students

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        first = request.form['first_name']
        last = request.form['last_name']
        conn = get_db()
        try:
            conn.execute("INSERT INTO students (first_name, last_name) VALUES (?, ?)", (first, last))
            conn.commit()
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Error adding student.')
    return render_template('add_student.html')


# Part V: Add Quizzes

@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = request.form['num_questions']
        date = request.form['quiz_date']
        conn = get_db()
        try:
            conn.execute("INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)",
                         (subject, num_questions, date))
            conn.commit()
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Error adding quiz.')
    return render_template('add_quiz.html')


# Part VI: View Student Quiz Results

@app.route('/student/<int:student_id>')
def student_results(student_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    results = conn.execute("""
        SELECT results.score, quizzes.subject, quizzes.quiz_date
        FROM results
        JOIN quizzes ON results.quiz_id = quizzes.id
        WHERE results.student_id = ?
    """, (student_id,)).fetchall()
    return render_template('student_results.html', student=student, results=results)


# Part VII: Add Quiz Result

@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db()
    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']
        try:
            conn.execute("INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)",
                         (student_id, quiz_id, score))
            conn.commit()
            return redirect(url_for('dashboard'))
        except:
            flash('Error adding result.')
    students = conn.execute("SELECT * FROM students").fetchall()
    quizzes = conn.execute("SELECT * FROM quizzes").fetchall()
    return render_template('add_result.html', students=students, quizzes=quizzes)

if __name__ == '__main__':
    app.run(debug=True)