"""
MINI PORTAIL EMPLOYES - VERSION VOLONTAIREMENT VULNERABLE 
Chaque faille est signalée par un commentaire [FAILLE n].
Pages : /  /login  /search  /ping  /load  /fetch
"""
import os
import re
import secrets
import sqlite3
import subprocess
import hashlib
import yaml
import requests
from flask import Flask, request, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# [CORRECTIF 1] Le secret vient d'une variable d'environnement, jamais du code
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

DB = "users.db"

# ---------------------------------------------------------------------------
# Mise en page HTML commune à toutes les pages (simple : un en-tête + un pied)
# ---------------------------------------------------------------------------
HEAD = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Portail Employés</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 720px; margin: 30px auto; padding: 0 15px; }
  nav a { margin-right: 14px; }
  .warn { background: #ffe0e0; border: 1px solid #c00; padding: 8px; }
  .ok { color: green; } .ko { color: #c00; }
  input { padding: 6px; margin: 4px 0; } button { padding: 6px 12px; }
  pre { background: #f4f4f4; padding: 10px; }
</style></head><body>
<p class="warn">&#9888; Application VULNERABLE</p>
<nav><a href="/">Accueil</a><a href="/login">Connexion</a><a href="/search">Recherche</a>
<a href="/ping">Diagnostic réseau</a><a href="/load">Import config</a><a href="/fetch">Aperçu URL</a></nav>
<hr>
"""
FOOT = "</body></html>"


def page(title, body):
    """Assemble le HTML final : en-tête + titre + contenu + pied de page."""
    return HEAD + "<h1>" + title + "</h1>" + body + FOOT


def init_db():
    """Crée la base SQLite avec un utilisateur admin / admin123."""
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    # [CORRECTIF 2] Hash salé et lent (PBKDF2/scrypt) au lieu de MD5
    pwd = generate_password_hash("admin123")
    conn.execute("DELETE FROM users")
    conn.execute("INSERT INTO users VALUES ('admin', ?)", (pwd,))
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return page("Portail Employés", "<p>Bienvenue ! Utilisez le menu pour naviguer.</p>")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = """<form method="post">
      <input name="username" placeholder="Nom d'utilisateur"><br>
      <input name="password" type="password" placeholder="Mot de passe"><br>
      <button>Se connecter</button></form>"""
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        pwd_hash = hashlib.md5(password.encode()).hexdigest()
        conn = sqlite3.connect(DB)
        # [FAILLE 3] INJECTION SQL : requête construite par concaténation (Bandit B608)
        # Attaque : utilisateur  admin' --   (mot de passe quelconque)
        query = "SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, pwd_hash)
        row = conn.execute(query).fetchone()
        conn.close()
        message = ("<p class='ok'>Connexion réussie. Bienvenue !</p>" if row
                   else "<p class='ko'>Identifiants invalides.</p>")
    return page("Connexion", form + message)


@app.route("/search")
def search():
    q = request.args.get("q", "")
    form = """<form method="get"><input name="q" placeholder="Nom d'un employé">
              <button>Rechercher</button></form>"""
    result = "<p>Résultats pour : %s</p><p>Aucun employé trouvé.</p>" % q if q else ""
    # [FAILLE 4] XSS / SSTI : l'entrée utilisateur est insérée DANS le template
    # Attaque : q = <script>alert(1)</script>   ou   q = {{7*7}}
    return render_template_string(page("Recherche d'employés", form + result))


@app.route("/ping")
def ping():
    form = """<form method="get"><input name="host" placeholder="127.0.0.1">
              <button>Ping</button></form>"""
    host = request.args.get("host", "")
    out = ""
    if host:
        # [FAILLE 5] INJECTION DE COMMANDE : shell=True + entrée non validée (Bandit B602)
        # Attaque : host = 127.0.0.1; cat /etc/passwd
        out = "<pre>" + subprocess.check_output("ping -c 1 " + host, shell=True).decode() + "</pre>"
    return page("Diagnostic réseau", form + out)


@app.route("/load")
def load():
    form = """<form method="get"><input name="data" placeholder="clé: valeur" size="40">
              <button>Importer</button></form>"""
    data = request.args.get("data", "")
    out = ""
    if data:
        # [FAILLE 6] DESERIALISATION DANGEREUSE : yaml.load avec Loader complet (Bandit B506)
        # Attaque : data = !!python/object/apply:os.system ["id"]
        out = "<pre>" + str(yaml.load(data, Loader=yaml.Loader)) + "</pre>"
    return page("Import de configuration YAML", form + out)


@app.route("/fetch")
def fetch():
    form = """<form method="get"><input name="url" placeholder="http://example.com" size="40">
              <button>Afficher</button></form>"""
    url = request.args.get("url", "")
    out = ""
    if url:
        # [FAILLE 7] SSRF (n'importe quelle URL, même interne) + pas de timeout (Bandit B113)
        out = "<pre>" + requests.get(url).text[:500] + "</pre>"
    return page("Aperçu d'une URL", form + out)


if __name__ == "__main__":
    init_db()
    # [FAILLE 8] debug=True (console de debug = exécution de code à distance) + 0.0.0.0
    # (Bandit B201 et B104)
    app.run(host="0.0.0.0", port=5000, debug=True)
