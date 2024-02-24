from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_NAME = 'orderingSystem.db'

def is_admin(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accounts WHERE username = ? AND admin = 1', (username,))
    admin_account = cursor.fetchone()
    conn.close()
    return True if admin_account else False

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = ?', (username,))
        account = cursor.fetchone()
        if account:
            # Check if the user has been blocked
            cursor.execute('SELECT * FROM blocked_users WHERE username = ?', (username,))
            blocked_user = cursor.fetchone()
            if blocked_user and blocked_user[2] >= 5:
                msg = 'Your account has been blocked due to multiple failed login attempts. Please contact support.'
            else:
                # Verify password
                if password == account[2]:
                    session['loggedin'] = True
                    session['id'] = account[0]
                    session['username'] = account[1]
                    msg = 'Logged in successfully!'
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    # Reset the failed login attempts counter
                    cursor.execute('DELETE FROM blocked_users WHERE username = ?', (username,))
                    conn.commit()
                    conn.close()
                    if is_admin(username):
                        return redirect(url_for('adminlanding'))
                    else:
                        return redirect(url_for('regularlanding'))
                else:
                    msg = 'Incorrect username / password!'
                    # Update the failed login attempts counter
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute('INSERT OR REPLACE INTO blocked_users (username, attempts) VALUES (?, COALESCE((SELECT attempts FROM blocked_users WHERE username = ?), 0) + 1)', (username, username))
            conn.commit()
            conn.close()
        else:
            msg = 'User not found!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/adminlanding') #landing page for just admin users
def adminlanding():
    if 'loggedin' in session and is_admin(session['username']):
        return render_template('admin.html')
    else:
        return redirect(url_for('login'))

@app.route('/regularlanding')
def regularlanding():
    if 'loggedin' in session and not is_admin(session['username']):
        return render_template('regular.html')
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = ?', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # People are automatically made not an admin (the False), those that are an admin will be altered in the database
            cursor.execute('INSERT INTO accounts VALUES (NULL, ?, ?, ?, False)', (username, password, email))
            conn.commit()
            msg = 'You have successfully registered!'
        conn.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/createlanding') #the landing page when creating a new order
def createlanding():
    return render_template('create.html')

@app.route('/neworder', methods=['GET', 'POST', 'PUT'])
def neworder():
    msg = ''
    if request.method == 'POST' and 'id' in request.form and 'quantity' in request.form:
        productid = request.form['id']
        quantity = request.form['quantity']
        userid = session['id']
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # You can't order more than what is in stock
        cursor.execute('SELECT * FROM stock WHERE id = ? AND quantity < ?', (productid, quantity))
        account = cursor.fetchone()
        if account:
            msg = 'This quantity of stock is not available!'
        elif quantity == '' or productid == '':
            msg = 'Please fill out the form!'
        else:
            cursor.execute('SELECT * FROM stock WHERE id = ?', (productid,))
            account = cursor.fetchone()
            if account:
                if quantity.isdigit():
                    cursor.execute('INSERT INTO orders VALUES (NULL, ?, ?, ?, "Submitted")', (productid, userid, quantity))
                    cursor.execute('UPDATE stock SET quantity=(quantity - ?) WHERE id=?', (quantity, productid))
                    conn.commit()
                    msg = 'You have successfully placed an order!'
                else:
                    msg = 'Quantity needs to be a numerical value!'
            else:
                msg = 'This is not a valid product ID!'
        conn.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('create.html', msg=msg)

@app.route('/vieworder', methods=['GET', 'POST'])
def vieworder():
    userid = session['id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders')
    data = cursor.fetchall()
    conn.close()
    return render_template("view.html", data=data, sessionid=userid)

@app.route('/viewordernonadmin', methods=['GET', 'POST'])
def viewordernonadmin():
    userid = session['id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders')
    data = cursor.fetchall()
    conn.close()
    return render_template("viewNonAdmin.html", data=data, sessionid=userid)

@app.route('/viewall', methods=['GET', 'POST'])
def viewall():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders')
    data = cursor.fetchall()
    conn.close()
    return render_template("adminViewAll.html", data=data)

#Admin's editting order functions (includes the delete options)
@app.route('/editorder')
def editorder():
    return render_template("editOrderLanding.html")

