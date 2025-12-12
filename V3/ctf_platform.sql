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
('Codice Morse', 'In questa CTF, dovrai decifrare un messaggio segreto in codice morse per risolvere la "Flag". Scopri come il codice morse può svelare i segreti nascosti e diventare un esperto di comunicazioni segrete!', 'SPWGRG{M0rs3_C0D3}', 'Cripto', 'ciao', NULL, '1.txt', NULL, NULL),

('Cifrario di Cesare', 'Nel Cifrario di Cesare, ogni lettera di un messaggio viene spostata di un certo numero di posizioni nell\'alfabeto. Trova la chiave di spostamento!', 'SPWGRG{C3s4r_Sh1ft}', 'Cripto', NULL, NULL, '2.txt', NULL, NULL),

('Codice Braille', 'Hai trovato una tavoletta con dei rilievi misteriosi. Questi simboli sono scritti in Codice Braille! Decifra la sequenza, che nasconde la parola chiave e il numero seriale del puzzle', 'SPWGRG{Y0u_C4nt_S33_M3}', 'Cripto', NULL, NULL, '3.txt', NULL, NULL),

('Enchantment Gliphs', 'Sei di fronte a un\'antica incudine con un testo misterioso inciso. Questi sono i glifi degli incantesimi di Minecraft! Traduci i simboli nel nostro alfabeto per scoprire la flag nascosta e completare l\'incantesimo.', 'SPWGRG{4LW4YSPUTM3ND1NG}', 'Cripto', NULL, NULL, '4.png', NULL, NULL),

('Phantom', 'Un blocco segreto di Minecraft nasconde la chiave per la flag! Devi usare le tue abilità di ricerca (OSINT) per identificare questo blocco e trovare due valori cruciali: il suo ID numerico (della versione Java Edition) e l\'anno in cui è stato introdotto nel gioco.', 'SPWGRG{PHANTOM_ID529_2018}', 'Misc', NULL, NULL, '5.png', NULL, NULL),

('Hog Rider Hunt', 'Hai visto questa immagine in un forum di Clash Royale. Devi usare le tue abilità di ricerca per trovare i dettagli esatti della carta Domatore di Cinghiali. Il codice segreto è composto dal costo in Elisir della carta e l\'anno in cui è stata rilasciata nel gioco.', 'SPWGRG{H0G_RIDER_4_2016}', 'Misc', NULL, NULL, '6.png', NULL, NULL),

('NEVER CHANGE THE PASSWORD', 'Oh no! Hai dimenticato la password del wifi della scuola ma non vuoi che nessuno lo sappia. Prova ad accedere al portale per scoprirla!', 'SPWGRG{4LW415_CH4NGE_,M3!!}', 'Web', NULL, NULL, 'https://neverchangeme.giorgictf.it/', NULL, NULL),

('DEEP SEARCH', 'Un enigma nascosto dietro le quinte: solo chi osserva con attenzione riesce a svelare ciò che non appare subito.', 'SPWGRG{H0G_R1D3R}', 'Web', NULL, NULL, 'https://deepsearch.giorgictf.it/', NULL, NULL),

('UNIQUE RIDERS LOL', 'Un percorso segreto attende chi ha il coraggio di esplorare oltre l\'indirizzo visibile.', 'SPWGRG{TR4V3RS3_TH3_P4TH}', 'Web', NULL, NULL, 'https://uniqueriderlol.giorgictf.it/', NULL, NULL),

('GIORGI BISCUITS', 'Dolci e croccanti, nascondono un piccolo segreto che si rivela solo a chi guarda più a fondo.', 'SPWGRG{1M_5O_D3L1C10U5}', 'Web', NULL, NULL, 'https://giorgibiscuits.giorgictf.it/', NULL, NULL);
