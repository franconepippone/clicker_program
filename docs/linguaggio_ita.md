# Clicker Program Language — Riferimento Comandi

Questo documento riassume tutti i comandi del linguaggio di programmazione integrato nell’applicazione. La sintassi generale dei comandi è:  
 **`<comando>`**` <param1> <param2> ...`,  
 dove i parametri dei comandi sono separati da spazi. Su questo documento, i parametri **opzionali** sono indicati tra parentesi graffe `{}` — **non** vanno scritte nel codice.

I commenti si scrivono con `;`: tutto ciò che segue su quella riga verrà ignorato.  
Esempio:  
`wait 1 ; attende 1 secondo`

---

## 🖱️ Comandi di Movimento

- **move** `<x> <y> {<t>}`  
  Sposta il mouse alle coordinate assolute `(x, y)`.  
  Il parametro opzionale `{t}` indica la durata in secondi del movimento.  
  Esempio: `move 100 50 0.5`

- **moverel** `<dx> <dy> {<t>}`  
  Sposta il mouse relativamente alla posizione attuale `(dx, dy)`.  
  Il parametro opzionale `{t}` indica la durata in secondi del movimento.  
  Esempio: `moverel 50 0 0.2`

---

## 🖱️ Comandi di Click

- **click** `{button}`  
  Esegue un click nella posizione corrente.  
  `{button}` può essere `left` o `right`.  
  Se omesso, il click sarà con il tasto sinistro.  
  Esempi: `click`, `click right`, `click left`

- **doubleclick**  
  Esegue un doppio click nella posizione corrente.  
  Esempio: `doubleclick`

---

## ⏱️ Comandi di Attesa

- **wait** `<t>`  
  Attende per `t` secondi.  
  Esempio: `wait 4.5 ; attende 4.5 secondi`

- **pause**  
  Mette in pausa l’esecuzione del programma fino a ripresa manuale.

---

## 🔁 Comandi di Ciclo e Salto

- **label** `<name>`  
  Definisce un’etichetta a cui poter saltare.  
  Esempio: `label inizio_ciclo`

- **jump** `<label> {<n>}`  
  Salta all’etichetta specificata.  
  Se `{n}` è indicato, il salto verrà eseguito fino a `{n}` volte.  
  Dopo aver raggiunto l’n-esimo salto, l’esecuzione prosegue normalmente, ma il comando potrà essere usato di nuovo in seguito.  
  Esempi: `jump inizio_ciclo`, `jump inizio_ciclo 20`

- **call** `<label>`  
  Salta incondizionatamente all’etichetta indicata, ricordando il punto nel programma da cui è stato chiamato.  
  Insieme al comando **return**, permette di simulare chiamate di funzione.  
  Esempio: `call funzione_click`

- **return**  
  Restituisce il controllo al punto in cui era stato eseguito il corrispondente **call**; in altre parole, ritorna ad eseguire il programma dal punto in cui era stato effettuato il salto con un **call**.  
  **Nota:** per il corretto funzionamento, ogni **call** deve corrispondere a un **return**.  
  Consulta *example_programs/functions.txt* per esempi pratici.

---

## 💬 Console / Output

- **print** `<message...>`  
  Stampa un messaggio nella console.  
  Esempio: `print Hello world!`

---

## Utilità 

- **centermouse**  
  Sposta il cursore al centro dello schermo.  
  Esempio: `centermouse`

- **goback**  
  Torna indietro alla precedente posizione del mouse,  
  annullando l’ultimo movimento eseguito da un comando `move`. Può essere usata in successione per ripercorrere la storia di movimenti.  
  Esempio: `goback`