@app.route('/editChosenOrder', methods=['GET', 'POST'])
def editChosenOrder():
    global editid
    msg = ''
    if request.method == 'POST' and 'editid' in request.form:
        editid = request.form['editid']
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (editid,))
        order = cursor.fetchall()
        conn.close()
        if order:
            return render_template('editOrderMain.html', order=order)
        else:
            msg = 'This is not a valid Order ID!'
    return render_template('editOrderLanding.html', msg=msg)

@app.route('/edittingOrder', methods=['GET', 'POST', 'PUT', 'DELETE'])
def edittingOrder():
    msg = ""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if request.method == 'POST' and ('newProduct' or 'newQuantity' or 'delete') in request.form:
        newid = request.form['newProduct']
        newquantity = request.form['newQuantity']
        delete = request.form['delete']

        if newid == '' and newquantity == '':
            if delete == 'delete' or delete == 'DELETE' or delete == 'Delete':
                cursor.execute('DELETE FROM orders WHERE id=?', (editid,))
                conn.commit()
                msg = 'You have successfully deleted this order!'
            else:
                msg = "The input was not correct."
        elif delete == '':
            if newid == '' or newquantity == '':
                msg = "Please fill out both a new ID and new Quantity. If not changing, please fill it out with the previous value."
            else:
                cursor.execute('SELECT * FROM stock WHERE id = ?', (newid,))
                account = cursor.fetchone()

                if account:
                    cursor.execute('SELECT * FROM stock WHERE id = ? AND quantity < ?', (newid, newquantity))
                    account = cursor.fetchone()

                    if account:
                        msg = 'This quantity of stock is not available!'
                    else:
                        if newquantity.isdigit():
                            cursor.execute('UPDATE orders SET productid=? WHERE id=?', (newid, editid))
                            cursor.execute('UPDATE orders SET quantity=? WHERE id=?', (newquantity, editid))
                            cursor.execute('UPDATE stock SET quantity=(quantity - ?) WHERE id=?', (newquantity, newid))
                            conn.commit()
                            msg = 'You have successfully updated your order!'
                        else:
                            msg = 'Quantity has to be a numerical value!'
                else:
                    msg = 'This is not a valid product ID!'
        else:
            msg = "You cannot delete and update!"
    conn.close()
    return render_template('editOrderMain.html', msg=msg)

#Non-admin editting order functions (does not include a delete option)
@app.route('/regulareditorder')
def regulareditorder():
    return render_template("regularEditLanding.html")

@app.route('/regularEditChosenOrder', methods=['GET', 'POST'])
def regularEditChosenOrder():
    global editid
    msg = ''
    if request.method == 'POST' and 'editid' in request.form:
        editid = request.form['editid']
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (editid,))
        order = cursor.fetchall()
        conn.close()
        if order:
            return render_template('regularEditMain.html', order=order)
        else:
            msg = 'This is not a valid Order ID!'
    return render_template('regularEditLanding.html', msg=msg)

@app.route('/regularEdittingOrder', methods=['GET', 'POST', 'PUT'])
def regularEdittingOrder():
    msg = ""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if request.method == 'POST' and ('newProduct' or 'newQuantity') in request.form:
        newid = request.form['newProduct']
        newquantity = request.form['newQuantity']

        if newid == '' or newquantity == '':
            msg = "Please fill out both a new ID and new Quantity. If not changing, please fill it out with the previous value."
        else:
            cursor.execute('SELECT * FROM stock WHERE id = ?', (newid,))
            account = cursor.fetchone()

            if account:
                cursor.execute('SELECT * FROM stock WHERE id = ? AND quantity < ?', (newid, newquantity))
                account = cursor.fetchone()

                if account:
                    msg = 'This quantity of stock is not available!'
                else:
                    if newquantity.isdigit():
                        cursor.execute('UPDATE orders SET productid=? WHERE id=?', (newid, editid))
                        cursor.execute('UPDATE orders SET quantity=? WHERE id=?', (newquantity, editid))
                        cursor.execute('UPDATE stock SET quantity=(quantity - ?) WHERE id=?', (newquantity, newid))
                        conn.commit()
                        msg = 'You have successfully updated your order!'
                    else:
                        msg = 'Quantity has to be a numerical value!'
            else:
                msg = 'This is not a valid product ID!'
    conn.close()
    return render_template('regularEditMain.html', msg=msg)
