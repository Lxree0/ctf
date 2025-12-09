from flask import Flask, render_template, request, session, redirect, url_for, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import shutil


app = Flask(__name__)
app.secret_key = "G1oRg1C7f"  # Cambialo in produzione

# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="admin",
        password="l0r3nz01306!",
        database="CTFDashboard"
)

def get_db():
    return get_db_connection()

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------


@app.route("/", methods=["GET", "POST"])
def login():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    error = None
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]  # nuova password dal form

       # -----------------------
       # ADMIN LOGIN
       # -----------------------
        if username == "admin.LG.07#":

            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            admin = cursor.fetchone()

            # se admin non esiste → errore
            if not admin:
                error = "L'account amministratore non esiste nel database."
                return render_template("login.html", error=error)

            # verifica password
            if not check_password_hash(admin["password"], password):
                error = "Password errata."
                return render_template("login.html", error=error)

            # login valido
            session["user_id"] = admin["id"]
            session["username"] = admin["username"]
            session["is_admin"] = True   

            cursor.close()
            db.close()
            return redirect(url_for("admin_dashboard"))


        # -----------------------
        # USER LOGIN
        # -----------------------
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        # Utente non esiste → crealo
        if not user:
            hashed_pw = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_pw)
            )
            db.commit()

            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

        else:
            # Utente esiste → controlla password
            if not check_password_hash(user["password"], password):
                error = "Password errata."
                return render_template("login.html", error=error)

        # login valido
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        cursor.close()
        db.close()
        return redirect(url_for("dashboard"))

    cursor.close()
    db.close()
    return render_template("login.html", error=error)

@app.route("/guest", methods=["POST"])
def guest_login():
    session["user_id"] = "guest"
    session["username"] = "Ospite"
    return redirect(url_for("dashboard"))

# ---------------------------------------------------------
# DASHBOARD (MODIFICATA PER CATEGORIE)
# ---------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    # -----------------------------
    # SE UTENTE È OSPITE
    # -----------------------------
    if session["user_id"] == "guest":
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Carico comunque le challenge (visibili)
        cursor.execute("SELECT * FROM challenges ORDER BY category, id ASC")
        all_challenges = cursor.fetchall()

        cursor.close()
        db.close()

        # Nessuna challenge completata
        completed = []

        # Organizzazione per categorie
        categorized_challenges = {}
        for challenge in all_challenges:
            category = challenge['category'].capitalize()
            categorized_challenges.setdefault(category, []).append(challenge)

        return render_template(
            "dashboard.html",
            categorized_challenges=categorized_challenges,
            completed=completed,
            username="Ospite"
        )





    

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Recupero tutte le challenge
    cursor.execute("SELECT * FROM challenges ORDER BY category, id ASC")
    all_challenges = cursor.fetchall()

    # Recupero le challenge completate dall'utente
    cursor.execute("""
        SELECT challenge_id
        FROM challenge_completion
        WHERE user_id=%s AND completed=TRUE
    """, (session["user_id"],))
    completed_challenges = cursor.fetchall()
    completed = [row["challenge_id"] for row in completed_challenges]

    # Recupero il nome utente
    cursor.execute("SELECT username FROM users WHERE id=%s", (session["user_id"],))
    user_row = cursor.fetchone()
    username = user_row["username"] if user_row else "Anonimo"

    cursor.close()
    db.close()

    # Organizzo le challenge per categoria
    categorized_challenges = {}
    for challenge in all_challenges:
        category = challenge['category'].capitalize()
        categorized_challenges.setdefault(category, []).append(challenge)

    return render_template(
        "dashboard.html",
        categorized_challenges=categorized_challenges,
        completed=completed,
        username=username   # <-- qui lo passi al template
    )






