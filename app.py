from flask import Flask, render_template, request
import smtplib, ssl, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

def send_bulk(sender, password, subject, body, recipients, smtp="smtp.gmail.com", port=465):
    results = []
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp, int(port), context=context) as server:
            server.login(sender, password)
            for r in recipients:
                r = r.strip()
                if not r: 
                    continue
                try:
                    msg = MIMEMultipart()
                    msg["From"], msg["To"], msg["Subject"] = sender, r, subject or "No Subject"
                    # Send as plain text unless user pasted HTML
                    subtype = "html" if ("<" in body and ">" in body) else "plain"
                    msg.attach(MIMEText(body, subtype))
                    server.sendmail(sender, r, msg.as_string())
                    results.append((r, "sent"))
                except Exception as e:
                    results.append((r, f"failed: {str(type(e).__name__)}"))
    except Exception as e:
        return None, f"Connection/Login error: {str(e)}"
    return results, None

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    sender = request.form.get("email","").strip()
    password = request.form.get("password","")
    subject = request.form.get("subject","").strip()
    body = request.form.get("message","")
    raw = (request.form.get("recipients","") or "")
    smtp = request.form.get("smtp_server","smtp.gmail.com").strip()
    port = request.form.get("port","465").strip()

    recipients = [x.strip() for x in raw.replace(";", ",").replace("\n", ",").split(",") if x.strip()]
    results, error = send_bulk(sender, password, subject, body, recipients, smtp, port)
    return render_template("result.html", error=error, results=results, subject=subject, count=len(recipients))

if __name__ == "__main__":
    # Local dev
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))