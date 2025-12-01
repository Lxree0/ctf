-- Selezione del database
USE ctfdashboard;

-- Eliminazione tabelle se esistono (ordine corretto)
DROP TABLE IF EXISTS challenge_completion;
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS challenges;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS ctf_groups;


-- Ricreazione delle tabelle
CREATE TABLE ctf_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    group_id INT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES ctf_groups(id)
);

CREATE TABLE challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    flag VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL
);

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

CREATE TABLE challenge_completion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    challenge_id INT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (group_id) REFERENCES ctf_groups(id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
);

-- Dati iniziali
INSERT INTO ctf_groups (group_name) VALUES
('admin'), 
('TeamA'),
('TeamB'), 
('TeamC'),
('TeamD');


INSERT INTO users (username, group_id) VALUES 
('admin.LG.07#', 1);

INSERT INTO challenges (title, description, flag, category) VALUES 
('Codice Morse', 'In questa CTF, dovrai decifrare un messaggio segreto in codice morse per risolvere la "Flag". Scopri come il codice morse può svelare i segreti nascosti e diventare un esperto di comunicazioni segrete!', 'SPWGRG{M0rs3_C0D3}', 'Cripto'),
('Cifrario di Cesare', 'Nel Cifrario di Cesare, ogni lettera di un messaggio viene spostata di un certo numero di posizioni nell\'alfabeto. Trova la chiave di spostamento!', 'SPWGRG{C3s4r_Sh1ft}', 'Cripto'),
('Codice Braille', 'Hai trovato una tavoletta con dei rilievi misteriosi. Questi simboli sono scritti in Codice Braille! Decifra la sequenza, che nasconde la parola chiave e il numero seriale del puzzle', 'SPWGRG{Y0u_C4nt_S33_M3}', 'Cripto'),
('Enchantment Gliphs', 'Sei di fronte a un\'antica incudine con un testo misterioso inciso. Questi sono i glifi degli incantesimi di Minecraft! Traduci i simboli nel nostro alfabeto per scoprire la flag nascosta e completare l\'incantesimo.', 'SPWGRG{4LW4YSPUTM3ND1NG}', 'Cripto'),
('Phantom', 'Un blocco segreto di Minecraft nasconde la chiave per la flag! Devi usare le tue abilità di ricerca (OSINT) per identificare questo blocco e trovare due valori cruciali: il suo ID numerico (della versione Java Edition) e l\'anno in cui è stato introdotto nel gioco.', 'SPWGRG{PHANTOM_ID529_2018}', 'Misc'),
('Hog Rider Hunt', 'Hai visto questa immagine in un forum di Clash Royale. Devi usare le tue abilità di ricerca per trovare i dettagli esatti della carta Domatore di Cinghiali. Il codice segreto è composto dal costo in Elisir della carta e l\'anno in cui è stata rilasciata nel gioco.', 'SPWGRG{H0G_RIDER_4_2016}', 'Misc'),
('NEVER CHANGE THE PASSWORD', 'Oh no! Hai dimenticato la password del wifi della scuola ma non vuoi che nessuno lo sappia. Prova ad accedere al portale per scoprirla!', 'SPWGRG{4LW415_CH4NGE_,M3!!}', 'Web'),
('DEEP SEARCH', 'Un enigma nascosto dietro le quinte: solo chi osserva con attenzione riesce a svelare ciò che non appare subito.', 'SPWGRG{H0G_R1D3R}', 'Web'),
('UNIQUE RIDERS LOL', 'Un percorso segreto attende chi ha il coraggio di esplorare oltre l\indirizzo visibile.', 'SPWGRG{TR4V3RS3_TH3_P4TH}', 'Web'),
('GIORGI BISCUITS', 'Dolci e croccanti, nascondono un piccolo segreto che si rivela solo a chi guarda più a fondo.', 'SPWGRG{1M_5O_D3L1C10U5}', 'Web')
