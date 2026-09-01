import os
import secrets

from flask import Flask, render_template, redirect, url_for
from routes.auth import auth_bp
from routes.teacher import teacher_bp
from routes.principal import principal_bp

app = Flask(__name__)

# Secret key for signing session cookies. Set SECRET_KEY as an environment
# variable in production; the random fallback means sessions simply won't
# survive a restart if it's unset, rather than everyone sharing one
# hardcoded key that's sitting in a public repo.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# 🔹 Register Blueprints (Auth, Teacher, Principal)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(teacher_bp, url_prefix="/teacher")
app.register_blueprint(principal_bp, url_prefix="/principal")

# 🌐 Home Route (Redirect to Login)
@app.route("/")
def home():
    return redirect(url_for("auth.login"))

@app.route("/health")
def health():
    return {"status": "ok"}

# 🌐 Error Handler (404 Page Not Found)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("auth/error.html", error="Page Not Found"), 404


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=debug_mode)