# ---------------------------------------------------------
# CHALLENGE PAGE 
# ---------------------------------------------------------
@app.route("/challenge/<int:challenge_id>")
def challenge_page(challenge_id):
    if "user_id" not in session or session["user_id"] == "guest":
        flash("Devi effettuare il login per accedere alle challenge.", "error")
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Recupero challenge
    cursor.execute("SELECT * FROM challenges WHERE id=%s", (challenge_id,))
    challenge = cursor.fetchone()
    if not challenge:
        cursor.close()
        db.close()
        return "Challenge non trovata", 404

    # Recupero username
    cursor.execute("SELECT username FROM users WHERE id=%s", (session["user_id"],))
    user_row = cursor.fetchone()
    username = user_row["username"] if user_row else "Anonimo"

    # Controllo se l'utente ha già completato la challenge
    cursor.execute("""
        SELECT completed FROM challenge_completion
        WHERE user_id=%s AND challenge_id=%s
    """, (session["user_id"], challenge_id))
    completion = cursor.fetchone()
    is_completed = completion["completed"] if completion else False

    cursor.close()
    db.close()

    # Preparo lista allegati
    attachments = []
    for f in ["attached_file", "attached_file2", "attached_file3"]:
        val = challenge.get(f)
        if val:
            if val.startswith("http://") or val.startswith("https://"):
                attachments.append({"type": "link", "url": val, "name": val})
            else:
                attachments.append({
                    "type": "file",
                    "url": url_for("static", filename=f"upload/{challenge_id}/{val}"),
                    "name": val
                })

    return render_template(
        "challenge.html",
        challenge=challenge,
        attachments=attachments,
        username=username,
        is_completed=is_completed
    )



# ---------------------------------------------------------
# SUBMIT FLAG

