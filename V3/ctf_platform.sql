-- Selezione del database
USE ctfdashboard;

-- Eliminazione tabelle nell’ordine corretto
DROP TABLE IF EXISTS challenge_completion;
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS challenges;
DROP TABLE IF EXISTS users;

-- Tabella utenti con punteggio individuale
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT NULL,
    score INT DEFAULT 0,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL
);
-- Tabella challenge invariata
CREATE TABLE challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    flag VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    points INT NOT NULL default 500,
    hint1 VARCHAR(255),
    hint2 VARCHAR(255),
    attached_file VARCHAR(255),
    attached_file2 VARCHAR(255),
    attached_file3 VARCHAR(255)
);

-- Tabella submissions (storico tentativi)
CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    challenge_id INT NOT NULL,
    submitted_flag VARCHAR(255) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
);

-- Tabella challenge completate dall’utente
CREATE TABLE challenge_completion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    challenge_id INT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, challenge_id),         -- un utente non può completare due volte la stessa challenge
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
);



INSERT INTO users (username, is_admin) VALUES 
('admin.LG.07#', TRUE);

INSERT INTO challenges (title, description, flag, category, hint1, hint2, attached_file, attached_file2, attached_file3) VALUES 
('Codice Morse', 'Un radioamatore ha trasmesso un messaggio di emergenza.Decifra l\'intera sequenza per svelare la parola chiave e la sua frequenza di trasmissione segreta.La flag deve essere nel seguente formato: SPWGRG{flag}', 'SPWGRG{M0rs3_C0D3}', 'Cripto', 'Hai mai usato un telegrafo elettrico?', 'Conosci il codice morse?', '1.txt', NULL, NULL),

('Cifrario di Cesare', 'Hai intercettato un messaggio criptato da un\'antica legione! Il messaggio sembra essere composto da lettere apparentemente prive di senso. A quanto pare la data del messaggio risale al periodo in cui Roma era governata da Cesare. La flag deve essere nel seguente formato: SPWGRG{flag}', 'SPWGRG{C3s4r_Sh1ft}', 'Cripto', 'Chissà qual è la chiave di spostamento…forse indietro.', 'Esisterà qualche cifrario da utilizzare?', '2.txt', NULL, NULL),

('Codice Braille', 'Hai trovato una tavoletta con dei rilievi misteriosi. Decifra la sequenza, che nasconde la parola chiave e il numero seriale del puzzle. La flag deve essere nel seguente formato: SPWGRG{flag}', 'SPWGRG{Y0u_C4nt_S33_M3}', 'Cripto', 'Non tutto si vede con gli occhi!', 'Se fosse stampata anche un CIECO potrebbe leggere questa flag!', '3.txt', NULL, NULL),

('Enchantment Gliphs', 'Sei di fronte a un\'antica incudine con un testo misterioso inciso. Traduci i simboli nel nostro alfabeto per scoprire la flag nascosta e completare l\'incantesimo.', 'SPWGRG{4LW4YSPUTM3ND1NG}', 'Cripto', 'Hai mai giocato a Minecraft?', NULL, '4.png', NULL, NULL),

('The Metadata Hunter', 'Un blocco segreto di Minecraft nasconde la chiave per la flag!La flag deve essere nel seguente formato: SPWGRG{gps_position}', 'SPWGRG{40 deg 38\' 42.87" N, 17 deg 56\' 8.90" E}', 'Misc', 'Esisterà un sito online per “ispezionare” le immagini?', 'Il titolo dice niente?', '5.png', NULL, NULL),

('Hog Rider Hunt', 'Hai visto questa immagine in un forum di Clash Royale. Devi usare le tue abilità di ricerca per trovare i dettagli esatti della carta Domatore di Cinghiali. Il codice segreto è composto dal costo in Elisir della carta e l\'anno in cui è stata rilasciata nel gioco.', 'SPWGRG{H0G_RIDER_4_2016}', 'Misc', 'La foto potrebbe dire qualcosa?', 'La steganografia potrebbe centrare qualcosa?', '6.png', NULL, NULL),

('NEVER CHANGE THE PASSWORD', 'Oh no! Hai dimenticato la password del wifi della scuola ma non vuoi che nessuno lo sappia. Prova ad accedere al portale per scoprirla!', 'SPWGRG{4LW415_CH4NGE_,M3!!}', 'Web', 'Dovrei chiamare l\'admin…', 'L\'admin dovrebbe cambiare la password, è troppo scontata…', 'https://neverchangeme.giorgictf.it/', NULL, NULL),

('DEEP SEARCH', 'Un enigma nascosto dietro le quinte: solo chi osserva con attenzione riesce a svelare ciò che non appare subito.', 'SPWGRG{H0G_R1D3R}', 'Web', 'Hai mai esaminato o ispezionato una pagina web?', 'F12', 'https://deepsearch.giorgictf.it/', NULL, NULL),

('UNIQUE RIDERS LOL', 'Un percorso segreto attende chi ha il coraggio di esplorare oltre l\'indirizzo visibile.', 'SPWGRG{TR4V3RS3_TH3_P4TH}', 'Web', 'UNIQUE RIDERS LOL: URL', 'Vorrei tanto aprire la carta più importante: la flag', 'https://uniqueriderlol.giorgictf.it/', NULL, NULL),

('GIORGI BISCUITS', 'Dolci e croccanti, nascondono un piccolo segreto che si rivela solo a ai piu\' golosi.', 'SPWGRG{1M_5O_D3L1C10U5}', 'Web', 'Buoni questi cookies.', 'F12 -> APPLICATION', 'https://giorgibiscuits.giorgictf.it/', NULL, NULL);
