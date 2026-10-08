"""
MINI PORTAIL EMPLOYES - VERSION CORRIGEE
Mêmes pages que la version vulnérable. Chaque correctif est signalé par [CORRECTIF n].
Règle d'or : le contenu utilisateur passe TOUJOURS par une variable Jinja ({{ variable }}),
qui l'échappe automatiquement, et jamais par une concaténation de texte.
"""
import os
import re
import secrets
import sqlite3
import subprocess  # nosec B404 - utilisé de façon sécurisée (voir /ping)
from urllib.parse import urlparse

import yaml
import requests
from flask import Flask, request, render_template_string, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# [CORRECTIF 1] Le secret vient d'une variable d'environnement, jamais du code
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

DB = "users.db"

HEAD = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Portail Employés</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 720px; margin: 30px auto; padding: 0 15px; }
  nav a { margin-right: 14px; }
  .ok { color: green; } .ko { color: #c00; }
  input { padding: 6px; margin: 4px 0; } button { padding: 6px 12px; }
  pre { background: #f4f4f4; padding: 10px; }
</style></head><body>
<nav><a href="/">Accueil</a><a href="/login">Connexion</a><a href="/search">Recherche</a>
<a href="/ping">Diagnostic réseau</a><a href="/load">Import config</a><a href="/fetch">Aperçu URL</a></nav>
<hr>
"""
FOOT = "</body></html>"


def page(title, body):
    """Assemble le HTML. Seuls des textes CONSTANTS sont concaténés ici (jamais d'entrée utilisateur)."""
    return HEAD + "<h1>" + title + "</h1>" + body + FOOT


def init_db():
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
    return render_template_string(
        page("Portail Employés", "<p>Bienvenue ! Utilisez le menu pour naviguer.</p>"))


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
        conn = sqlite3.connect(DB)
        # [CORRECTIF 3] Requête PARAMETREE : le « ? » fait traiter l'entrée comme une donnée
        row = conn.execute("SELECT password FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if row and check_password_hash(row[0], password):
            message = "<p class='ok'>Connexion réussie. Bienvenue !</p>"
        else:
            message = "<p class='ko'>Identifiants invalides.</p>"
    return render_template_string(page("Connexion", form + message))


@app.route("/search")
def search():
    q = request.args.get("q", "")
    form = """<form method="get"><input name="q" placeholder="Nom d'un employé">
              <button>Rechercher</button></form>"""
    # [CORRECTIF 4] q est passé comme VARIABLE du template ({{ q }}) : Jinja2 l'échappe
    result = "<p>Résultats pour : {{ q }}</p><p>Aucun employé trouvé.</p>" if q else ""
    return render_template_string(page("Recherche d'employés", form + result), q=q)


# Un nom d'hôte / une IP ne contient que ces caractères
HOST_RE = re.compile(r"^[A-Za-z0-9.\-]{1,253}$")


@app.route("/ping")
def ping():
    form = """<form method="get"><input name="host" placeholder="127.0.0.1">
              <button>Ping</button></form>"""
    host = request.args.get("host", "")
    out = ""
    if host:
        # [CORRECTIF 5] Liste blanche de caractères + pas de shell + arguments en liste + timeout
        if not HOST_RE.match(host):
            abort(400, "Hôte invalide")
        result = subprocess.run(  # nosec B603 - arguments en liste, entrée validée par regex
            ["ping", "-c", "1", host], capture_output=True, text=True, timeout=5, check=False)
        out = "<pre>{{ out }}</pre>"
        return render_template_string(page("Diagnostic réseau", form + out), out=result.stdout)
    return render_template_string(page("Diagnostic réseau", form))


@app.route("/load")
def load():
    form = """<form method="get"><input name="data" placeholder="clé: valeur" size="40">
              <button>Importer</button></form>"""
    data = request.args.get("data", "")
    if data:
        # [CORRECTIF 6] safe_load ne construit que des types simples (dict, list, str...)
        parsed = str(yaml.safe_load(data))
        return render_template_string(
            page("Import de configuration YAML", form + "<pre>{{ out }}</pre>"), out=parsed)
    return render_template_string(page("Import de configuration YAML", form))


@app.route("/fetch")
def fetch():
    form = """<form method="get"><input name="url" placeholder="http://example.com" size="40">
              <button>Afficher</button></form>"""
    url = request.args.get("url", "")
    if url:
        # [CORRECTIF 7] Schéma limité à http(s) + timeout
        # (pour une protection SSRF complète : liste blanche de domaines, voir README)
        if urlparse(url).scheme not in ("http", "https"):
            abort(400, "URL invalide")
        text = requests.get(url, timeout=5).text[:500]
        return render_template_string(
            page("Aperçu d'une URL", form + "<pre>{{ out }}</pre>"), out=text)
    return render_template_string(page("Aperçu d'une URL", form))


if __name__ == "__main__":
    init_db()
    # [CORRECTIF 8] debug désactivé, hôte configurable (127.0.0.1 par défaut)
    app.run(host=os.environ.get("APP_HOST", "127.0.0.1"), port=5000, debug=False)
