# Clicker Program Language — Riferimento Comandi

Questo documento riassume tutti i comandi del linguaggio di programmazione integrato nell’applicazione. La sintassi generale dei comandi è:  
 **`<comando>`**` <param1> <param2> ...`,  
 dove i parametri dei comandi sono separati da spazi. Su questo documento, i parametri **opzionali** sono indicati tra parentesi graffe `{}` — **non** vanno scritte nel codice.

I commenti si scrivono con `;`, tutto ciò che segue su quella riga verrà ignorato.  
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
  Esempio: `moverel 50 0 1.5`

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
  Dopo aver raggiunto l’n-esimo salto, il prossimo salto fallirà e l'esecuzione passerà oltre; tuttavia, qualora la stessa istruzione di salto dovesse essere rieseguita (ad esempio tramite configurazione di cicli annidati), il salto verrà resettato e si comporterà come se fosse stato appena incontrato, nella modalità descritta in precedenza (**n** salti).  
  Esempi: `jump inizio_ciclo`, `jump inizio_ciclo 20`

- **call** `<label>`  
  Salta incondizionatamente all’etichetta indicata, ricordando il punto nel programma da cui è stato chiamato.  
  Insieme al comando **return**, permette di simulare chiamate a funzioni.  
  Esempio: `call funzione_click`

- **return**  
  Restituisce il controllo al punto del programma in cui era stato eseguito il corrispondente **call**; in altre parole, ritorna ad eseguire il programma dal punto subito dopo in cui era stato effettuato il salto con un **call**.  
  **Nota:** per il corretto funzionamento, ogni **call** deve corrispondere a un **return**.  
  Consulta *example_programs/functions.txt* per esempi pratici.

---

##  🧮 Variabili
Tutte le funzionalità inerenti alle variabili sono unificate nel comando **var** :

- **var** `<nome> = <valore>`   
  Assegna `<valore>` alla variabile `<nome>`. `<valore>` può essere un valore "letterale" (es.: `10`, `2.5`) oppure un riferimento ad un'altra variabile (es.: `x`, `la_mia_variabile`).  
  Esempio: `var x = 1`, `var x = y`

- **var** `<nome> = <valore> <OPERAZIONE> <valore>`   
  Esegue un operazione matematica fra i due valori inseriti (come nel caso precedente, possono essere sia "letterali" sia riferimenti a altre variabili). Le operazioni possibili sono `+`, `-`, `*`, `/`.
  Esempio: `var x = x + 1`, `var x = y * z`

La maggior parte dei comandi che accettano dei numeri come parametri (es.: `move`, `moverel`, `jump`, `wait`) supportano il passaggio di variabili. Esempi:
- `move x y`  
- `wait PAUSE_SECS`
- `moverel 50 incremento_y`  
dove **x**, **y**, **PAUSE_SECS**, **incremento_y** sono tutte variabili definite in una porzione precedente del codice.  

Esistono delle variabili globali speciali di sola lettura, che possono essere copiate in altre variabili o utilizzate in comandi. Sono prefissate dal carattere `$`:
- `$MOUSE_X` coordinata x del mouse
- `$MOUSE_Y` coordinata y del mouse
- `$OFFSET_X` offset applicato sulla coordinata x (generato con **setoffset**)
- `$OFFSET_Y` offset applicato sulla coordinata y



Consulta *example_programs/variables.txt* per esempi di codice.

---

## 💬 Console / Output

- **print** `<message...>`  
  Stampa un messaggio nel terminale.  
  Esempio: `print Hello world!`

- **printvar** `<nome>`  
  Stampa il valore della variabile inserita nel terminale.  
  Esempio: `printvar x` > **Terminal: x = 3.0**

---

## 🧰 Utilità 

- **centermouse**  
  Sposta il cursore al centro dello schermo.  
  Esempio: `centermouse`

- **goback**  
  Torna indietro alla precedente posizione del mouse,  
  annullando l’ultimo movimento eseguito da un comando `move`. Può essere usata in successione per ripercorrere la storia di movimenti.  
  Esempio: `goback`
