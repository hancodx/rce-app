from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3
import hashlib
import os
import atexit

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_123')
DATABASE = 'database.db'

# Initialisation de la base au démarrage
def init_db():
    if not os.path.exists(DATABASE):
        print("🗄️ Initialisation de la base de données...")
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Table users
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
        ''')
        
        # Table data
        cursor.execute('''
        CREATE TABLE data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER
        )
        ''')
        
        # Utilisateurs
        password_hash = hashlib.md5('password123'.encode()).hexdigest()
        users = [
            ('admin', password_hash, 'admin'),
            ('user1', password_hash, 'user'),
            ('test', password_hash, 'user')
        ]
        cursor.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', users)
        
        # Données
        data_entries = [
            ('Server Stats', 'CPU: 45%, RAM: 2.3/4GB', 1),
            ('User Activity', '5 users online', 1),
            ('Backup Status', 'Last backup: 2024-01-15', 2),
            ('Security Log', 'No threats detected', 3)
        ]
        cursor.executemany('INSERT INTO data (title, content, user_id) VALUES (?, ?, ?)', data_entries)
        
        conn.commit()
        conn.close()
        print("✅ Base de données initialisée!")

# Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔐 Login RCE Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; }
        .login-container { max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .login-title { text-align: center; color: #333; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; background: #007cba; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        .btn:hover { background: #005a87; }
        .error { color: #d63031; background: #ffeaa7; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
        .demo-info { background: #dfe6e9; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1 class="login-title">🔐 Connexion</h1>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <div class="form-group">
                <input type="text" name="username" placeholder="Nom d'utilisateur" class="form-input" required>
            </div>
            <div class="form-group">
                <input type="password" name="password" placeholder="Mot de passe" class="form-input" required>
            </div>
            <button type="submit" class="btn">Se connecter</button>
        </form>
        <div class="demo-info">
            <strong>Comptes de test:</strong><br>
            👤 admin / user1 / test<br>
            🔑 password123
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📊 Dashboard RCE Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f8f9fa; }
        .header { background: #2d3436; color: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; padding: 25px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .vuln-section { background: #ffeaa7; border-left: 4px solid #e17055; padding: 20px; margin: 25px 0; border-radius: 5px; }
        .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }
        pre { background: #2d3436; color: #00b894; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: 'Courier New', monospace; }
        .btn { background: #e17055; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #d63031; }
        .logout { float: right; color: white; text-decoration: none; }
        .user-info { color: #00b894; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Dashboard de Test RCE</h1>
        <div class="user-info">
            Bienvenue, <strong>{{ username }}</strong> ({{ role }}) 
            <a href="/logout" class="logout">🚪 Déconnexion</a>
        </div>
    </div>
    
    <div class="container">
        <div class="warning">
            <h3>⚠️ AVERTISSEMENT - APPLICATION VULNÉRABLE</h3>
            <p>Cette application contient des vulnérabilités intentionnelles pour l'apprentissage de la cybersécurité.</p>
            <p><strong>NE PAS UTILISER AVEC DES DONNÉES RÉELLES!</strong></p>
        </div>
        
        <h2>📈 Données du Système</h2>
        {% for item in data %}
        <div class="card">
            <h3>{{ item[1] }}</h3>
            <p>{{ item[2] }}</p>
        </div>
        {% endfor %}
        
        <div class="vuln-section">
            <h3>🔴 Section Vulnérable - Injection SQL</h3>
            <p><em>Testez les injections SQL dans le champ de recherche</em></p>
            <form method="POST" action="/search">
                <input type="text" name="query" placeholder="Rechercher par titre..." value="{{ query }}" 
                       style="width: 70%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                <button type="submit" class="btn">🔍 Rechercher</button>
            </form>
            
            {% if search_results is defined %}
            <div style="margin-top: 20px;">
                <h4>Résultats pour "{{ query }}":</h4>
                <pre>{{ search_results }}</pre>
            </div>
            {% endif %}
        </div>
        
        <div class="vuln-section">
            <h3>🔴 Section Vulnérable - Execution de Commandes (RCE)</h3>
            <p><em>Testez l'exécution de commandes système</em></p>
            <form method="POST" action="/diagnostic">
                <input type="text" name="command" placeholder="Commande système..." value="{{ command }}" 
                       style="width: 70%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                <button type="submit" class="btn">⚡ Exécuter</button>
            </form>
            
            {% if command_output is defined %}
            <div style="margin-top: 20px;">
                <h4>Résultat de la commande:</h4>
                <pre>{{ command_output }}</pre>
            </div>
            {% endif %}
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
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            # 🔴 VULNÉRABILITÉ: Injection SQL
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password_hash}'"
            cursor.execute(query)
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[3]
                conn.close()
                return redirect(url_for('dashboard'))
            else:
                conn.close()
                return render_template_string(LOGIN_TEMPLATE, error='❌ Identifiants incorrects')
        except Exception as e:
            conn.close()
            return render_template_string(LOGIN_TEMPLATE, error=f'❌ Erreur: {str(e)}')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")
    data = cursor.fetchall()
    conn.close()
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                username=session['username'],
                                role=session['role'],
                                data=data)

@app.route('/search', methods=['POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    query = request.form['query']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # 🔴 VULNÉRABILITÉ: Injection SQL
        sql = f"SELECT * FROM data WHERE title LIKE '%{query}%'"
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        
        return render_template_string(DASHBOARD_TEMPLATE,
                                    username=session['username'],
                                    role=session['role'],
                                    data=[],
                                    query=query,
                                    search_results=results)
    except Exception as e:
        conn.close()
        return render_template_string(DASHBOARD_TEMPLATE,
                                    username=session['username'],
                                    role=session['role'],
                                    data=[],
                                    query=query,
                                    search_results=f"❌ Erreur: {str(e)}")

@app.route('/diagnostic', methods=['POST'])
def diagnostic():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    command = request.form['command']
    
    try:
        # 🔴 VULNÉRABILITÉ: RCE
        import subprocess
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=10)
        output = result
    except subprocess.TimeoutExpired:
        output = "⏰ Timeout - Commande trop longue"
    except Exception as e:
        output = f"❌ Erreur: {str(e)}"
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")
    data = cursor.fetchall()
    conn.close()
    
    return render_template_string(DASHBOARD_TEMPLATE,
                                username=session['username'],
                                role=session['role'],
                                data=data,
                                command=command,
                                command_output=output)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Application RCE Test démarrée!")
    print(f"📍 Accédez à: http://localhost:{port}")
    print("🔴 VULNÉRABILITÉS INTENTIONNELLES - PENTEST UNIQUEMENT")
    app.run(host='0.0.0.0', port=port)
