from flask import Flask, render_template_string, request, redirect, url_for, session
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'

PASSWORD = "kader11000"

# Templates
login_template = """<html><head><title>Login</title></head><body><form method='POST'><input type='password' name='password'><button type='submit'>Login</button></form></body></html>"""

main_template = """<html><head><title>Toolkit</title></head><body>
<h1>kader11000 Toolkit</h1>
<a href='{{ url_for('sqli_scanner') }}'>SQLi Scanner</a><br>
<a href='{{ url_for('osint_investigator') }}'>OSINT Investigator</a><br>
<a href='{{ url_for('wordpress_scanner') }}'>WordPress Scanner</a><br>
<a href='{{ url_for('android_lab') }}'>Android Exploit Lab</a><br>
<a href='{{ url_for('smb_exploiter') }}'>SMB Auto Exploiter</a><br>
<a href='{{ url_for('logout') }}'>Logout</a>
</body></html>"""

simple_template = """<html><head><title>{{ title }}</title></head><body>
<h1>{{ title }}</h1>
<form method='POST'>
<input name='input_data' placeholder='Enter input'><button type='submit'>Run</button>
</form>
{% if result %}<pre>{{ result }}</pre>{% endif %}
<a href='{{ url_for('dashboard') }}'>Back</a>
</body></html>"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
    return render_template_string(login_template)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(main_template)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/sqli-scanner', methods=['GET', 'POST'])
def sqli_scanner():
    return handle_tool("sqli_scanner.py", "SQLi Scanner")

@app.route('/osint-investigator', methods=['GET', 'POST'])
def osint_investigator():
    return handle_tool("osint_tool.py", "OSINT Investigator")

@app.route('/wordpress-scanner', methods=['GET', 'POST'])
def wordpress_scanner():
    return handle_tool("wp-scan.py", "WordPress Scanner")

@app.route('/android-lab', methods=['GET', 'POST'])
def android_lab():
    return handle_tool("android_lab.py", "Android Exploit Lab")

@app.route('/smb-exploiter', methods=['GET', 'POST'])
def smb_exploiter():
    return handle_tool("smb_auto_exploit.py", "SMB Auto Exploiter")

def handle_tool(script, title):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    result = ""
    if request.method == 'POST':
        input_data = request.form['input_data']
        try:
            cmd = f"python3 {script} {input_data}"
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            result = output.stdout + output.stderr
        except Exception as e:
            result = f"Error: {str(e)}"
    return render_template_string(simple_template, title=title, result=result)

if __name__ == '__main__':
    app.run(debug=True)
