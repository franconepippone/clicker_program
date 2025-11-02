# Clicker Program Language — Riferimento Comandi (Compatto)

Questo è la documentazione compatta per tutti i comandi del linguaggio di programmazione integrato nell'applicazione.  
I parametri per i comandi sono separati da spazi. I parametri opzionali sono mostrati tra parentesi graffe `{}` solo in questo documento; nel linguaggio effettivo le parentesi *non* vanno scritte.

Usa `;` per scrivere commenti; il testo scritto dopo questo simbolo verrà ignorato.  
Esempio: `wait 1 ; attende per 1 secondo`

---

### Comandi di Movimento

- **move** `<x> <y> {<t>}`  
  Muove il mouse alle coordinate assolute `(x, y)`. Il parametro opzionale `{t}` rappresenta la durata in secondi.  
  Esempio: `move 100 50 0.5`

- **moverel** `<dx> <dy> {<t>}`  
  Muove il mouse in modo relativo alla posizione corrente `(dx, dy)`. Il parametro opzionale `{t}` indica la durata.  
  Esempio: `moverel 50 0 0.2`

---

### Comandi di Click

- **click** `{button}`  
  Esegue un click del mouse nella posizione corrente. `{button}` può essere `left` o `right`.  
  Se `button` non viene fornito , il click sarà con il tasto sinistro per default.  
  Esempio: `click`, `click right`, `click left`

- **doubleclick**  
  Esegue un doppio clic nella posizione corrente.  
  Esempio: `doubleclick`

---

### Comandi di Attesa

- **wait** `<t>`  
  Attende `t` secondi.  
  Esempio: `wait 4.5    ;attende per 4.5 secondi`

- **pause**  
  Mette in pausa l'esecuzione del programma. 

---

### Comandi di Ciclo e Salto

- **label** `<name>`  
  Definisce un’etichetta a cui saltare.  
  Esempio: `label inizio_ciclo`

- **jump** `<label> {<n>}`  
  Salta all’etichetta specificata. Se `{n}` è fornito, il salto verrà eseguito fino a `{n}` volte;  
  una volta raggiunto l'n-esimo salto, il salto fallirà e il programma continuerà con l’istruzione successiva.  
  Dopo di ciò, il salto potrà essere utilizzato di nuovo, permettendo a loop e cicli annidati di ripetersi più volte.  
  Esempio: `jump inizio_ciclo`, `jump inizio_ciclo 20`

- **call** `<label>`  
Simile a **jump**, salta in maniera incondizionata verso l'etichetta fornita. Internamente, questo comando mantiene un riferimento all'ultima istuzione eseguita prima del salto, e insieme a **return** può essere utilizzato per simulare il meccanismo di chiamate a funzioni.

- **return**  
Può essere chiamato dopo un comando **call** per tornare al punto del programma in cui l'esecuzione si era bloccata prima di effettuare il salto.  
 **N.B.:** per il corretto funzionamento dei comandi **call**/**return**, è fondamentale che **call** salti solo ad etichette che implementano blocchi di codice terminanti in un **return**. In un programma dovrebbero esserci sempre un numero di comandi **call** uguale al numero di comandi **return**. Guarda il file in *example_programs/functions.txt* per degli esempi sul funzionamento. 

---

### Console / Output

- **print** `<message...>`  
  Stampa un messaggio nella console.  
  Esempio: `print Hello world!`

---

### Utilità del Mouse

- **centermouse**  
  Muove il mouse al centro dello schermo.  
  Esempio: `centermouse`

- **goback**  
  Torna indietro di un passo nella cronologia delle posizioni del mouse,  
  annullando l’ultimo spostamento creato da un comando `move`.  
  Esempio: `goback`
