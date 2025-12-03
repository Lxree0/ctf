from flask import Flask, render_template, request, session, redirect, url_for, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import mysql.connector

app = Flask(__name__)
app.secret_key = "G10RG1C7F"

# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="192.168.51.245",
        user="admctf",
        password="l0r3nz01306!",
        database="ctfdashboard"
)
'''
def get_db_connection():
    return mysql.connector.connect(
        host="172.0.0.1",
        user="admin",
        password="l0r3nz01306!",
        database="ctfdashboard"
)
'''

def get_db():
    return get_db_connection()

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------


@app.route("/", methods=["GET", "POST"])
def login():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    #prende tutti i team tranne quello admin (id=1)
    cursor.execute("SELECT * FROM ctf_groups WHERE id != %s", (1,))
    teams = cursor.fetchall()

    error = None
    
    if request.method == "POST":
        username = request.form["username"]
        team_id = request.form["team_id"]
        
        if username == "admin.LG.07#":
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()


            session["user_id"] = user["id"]
            session["username"] = username
            session["group_id"] = user["group_id"]

            cursor.close()
            db.close()
            return redirect(url_for('admin_dashboard'))
        



        # Controlla se lo username esiste già (indipendentemente dal team)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Se esiste, verifica se il team corrisponde
            if str(existing_user["group_id"]) != team_id:
                error = "Questo username è già registrato in un altro team."
                return render_template("login.html", teams=teams, error=error)
            else:
                user = existing_user
        else:
            # Se non esiste, crealo
            try:
                cursor.execute(
                    "INSERT INTO users (username, group_id) VALUES (%s, %s)",
                    (username, team_id)
                )
                db.commit()

                # Recupera l'utente appena creato
                cursor.execute("SELECT * FROM users WHERE username=%s AND group_id=%s", (username, team_id))
                user = cursor.fetchone()
            except Exception as e:
                error = "Errore durante la creazione dell'utente."
                return render_template("login.html", teams=teams, error=error)
        
        cursor.close()
        db.close()

        # Imposta la sessione
        session["user_id"] = user["id"]
        session["username"] = username
        session["group_id"] = user["group_id"]

     
        if username == "admin.LG.07#":
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('dashboard'))
    cursor.close()
    db.close()
    return render_template("login.html", teams=teams)


# ---------------------------------------------------------
# DASHBOARD (MODIFICATA PER CATEGORIE)
# ---------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Recupera tutte le challenge
    cursor.execute("SELECT * FROM challenges ORDER BY category, id ASC")
    all_challenges = cursor.fetchall()

    # Recupera le challenge completate dal team
    cursor.execute("""
        SELECT challenge_id
        FROM challenge_completion
        WHERE group_id=%s AND completed=TRUE
    """, (session["group_id"],))
    completed_challenges = cursor.fetchall()
    completed = [row["challenge_id"] for row in completed_challenges]

    cursor.close()
    db.close()

    # Raggruppa le challenge per categoria
    categorized_challenges = {}
    for challenge in all_challenges:

        category = challenge['category'].capitalize() 
        if category not in categorized_challenges:
            categorized_challenges[category] = []
        categorized_challenges[category].append(challenge)

    return render_template("dashboard.html", 
                           categorized_challenges=categorized_challenges, 
                           completed=completed)





# ---------------------------------------------------------
# CHALLENGE PAGE 
# ---------------------------------------------------------
@app.route("/challenge/<int:challenge_id>")
def challenge_page(challenge_id):
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Prendi challenge richiesta
    cursor.execute("SELECT * FROM challenges WHERE id=%s", (challenge_id,))
    challenge = cursor.fetchone()
    if not challenge:
        cursor.close()
        db.close()
        return "Challenge non trovata", 404

    # Trova l'ultima challenge completata dall'utente
    cursor.execute("""
        SELECT MAX(challenge_id) as last_completed 
        FROM submissions 
        WHERE user_id=%s AND is_correct=1
    """, (session["user_id"],))
    last = cursor.fetchone()
    last_completed = last["last_completed"] or 0  # Se nulla, 0

    # Blocca accesso se l'utente non ha completato la challenge precedente
    # ATTENZIONE: Questa logica è sequenziale (ID successivo), non tiene conto della categoria.
    if challenge_id > last_completed + 1:
        cursor.close()
        db.close()
        flash("Devi completare le challenge precedenti prima!")
        return redirect("/dashboard")

    cursor.close()
    db.close()
    return render_template("challenge.html", challenge=challenge)



# ---------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------

@app.route('/admin')
def admin_dashboard():
    
    if 'username' not in session or session['username'] != 'admin.LG.07#':
        flash("Accesso negato: solo l'admin può vedere questa pagina.", "danger")
        return redirect(url_for('login'))  

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Recupera tutti i gruppi
    cursor.execute("SELECT * FROM ctf_groups")
    groups = cursor.fetchall()

    # Per ogni gruppo, recupera lo stato delle CTF completate
    for group in groups:
        group_id = group['id']
        cursor.execute("""
            SELECT c.id, c.title,
            (SELECT MAX(is_correct) FROM submissions s 
             WHERE s.challenge_id = c.id 
             AND s.user_id IN (SELECT id FROM users WHERE group_id=%s)
            ) AS completed
            FROM challenges c
            ORDER BY c.id ASC
        """, (group_id,))
        challenges = cursor.fetchall()

        # Sostituisci il valore booleano "completed" con "Si" se è vero
        for challenge in challenges:
            challenge['completed'] = "Si" if challenge['completed'] else "No"
        
        group['challenges'] = challenges

    cursor.close()
    conn.close()

    return render_template('admin.html', groups=groups)

