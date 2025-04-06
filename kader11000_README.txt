
kader11000_tool – Remote Payload Injection & Management Tool

Overview
--------
This tool is a Flask-based web application that enables:
- Secure login with admin and user roles
- Managing remote targets (via SSH using Paramiko)
- Uploading and injecting payloads into bootloader files
- Generating professional HTML reports
- Logging all activities
- Password-protected access

Requirements
------------
- Python 3.8+
- pip

Installation
------------
1. Clone the project or unzip the provided archive.
2. Install dependencies:
   pip install flask paramiko

3. Ensure a SQLite database exists:
   If not, a default one will be created at users.db with admin user:
   - Username: admin
   - Password: admin

Usage
-----
1. Run the application:
   python kader11000_tool.py

2. Access the Web Interface:
   http://127.0.0.1:5000

3. Login with credentials:
   - Admin login: Can manage targets, view logs, and perform injections.
   - User login: Can perform injections and upload files.

Features
--------
1. Upload Bootloader File
   - Go to Upload
   - Choose a bootloader file to upload

2. Inject Payload
   - Provide a base64 payload string
   - Choose a previously uploaded bootloader
   - Generates an injected file and downloadable HTML report

3. Remote Command Execution
   - Admin can send commands to all registered SSH targets

4. Targets Management
   - Add, Edit, or Delete remote targets (IP, Username, Password)

5. Activity Logs
   - All actions are stored in logs table
   - Viewable only by Admin

Output
------
- Injected files are saved inside the /k4log/ directory
- HTML reports are archived in the same directory

Security
--------
- Access protected by login system
- Logs maintained for auditing
