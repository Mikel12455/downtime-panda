# Architettura

In questa sezione è illustrato tutto quanto riguardi l'architettura ed il funzionamento del progetto.

## Organizzazione del sorgente

Il progetto è organizzato in una serie di cartelle e moduli con l'obiettivo di suddividerlo in modo "verticale", ovvero dividerlo per funzionalità.

### Moduli principali

I moduli non contenuti in `blueprints` fanno principalmente da configurazione dell'applicazione Flask.

- `__init__.py`: Contiene la funzione `create_app`, che fa da "application factory" per Flask.
- `extensions.py`: Inizializza tutte le estensioni Flask usate per tutta l'applicazione
- `config.py`: Contiene le classi per configurare l'applicazione a partire dai valori nelle variabili d'ambiente.

### Blueprint

Ogni pacchetto Python sotto la cartella `blueprints` contiene, al suo interno, diversi moduli con tutto quello che serve per implementare la relativa funzionalità:

- **`routes.py`**: Rotte Flask della relativa funzionalità
- **`messages.py`**: Messaggi di feedback inviati all'utente per quando fa qualcosa (Ex. credenziali non valide durante il login).
- **`forms.py`**: Tutti i form utili al modulo, implementati tramite [Flask-WTF](https://flask-wtf.readthedocs.io/en/latest/).
- **`api.py`**: Rotte per servire l'API esposta dalla funzionalità.
- **`models.py`**: Modelli per interfacciarsi con il database.

I template Jinja di ogni blueprint è incluso nella cartella `templates`. La struttura delle cartelle è la stessa seguita in `blueprints`.

## Schema E-R

Il database usato da Downtime Panda è riassunto nello schema seguente.

![Entity Relationship Diagram](assets/er_schema.drawio.svg)

!!! info "Sulla colonna `ID` ..."
    Senza doverlo ripetere in ogni entità, la colonna `ID` di ognuna delle entità è un **intero a 8 byte autogenerato**.

    La scelta di usare un intero a 8 byte sta nella tabella `Ping`, che nel tempo si riempirà di numerosi ping dai più disparati servizi; questo porterà inevitabilmente a superare il massimo numero di valori possibili per un tipico intero a 4 byte (circa **~4.000.000.000**, dimezzati se non si vogliono usare i valori negativi).

    Si poteva probabilmente evitare per le altre entità ma, non essendoci alcuna ragione particolare per non farlo, si è deciso di usare comunque interi a 8 byte.

!!! warning "In ambiente di sviluppo"
    SQLite non lavora bene con chiavi primarie come interi a 8 byte autoincrementanti. Pertanto, nell'**ambiente di sviluppo**, tutti gli ID sono effettivamente **interi a 4 byte**.

### User

Rappresenta un utente registrato, completo di *username*, *email*, e *hash della password*.

#### Campi

- username: string(255), unique
- email: string(255), unique
- password_hash: string(255)

#### Note

L'hash della password è calcolato tramite Argon2id

### API Token

Rappresenta un token generato dall'utente per accedere alla propria API.

Il singolo Token è una stringa esadecimale casuale generata direttamente dal backend. La stringa è lunga 32 caratteri esadecimali, che equivalgono ad un token da 16 byte.

### Service

Rappresenta un servizio monitorato da Downtime Panda.

Vengono generati automaticamente alla prima iscrizione di un utente al servizio. Dalla seconda iscrizione in poi viene riusato lo stesso servizio.

### Ping

Rappresenta il singolo ping/heartbeat mandato al servizio.

In breve, salva la risposta HTTP ricevuta in un certo istante nel tempo.

### Subscription

Rappresenta l'iscrizione di un utente ad un servizio
