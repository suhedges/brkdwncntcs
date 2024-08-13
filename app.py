from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
from collections import defaultdict
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random key for session encryption

# Update the session configuration to ensure it is temporary
app.config['SESSION_PERMANENT'] = False
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True
)

PASSWORD = "1234"
MAX_ATTEMPTS = 3
LOCKOUT_TIME = timedelta(minutes=10)
IP_LOCKOUT_DURATION = timedelta(hours=1)

failed_attempts = defaultdict(list)
locked_ips = {}

def is_ip_locked(ip):
    if ip in locked_ips:
        lockout_end = locked_ips[ip]
        if datetime.now() < lockout_end:
            return True
        else:
            del locked_ips[ip]
    return False

def log_failed_attempt(ip):
    failed_attempts[ip].append(datetime.now())
    if len(failed_attempts[ip]) > MAX_ATTEMPTS:
        failed_attempts[ip] = failed_attempts[ip][-MAX_ATTEMPTS:]

    attempts = failed_attempts[ip]
    if len(attempts) == MAX_ATTEMPTS and attempts[-1] - attempts[0] < LOCKOUT_TIME:
        locked_ips[ip] = datetime.now() + IP_LOCKOUT_DURATION
        failed_attempts[ip] = []

@app.route('/', methods=['GET', 'POST'])
def login():
    ip = request.remote_addr

    if is_ip_locked(ip):
        return render_template('login.html', message="Too many failed attempts. Please try again later.", disabled=True)

    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('notice'))
        else:
            log_failed_attempt(ip)
            if is_ip_locked(ip):
                return render_template('login.html', message="Too many failed attempts. Please try again later.", disabled=True)
            else:
                return render_template('login.html', message="Incorrect password. Please try again.", disabled=False)

    return render_template('login.html', message="", disabled=False)

@app.route('/notice')
def notice():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template('notice.html')

@app.route('/contacts')
def contacts():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template('contacts.html')

if __name__ == '__main__':
    app.run(debug=True)
