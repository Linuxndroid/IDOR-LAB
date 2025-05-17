from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = 'insecuresecret'

# Insecure user storage
users = {
    'admin': {'id': 1, 'password': 'admin', 'files': []},
    'kutapak': {'id': 2, 'password': 'kutapak', 'files': []},
    'charlie': {'id': 3, 'password': 'charlie123', 'files': []},
}

UPLOAD_FOLDER = 'user_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = users.get(username)
    if user and user['password'] == password:
        session['username'] = username
        session['user_id'] = user['id']
        return redirect(url_for('dashboard'))
    return 'Invalid credentials', 403

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    user_id = session.get('user_id')
    username = session.get('username')
    user_data = users.get(username)

    if user_data:
        return render_template('dashboard.html', username=username, user_id=user_id, files=user_data['files'])
    return 'User not found', 404

@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    user_id = request.form.get('id', type=int)
    uploaded_file = request.files['file']
    if uploaded_file:
        filename = f"user{user_id}_{uploaded_file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_file.save(filepath)
        for uname, udata in users.items():
            if udata['id'] == user_id:
                udata['files'].append(filename)
                break
    return redirect(url_for('dashboard'))

@app.route('/download/<filename>')
def download_file(filename):
    if 'username' not in session:
        return redirect(url_for('home'))
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'username' not in session:
        return redirect(url_for('home'))

    user_id = request.args.get('id', type=int) if request.method == 'GET' else request.form.get('id', type=int)
    target_user = None
    for uname, udata in users.items():
        if udata['id'] == user_id:
            target_user = uname
            break

    if not target_user:
        return 'User not found', 404

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')

        # Update username if changed
        if new_username and new_username != target_user:
            users[new_username] = users.pop(target_user)
            session['username'] = new_username
            target_user = new_username

        if new_password:
            users[target_user]['password'] = new_password

        return redirect(url_for('dashboard'))

    return render_template('edit.html', username=target_user, user_id=user_id)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
