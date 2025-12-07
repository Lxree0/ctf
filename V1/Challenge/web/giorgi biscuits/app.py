from flask import Flask, render_template, make_response

app = Flask(__name__)

@app.route("/")
def index():
    # Creiamo la risposta renderizzando la pagina
    resp = make_response(render_template(
        "index.html",
        challenge_name="GIORGI BISCUITS",
        challenge_subtitle="Trova la flag nascosta… se sei capace."
    ))

    # Impostiamo il cookie con la flag
    # Durata 1 ora (3600 secondi)
    resp.set_cookie(
        "SPWGRG",                   # nome del cookie
        "SPWGRG{1M_5O_D3L1C10U5}",  # valore della flag
        max_age=None,                # durata in secondi
        httponly=False,              # il cookie è accessibile da JavaScript se vuoi
        samesite='Lax'               # protezione CSRF minima
    )

    return resp

if __name__ == "__main__":
    app.run(debug=True)
