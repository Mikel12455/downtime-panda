# Architettura

In questa sezione è illustrato tutto quanto riguardi l'architettura del progetto.

## Organizzazione del progetto

Il progetto è organizzato in una serie di cartelle e moduli con l'obiettivo di suddividerlo in modo "verticale", ovvero dividerlo per funzionalità.

Ogni pacchetto Python sotto la cartella Blueprints contiene, al suo interno, diversi moduli con tutto quello che serve per implementare la relativa funzionalità:

- **`templates`** e **`static`**: Rispettivamente, pagine template Jinja ed asset per costruire le pagine HTML della relativa rotta.
- **`routes.py`**: Rotte Flask della relativa funzionalità
- **`messages.py`**: Messaggi di feedback inviati all'utente per quando fa qualcosa (Ex. credenziali non valide durante il login).
- **`api.py`**: Rotte per servire l'API esposta dalla funzionalità.
- **`models.py`**: Modelli per interfacciarsi con il database.

## Schema E-R

Il database usato da Downtime Panda è riassunto nello schema seguente.

![Entity Relationship Diagram](assets/er_schema.drawio.svg)

!!! info "Colonna `ID`"
    Senza doverlo ripetere in ogni entità, la colonna `ID` di ognuna delle entità è un **intero a 8 byte autogenerato**.

    La scelta di usare un intero a 8 byte sta nella tabella `Ping`, che nel tempo si riempirà di numerosi ping dai più disparati servizi.

    Si poteva probabilmente evitare per le altre entità.

### User

Rappresenta un utente registrato, completo di *username*, *email*, e *hash della password*.

L'hash della password è calcolato tramite Argon2id

### API Token

Rappresenta un token generato dall'utente per accedere alla propria API.

Il singolo Token è una stringa esadecimale casuale generata direttamente dal backend. La stringa è lunga 16 caratteri esadecimali, che equivalgono ad un token da 32 byte.

### Service

Rappresenta un servizio monitorato da Downtime Panda.

Vengono generati automaticamente alla prima iscrizione di un utente al servizio. Dalla seconda iscrizione in poi viene riusato lo stesso servizio.

### Ping

Rappresenta il singolo ping/heartbeat mandato al servizio.

In breve, salva la risposta HTTP ricevuta in un certo istante nel tempo.

### Subscription

Rappresenta l'iscrizione di un utente ad un servizio
