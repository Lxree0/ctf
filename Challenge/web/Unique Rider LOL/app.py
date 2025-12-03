from flask import Flask, render_template

app = Flask(__name__)

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

@app.route("/card/<card_id>")
def card_page(card_id):
    card = CARDS.get(card_id)
    if not card:
        return "Carta non trovata", 404
        
    return render_template("card.html", card=card)


@app.route("/")
def hello_world():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)