# Architettura

In questa sezione è illustrato tutto quanto riguardi l'architettura del progetto.

## A grandi linee

La funzionalità principale di `downtime-panda` è il monitoraggio dei servizi registrati nel database tramite delle richieste periodiche allo stesso.

L'implementazione di tale funzionalità è fatta grazie al pacchetto [APScheduler](https://pypi.org/project/APScheduler/), assieme all'estensione [Flask-APScheduler](https://pypi.org/project/Flask-APScheduler/) e al pacchetto [requests](https://requests.readthedocs.io/en/latest/) per le effettive richieste al servizio.

### Monitoraggio di un servizio

Quando un utente decide di monitorare un servizio, questo inserisce il **nome** e l'**uri** del servizio che vuole monitorare. All'invio dei dati, downtime-panda fa una ricerca dell'uri fornito nel db per vedere se tale servizio è stato già registrato in passato.

Un esito negativo porta alla **registrazione dell'URI** del servizio nella tabella `Service` del database, assieme alla creazione di un nuovo job in background tramite **APScheduler**.
Questo job, ogni 5 secondi, manda una **richiesta HTTP HEAD** all'URI del relativo servizio e salva il risultato della richiesta nella tabella `Ping`.

Un esito positivo semplicemente prende il riferimento a quel servizio, saltando tutta la fase elencata sopra.

Avendo il servizio, il monitoraggio dello stesso da parte dell'utente viene registrato nella tabella `Subscriptions`. Oltre a contenere i riferimenti all'utente e al servizio, la tabella contiene anche la data di creazione del record, il nome dato dall'utente al servizio, ed un UUID generato per identificare l'iscrizione senza far riferimento all'ID del servizio stesso.

L'utente a quel punto è in grado di vedere lo stato del servizio accedendo alla rotta `/you/subscriptions/<uuid>`.

### API per il monitoraggio

Con una iscrizione attiva, l'utente è in grado di richiedere l'ultimo stato del servizio monitorato tramite l'API esposta alla rotta `/api/subscriptions/status`, fornendo un **subscription_uuid** come query parameter ed un **token** a suo nome nell'intestazione.

La rotta ritorna le seguenti risposte:

- **401 UNAUTHORIZED**: Non è stato fornito il token per l'autenticazione
- **404 NOT FOUND**: Non vi è nessuna iscrizione con quell'uuid per l'utente con quel token
- **200 OK**: Token e uuid sono corretti

Con i dati corretti, la rotta ritorna un file JSON contenente lo stato HTTP del servizio più il timestamp dell'ultima richiesta fatta allo stesso.

Ad esempio, una richiesta fatta con [curl](https://curl.se/) potrebbe essere fatta come segue...

``` sh
curl --request GET \
  --url 'http://localhost:8080/api/subscriptions/status?subscription_uuid=00000000-0000-0000-0000-000000000000' \
  --header 'authorization: Bearer abcdefghijklmnopqrstuvwxyz123456'
```

...ed una possibile risposta potrebbe essere questa

```json
{
  "http_response": 200,
  "response_time": 0.2,
  "pinged_at": "2025-06-14T16:21:38.856451"
}
```

#### Token e autenticazione con l'API

Come detto sopra, l'utente ha bisogno di un token per autenticarsi con l'API.

I token dell'utente autenticato vengono gestiti sulla rotta `/you/tokens`. Tramite gli appositi pulsanti, l'utente può registrare o revocare token a suo nome.

L'autenticazione con l'API è implementata tramite l'estensione [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/), in particolare usando **`TokenHTTPAuth`**. L'autenticazione implementata dall'estensione è di tipo **Bearer**: chiunque è in possesso del token è in grado di fare richieste all'API, senza dover fornire prova di essere il legittimo detentore della stringa.

Nel fare la richiesta GET all'API è necessario fornire il token nell'intestazione della richiesta. In particolare, va incluso nell'intestazione `Authorization`, nella forma `Bearer <token>`, come indicato sopra.

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
