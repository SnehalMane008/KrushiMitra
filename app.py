@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First, print debug info
        print(f"Login attempt: Username={username}, Password={password}")
        
        # Query to find the user
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            # Print debug info on success
            print(f"Login successful: {user}")
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Get all users for debugging
            cursor.execute("SELECT * FROM users")
            all_users = cursor.fetchall()
            print(f"All users in database: {all_users}")
            
            flash('Invalid username or password', 'danger')
        
        conn.close()
    
    return render_template('login.html') 