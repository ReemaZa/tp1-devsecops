# TP DevSecOps 1 - SAST & SCA : "Mini Portail Employés"
- vulnerable/ : portail Flask avec 8 failles + dépendances vulnérables
- fixed/      : version corrigée
- scripts/    : scans Bandit, SonarQube, pip-audit, OWASP Dependency-Check
- docker-compose.sonar.yml : serveur SonarQube

Lancer : cd vulnerable && docker build -t tp-vuln . && docker run --rm -p 5000:5000 tp-vuln
Puis ouvrir http://localhost:5000

Attaques de démo (version vulnérable) :
- /login      : utilisateur  admin' --   + mot de passe quelconque
- /search     : <script>alert(1)</script>   ou   {{7*7}}
- /ping       : 127.0.0.1; cat /etc/passwd
- /load       : !!python/object/apply:os.getcwd []
- /fetch      : http://127.0.0.1:5000/   (le serveur s'appelle lui-même = SSRF)
