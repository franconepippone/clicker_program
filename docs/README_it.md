# Clicker Program

Un software (auto-clicker / strumento di automazione dei click) per automatizzare le operazioni svolte con il cursore del mouse, controllato interamente tramite un’interfaccia grafica (GUI).

---

## Panoramica

Il software include un linguaggio di scripting personalizzato, leggero e progettato appositamente per l’automazione del mouse.  
Questo linguaggio consente di scrivere script semplici e leggibili che possono controllare i movimenti del cursore, eseguire click del mouse, definire e manipolare variabili ed eseguire logiche cicliche utilizzando comandi ispirati ad assembly come `jump`, `call` e `return`.

Dall’interfaccia grafica sono disponibili due operazioni principali:

- **Run (Esegui)** — Esegue lo script corrente.  
  - Include una modalità **Safe Mode**, che disabilita i click del mouse, consentendo solo la simulazione dei movimenti del cursore.
- **Record (Registra)** — Registra una sequenza di azioni del mouse e inserisce automaticamente i comandi corrispondenti nell’editor.  
  - Premendo il **pulsante centrale del mouse** (rotellina) viene registrato solo un comando di movimento, senza click.

Per un elenco completo e dettagliato dei comandi del linguaggio di scripting, consultare la [Command Reference](linguaggio_it.md).

---

## Installazione

**Prerequisiti:**  
 - Python **3.8+**  
 - **pip** (gestore pacchetti Python)

### 1. Clonare il repository

Usando **git** (scrivi i seguenti comandi nel terminale):

    git clone https://github.com/franconepippone/clicker_program.git
    cd clicker_program

Oppure scarica l’archivio ZIP da GitHub ed estrailo manualmente.

---

### 2. Installare le dipendenze

Questo progetto è stato sviluppato utilizzando il gestore di pacchetti **uv** per Python.

#### Opzione A: Utilizzare `uv` (consigliato)

Installa `uv` globalmente:

    pip install uv

Poi, nella cartella del progetto:

    uv sync

#### Opzione B: Utilizzare `pip`

Se preferisci installare manualmente le dipendenze:

    pip install -r requirements.txt

> Nota: utilizzando `pip`, l’ambiente virtuale Python non verrà creato o gestito automaticamente.

---

### 3. Avviare l’applicazione

Nella cartella del progetto:

    uv run src/main.py

Se sei su Windows, puoi anche fare doppio click sul file `run_win.vbs` per avviare l’applicazione.  
(È possibile creare un collegamento per un accesso più rapido.)

---

## Informazioni aggiuntive

- Questo software è destinato all’**uso personale**.  
  L’utilizzo in contesti professionali o critici è a tuo rischio.
- La parte del codice relativa alla GUI è stata sviluppata con un ampio supporto di strumenti di intelligenza artificiale generativa (GPT) e potrebbe non aderire alle convenzioni standard di programmazione / Python o alle buone pratiche di scrittura di codice.

---
