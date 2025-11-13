from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3
import hashlib
import os
import subprocess

app = Flask(__name__)
app.secret_key = 'dev_key_123'

# Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f2f5; }
        .login-box { background: white; padding: 30px; max-width: 400px; margin: 100px auto; border-radius: 10px; }
        input { width: 100%; padding: 10px; margin: 10px 0; }
        button { width: 100%; padding: 10px; background: #007cba; color: white; border: none; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Connexion</h2>
        {% if error %}<div style="color:red">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Nom d'utilisateur" required>
            <input type="password" name="password" placeholder="Mot de passe" required>
            <button type="submit">Se connecter</button>
        </form>
        <p>Utilisateurs: admin / user1 / test<br>Mot de passe: password123</p>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        body { font-family: Arial; margin: 0; }
        .header { background: #333; color: white; padding: 15px; }
        .container { padding: 20px; }
        .rce-section { background: #ffe6e6; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Dashboard - {{ username }}</h1>
        <a href="/logout" style="color:white; float:right">Déconnexion</a>
    </div>
    
    <div class="container">
        <div class="rce-section">
            <h3>Test RCE - Exécution de Commandes</h3>
            <form method="POST" action="/diagnostic">
                <input type="text" name="command" placeholder="Entrez votre commande..." style="width:70%">
                <button type="submit">Exécuter</button>
            </form>
            {% if command_output %}<pre>{{ command_output }}</pre>{% endif %}
        </div>
    </div>
</body>
</html>
'''

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Authentification sécurisée
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password_hash))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            conn.close()
            return render_template_string(LOGIN_TEMPLATE, error='Identifiants incorrects')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")
    data = cursor.fetchall()
    conn.close()
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                username=session['username'],
                                role=session['role'],
                                data=data)

@app.route('/diagnostic', methods=['POST'])
def diagnostic():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    command = request.form['command']
    
    # 🔴 RCE VULNÉRABILITÉ
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=5)
        output = result
    except Exception as e:
        output = f"Erreur: {str(e)}"
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")
    data = cursor.fetchall()
    conn.close()
    
    return render_template_string(DASHBOARD_TEMPLATE,
                                username=session['username'],
                                role=session['role'],
                                data=data,
                                command_output=output)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists('database.db'):
        print("Exécutez d'abord: python database.py")
        exit(1)
    app.run(host='0.0.0.0', port=5000, debug=True)