@app.route("/submit", methods=["POST"])
def submit():
    if "user_id" not in session:
        return redirect("/")

    # Controllo challenge_id sicuro
    challenge_id_raw = request.form.get("challenge_id")
    if not challenge_id_raw or not challenge_id_raw.isdigit():
        return "Challenge ID non valido", 400
    challenge_id = int(challenge_id_raw)

    # Controllo flag
    flag = request.form.get("flag")
    if not flag:
        return "Flag mancante", 400

    user_id = session["user_id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Recupera la flag corretta dalla challenge
    cursor.execute("SELECT flag, points FROM challenges WHERE id=%s", (challenge_id,))
    challenge = cursor.fetchone()
    if not challenge:
        cursor.close()
        db.close()
        return "Challenge non trovata", 404

    # Verifica se la flag è corretta
    is_correct = (flag == challenge["flag"])

    # Inserisci la submission nello storico
    cursor.execute("""
        INSERT INTO submissions (user_id, challenge_id, submitted_flag, is_correct)
        VALUES (%s, %s, %s, %s)
    """, (user_id, challenge_id, flag, is_correct))
    db.commit()

    # Se corretta, segna challenge completata e aggiorna punteggio
    if is_correct:
        # Inserisce o aggiorna la tabella challenge_completion
        cursor.execute("""
            INSERT INTO challenge_completion (user_id, challenge_id, completed)
            VALUES (%s, %s, TRUE)
            ON DUPLICATE KEY UPDATE completed=TRUE
        """, (user_id, challenge_id))
        db.commit()

        # Aggiorna il punteggio dell'utente
        cursor.execute("""
            UPDATE users SET score = score + %s WHERE id = %s
        """, (challenge["points"], user_id))
        db.commit()

    cursor.close()
    db.close()

    # Mostra il risultato della submission
    return render_template("result.html", result=is_correct, challenge_id=challenge_id)








# ---------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------

@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or session['username'] != 'admin.LG.07#':
        flash("Accesso negato.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Recupero utenti
    cursor.execute("SELECT id, username, score FROM users ORDER BY score DESC")
    users = cursor.fetchall()

    # Calcolo quante challenge ha completato ciascun utente
    for user in users:
        cursor.execute("""
            SELECT COUNT(*) AS completed_count
            FROM submissions
            WHERE user_id = %s AND is_correct = 1
        """, (user["id"],))
        result = cursor.fetchone()
        user["completed_count"] = result["completed_count"]
        user["score"] = user.get("score")

    cursor.close()
    conn.close()

    return render_template("admin.html", users=users)


UPLOAD_FOLDER = os.path.join("static", "upload")


@app.route('/admin/add_challenge')
def add_challenge():
    if not session.get('is_admin'):
        flash("Accesso negato: solo l'admin può aggiungere challenge.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, category FROM challenges ORDER BY id ASC")
    challenges = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('add_challenge.html', challenges=challenges)



@app.route('/admin/submit_challenge', methods=['POST'])
def submit_challenge():
    if (
        'username' not in session 
        or session['username'] != 'admin.LG.07#' 
        or not session.get('is_admin')
    ):
        flash("Accesso negato: solo l'admin può aggiungere challenge.", "danger")
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']
    flag = request.form['flag']
    category = request.form['category']
    points = request.form['points']
    hint1 = request.form.get('hint1') or None
    hint2 = request.form.get('hint2') or None

    conn = get_db_connection()
    cursor = conn.cursor()

    # Inserisco challenge base
    cursor.execute(
        "INSERT INTO challenges (title, description, flag, category, points, hint1, hint2) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (title, description, flag, category, points, hint1, hint2)
    )
    conn.commit()
    challenge_id = cursor.lastrowid  # id della nuova challenge

    # Preparo cartella upload/<id>
    challenge_folder = os.path.join(UPLOAD_FOLDER, str(challenge_id))
    os.makedirs(challenge_folder, exist_ok=True)

   # Gestione allegati
    attached_files = []
    for i in range(1, 4):
        file_field = f"attached_file{i if i>1 else ''}"
        link_field = f"{file_field}_link"

        file = request.files.get(file_field)
        link = request.form.get(link_field)

        if link:  # se è un link esterno
            attached_files.append(link)
        elif file and file.filename:
            # Estrai l'estensione dal nome originale
            ext = os.path.splitext(file.filename)[1]  # es. ".pdf", ".zip", ".png"
            
            # Rinomina il file con id challenge + indice
            filename = f"{challenge_id}_{i}{ext}"
            
            file.save(os.path.join(challenge_folder, filename))
            attached_files.append(filename)
        else:
            attached_files.append(None)

    # Update challenge con allegati
    cursor.execute(
        "UPDATE challenges SET attached_file=%s, attached_file2=%s, attached_file3=%s WHERE id=%s",
        (attached_files[0], attached_files[1], attached_files[2], challenge_id)
    )
    conn.commit()

    cursor.close()
    conn.close()

    flash("Challenge aggiunta con successo!", "success")
    return redirect(url_for('add_challenge'))


@app.route('/admin/delete_challenge/<int:challenge_id>', methods=['POST'])
def delete_challenge(challenge_id):
    if not session.get('is_admin'):
        flash("Accesso negato: solo l'admin può eliminare challenge.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM challenges WHERE id = %s", (challenge_id,))
    conn.commit()
    cursor.close()
    conn.close()

    # Elimina cartella upload/<id>
    challenge_folder = os.path.join(UPLOAD_FOLDER, str(challenge_id))
    if os.path.exists(challenge_folder):
        shutil.rmtree(challenge_folder)

    flash("Challenge eliminata con successo!", "success")
    return redirect(url_for('add_challenge'))



@app.route("/logout")
def logout():
    session.clear()   # rimuove tutte le informazioni della sessione
    return redirect(url_for("login"))


@app.route("/PlatformCred")
def PlatformCred():
    return render_template("PlatformCred.html")

@app.route("/contact")
def contact():
    return render_template("Contact.html")

@app.route("/about")
def about():
    return render_template("About.html")


@app.route("/stats")
def stats():
    if "user_id" not in session:
        return redirect("/")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Recupero utente
    cursor.execute("SELECT username, score FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()

    # Recupero challenge
    cursor.execute("SELECT * FROM challenges ORDER BY category, id ASC")
    challenges = cursor.fetchall()

    cursor.execute("SELECT challenge_id FROM challenge_completion WHERE user_id=%s AND completed=TRUE", (session["user_id"],))
    completed_challenges = cursor.fetchall()
    completed = [row["challenge_id"] for row in completed_challenges]

    cursor.close()
    db.close()

    return render_template(
        "stats.html",
        username=user["username"],
        score=user["score"],
        challenges=challenges,
        completed=completed,
        completed_count=len(completed),
        remaining_count=len(challenges) - len(completed)
    )

if __name__ == "__main__":
    app.run(debug=True)