@app.route('/admin/add_challenge')
def add_challenge():
    if 'username' not in session or session['username'] != 'admin.LG.07#':
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
    if 'username' not in session or session['username'] != 'admin.LG.07#':
        flash("Accesso negato: solo l'admin può aggiungere challenge.", "danger")
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']
    flag = request.form['flag']
    category = request.form['category']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO challenges (title, description, flag, category) VALUES (%s, %s, %s, %s)",
        (title, description, flag, category)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Challenge aggiunta con successo!", "success")
    return redirect(url_for('add_challenge'))


@app.route('/admin/delete_challenge/<int:challenge_id>', methods=['POST'])
def delete_challenge(challenge_id):
    if 'username' not in session or session['username'] != 'admin.LG.07#':
        flash("Accesso negato: solo l'admin può eliminare challenge.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM challenges WHERE id = %s", (challenge_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Challenge eliminata con successo!", "success")
    return redirect(url_for('add_challenge'))  



# ---------------------------------------------------------
# SUBMIT FLAG
# ---------------------------------------------------------
@app.route("/submit", methods=["POST"])
def submit():
    if "user_id" not in session:
        return redirect("/")

    challenge_id = int(request.form["challenge_id"])
    flag = request.form["flag"]
    user_id = session["user_id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Recupera la flag corretta dalla challenge
    cursor.execute("SELECT flag FROM challenges WHERE id=%s", (challenge_id,))
    challenge = cursor.fetchone()
    if not challenge:
        cursor.close()
        db.close()
        return "Challenge non trovata", 404

    # Verifica se la flag è corretta
    is_correct = (flag == challenge["flag"])

    # Inserisci la submission
    cursor.execute("""
        INSERT INTO submissions (user_id, challenge_id, submitted_flag, is_correct)
        VALUES (%s, %s, %s, %s)
    """, (user_id, challenge_id, flag, is_correct))
    db.commit()

    # Se la flag è corretta, aggiorna lo stato della challenge nel gruppo
    if is_correct:
        cursor.execute("""
            INSERT INTO challenge_completion (group_id, challenge_id, completed)
            VALUES (%s, %s, TRUE)
            ON DUPLICATE KEY UPDATE completed=TRUE
        """, (session["group_id"], challenge_id))  # Utilizza il group_id dell'utente
        db.commit()

    cursor.close()
    db.close()

    # Mostra il risultato della submission
    return render_template("result.html", result=is_correct, challenge_id=challenge_id)


# ---------------------------------------------------------
# PAGINE EXTRA CHALLENGES
# ---------------------------------------------------------
@app.route("/extra/<int:challenge_id>")
def extra(challenge_id):
    if "user_id" not in session:
        return redirect("/")

    challenge_pages = {
        7: "loginspw.html",
        8: "clash1.html",
        9: "clash1.html",
        10: "cookie.html"
    }

    template = challenge_pages.get(challenge_id)
    if not template:
        return "Challenge non trovata", 404

    return render_template(template)

@app.route('/login', methods=['POST'])
def login1():
    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "admin":
        return render_template('adminspw.html')
    else:
        # Rick Roll redirect
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    

CARDS = {
    "pekka": {
        "name": "P.E.K.K.A",
        "rarity": "epic",
        "image": "img/PEKKACard.webp",
        "description": "Una guerriera pesantemente corazzata con attacchi devastanti."
    },
    "wizard": {
        "name": "Stregone",
        "rarity": "rare",
        "image": "img/WizardCard.webp",
        "description": "Lancia potenti palle di fuoco a distanza."
    },
    "giant": {
        "name": "Gigante",
        "rarity": "rare",
        "image": "img/GiantCard.png",
        "description": "Tank enorme che mira solo agli edifici."
    },
    "baby-dragon": {
        "name": "Baby Dragon",
        "rarity": "epic",
        "image": "img/BabyDragonCard.webp",
        "description": "Sputa fuoco ad area devastando gruppi di nemici."
    },
    "hog-rider": {
        "name": "FLAG",
        "rarity": "rare",
        "image": "img/HogRiderCard.webp",
        "description": "LA FLAG NON é QUI"
    },
    "flag": {
        "name": "FLAG",
        "rarity": "rare",
        "image": "img/flag.webp",
        "description": "LA Flag è: SPWGRG{TR4V3RS3_TH3_P4TH}"
    }
}

@app.route("/extra/<card_id>")
def extra1(card_id):
    card = CARDS.get(card_id)
    if not card:
        return "Carta non trovata", 404
        
    return render_template("card.html", card=card)

@app.route("/extra/10")
def index():
    # Creiamo la risposta renderizzando la pagina
    resp = make_response(render_template(
        "cookie.html",
        challenge_name="GIORGI BISCUITS",
        challenge_subtitle="Trova la flag nascosta… se sei capace."
    ))

   
    resp.set_cookie(
        "SPWGRG",                   # nome del cookie
        "SPWGRG{1M_5O_D3L1C10U5}",  # valore della flag
        max_age=None,                # durata in secondi
        httponly=False,              # il cookie è accessibile da JavaScript se vuoi
        samesite='Lax'               # protezione CSRF minima
    )

    return resp



@app.route("/PlatformCred")
def PlatformCred():
    return render_template("PlatformCred.html")

@app.route("/contact")
def contact():
    return render_template("Contact.html")

@app.route("/about")
def about():
    return render_template("About.html")

if __name__ == "__main__":
    app.run(debug=True)
