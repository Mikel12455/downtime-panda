# Principali Caratteristiche dell'Applicazione

In questa sezione sono elencate le principali caratteristiche dell'applicazione, che siano correlate alla sicurezza o meno.

## Generale

### Ping di servizi

Il principale servizio offerto dall'applicazione è il monitoraggio dello stato di risorse o servizi in rete: l'utente chiede all'applicazione, ad esempio, di monitorare lo stato di un sito web, e questa farà, in background, richieste periodiche al sito web per verificarne lo stato.

Questa feature è implementata tramite il pacchetto [APScheduler](https://apscheduler.readthedocs.io/en/latest/), gestito dall'estensione [Flask-APScheduler](https://viniciuschiele.github.io/flask-apscheduler/).

### Versionamento delle Migrazioni del DB

Lo schema dell'intero DB è versionato grazie all'uso di [Alembic](https://alembic.sqlalchemy.org/en/latest/), gestito tramite l'estensione [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/index.html).

La cartella `migrations/versions` versiona ogni modifica fatta allo schema del DB, in modo da poter ricreare lo stesso db ovunque.

### Ambiente di test, sviluppo e staging

Questo progetto offre tre ambienti diversi:

- **Test**: E' l'ambiente usato da `pytest` per far girare gli unit test. Fa uso di un database SQLite in memoria, unico per ogni singolo test.
- **Sviluppo**: E' l'ambiente per sviluppare. L'applicazione *gira localmente* su `localhost:8080`, è abilitata al *DEBUG* e all'*autorefresh* dopo ogni modifica, e fa uso di un *database `SQLite`* creato automaticamente in `src/instance/dtpanda.db`. Il file del database è ignorato da `git`.
- **Staging**: E' un ambiente che cerca di copiare un ambiente di produzione. Monta su non solo l'applicazione, ma anche un database Postgres e un Reverse Proxy con Caddy. Funziona grazie a `docker compose`

Per quanto non sia direttamente una feature di sicurezza, avere questi tre ambienti ha comunque un effetto indiretto sulla stessa:

- L'ambiente di test permette di verificare automaticamente il **corretto funzionamento** dell'applicazione, individuando eventuali **regressioni e bug** scaturiti dall'aggiunta di nuove feature.
- L'ambiente di sviluppo cerca di essere quanto meno oneroso nell'utilizzo da parte dello sviluppatore. Con i log di Debug abilitati e il refresh della pagina automatico dopo ogni nuova feature, si cerca di rendere lo sviluppo quanto più rapido possibile.
- L'ambiente di staging offre un modo di testare l'applicazione in un ambiente simile a quello di produzione. L'idea è così catturare problemi che non sarebbe possibile verificare durante il solo sviluppo (ad esempio, scaturiti dall'uso di un Reverse Proxy tra l'utente e l'applicazione)


### Test tramite PyTest

Per verificare il funzionamento dell'applicazione durante il suo sviluppo è stato utilizzato `pytest`. Tramite questa libreria, è possibile implementare degli unit-test per la nostra applicazione come delle semplici funzioni.

Come già detto nella sezione precedente, mettere su dei test automatici permette di catturare rapidamente bug e regressioni durante lo sviluppo.

### Pre-Commit, Task e MkDocs

Più dei "nice-to-have" che delle vere e proprie funzionalità dell'applicazione, hanno comunque la loro utilità:

- **Pre-commit** configura automaticamente dei git hooks, script eseguiti automaticamente all'atto di una commit. Utilissimi per formattare automaticamente il codice o anche controllare se vengono incluse informazioni sensibili tra i file di una commit.
- **Task** permette di dare un nome ad una serie di comandi usati di frequente, tramite la definizione di un `Taskfile`.
- **MkDocs** alimenta la documentazione che stai leggendo in questo momento ;).


## Sicurezza

### Gestione dell'utente

Sul database, l'utente è un record della tabella `User` che salva uno username, una email, e l'hash della sua password per effettuare il login. Questo è stato già delineato nella sezione [Architettura](./2-architecture.md).

All'interno dell'applicazione Flask, l'utente è gestito tramite l'estensione [`Flask-Login`](https://flask-login.readthedocs.io/en/latest/). L'estensione implementa la gestione dei cookie di sessione dell'utente, senza però imporre l'suo di un certo modello o rappresentazione per lo stesso.

#### Registrazione

La registrazione dell'utente avviene compilando un semplice form, composto da username, email, password ed una conferma password.

La verifica del form è lasciata a Flask-WTF, il quale fa sia semplici controlli (quali rendere i campi obbligatori o controllare la lunghezza della password) che controlli più legati alla logica dell'applicazione (controllare che username ed email non siano già stati usati da altri utenti).

Nella registrazione, dalla password dell'utente viene ricavato il digest tramite l'algoritmo Argon2id, implementato tramite la libreria [argon2-cffi](https://argon2-cffi.readthedocs.io/en/stable/).

Se la registrazione va a buon fine, l'applicazione effettua automaticamente il login come "cortesia" all'utente.

#### Login e Logout

Come già detto, l'autenticazione è fornita da Flask-Login. L'implementazione è relativamente semplice: Flask-Login si occupa di salvare l'id dell'utente in un cookie di sessione all'atto del login, mentre l'unica cosa che va fatta dal nostro lato è specificare come recuperare un utente dato l'id dal cookie.

```py title="blueprints/user/routes.py"
from downtime_panda.extensions import login_manager

from .models import User

...

@login_manager.user_loader
def user_loader(id: str):
    id = int(id)
    return User.get_by_id(id)
```

Flask-Login si appoggia alle [sessioni di Flask](https://flask.palletsprojects.com/en/stable/quickstart/#sessions). La sessione è crittograficamente firmata tramite la FLASK_SECRET_KEY, che nel nostro caso è impostata tramite variabili d'ambiente (vedi di più nella sezione [Configurazione Sicura](#configurazione-sicura))

### Monitoraggio dei servizi ed accesso all'API tramite Token

Quando un utente decide di monitorare un servizio, questo inserisce il **nome** e l'**uri** del servizio che vuole monitorare. All'invio dei dati, downtime-panda fa una ricerca dell'uri fornito nel db per vedere se tale servizio è stato già registrato in passato.

Un esito negativo porta alla **registrazione dell'URI** del servizio nella tabella `Service` del database, assieme alla creazione di un nuovo job in background tramite **APScheduler**.
Questo job, ogni 5 secondi, manda una **richiesta HTTP HEAD** all'URI del relativo servizio e salva il risultato della richiesta nella tabella `Ping`.

Un esito positivo semplicemente prende il riferimento a quel servizio, saltando tutta la fase elencata sopra.

Avendo il servizio, il monitoraggio dello stesso da parte dell'utente viene registrato nella tabella `Subscriptions`. Oltre a contenere i riferimenti all'utente e al servizio, la tabella contiene anche la data di creazione del record, il nome dato dall'utente al servizio, ed un UUID generato per identificare l'iscrizione senza far riferimento all'ID del servizio stesso.

L'utente a quel punto è in grado di vedere lo stato del servizio accedendo alla rotta `/you/subscriptions/<uuid>`.

#### API per il monitoraggio

Con una iscrizione attiva, l'utente è in grado di richiedere l'ultimo stato del servizio monitorato tramite l'API esposta alla rotta `/api/subscriptions/status`, fornendo un **subscription_uuid** come query parameter ed un **token** a suo nome nell'intestazione.

La rotta ritorna le seguenti risposte:

- **401 UNAUTHORIZED**: Non è stato fornito il token per l'autenticazione
- **404 NOT FOUND**: Non vi è nessuna iscrizione con quell'uuid per l'utente con quel token, oppure non è ancora stato fatto alcun ping al servizio.
- **200 OK**: Token e uuid sono corretti,ed è stato fatto almeno un ping al servizio.

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
  "pinged_at": "2025-06-14T16:21:38.856451",
  "response_time": 0.2,
}
```

Di seguito è riportata una richiesta fatta correttamente al servizio, tramite il client [Bruno](https://www.usebruno.com/).

![Una richiesta fatta correttamente all'API](./assets/3.1%20-%20Richiesta%20API%20Tramite%20Bruno.PNG)

#### Token e autenticazione con l'API

Come detto sopra, l'utente ha bisogno di un token per autenticarsi con l'API.

I token dell'utente autenticato vengono gestiti sulla rotta `/you/tokens`. Tramite gli appositi pulsanti, l'utente può registrare o revocare token a suo nome.

L'autenticazione con l'API è implementata tramite l'estensione [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/), in particolare usando **`TokenHTTPAuth`**. L'autenticazione implementata dall'estensione è di tipo **Bearer**: chiunque sia in possesso del token è in grado di fare richieste all'API, senza dover fornire prova di essere il legittimo detentore della stringa.

Nel fare la richiesta GET all'API è necessario fornire il token nell'intestazione della richiesta. In particolare, va incluso nell'intestazione `Authorization`, nella forma `Bearer <token>`, come indicato sopra.

### Configurazione sicura

Come consigliato per la [Twelve-Factor App](https://12factor.net/config), la configurazione del codice andrebbe fatta usando le variabili d'ambiente del sistema che ospita l'app. In questo modo si evita di legare la configurazione al codice, e si evitano problemi comuni come includere dati sensibili nel Sistema di Controllo delle Versioni (VCS).

Il file `config.py` contiene le classi che definiscono la configurazione dell'applicazione. L'uso di una classe per la configurazione dell'applicazione Flask è una pratica [documentata dai manutentori stessi](https://flask.palletsprojects.com/en/stable/config/).

La classe `Config` viene caricata all'avvio dell'applicazione

```py title="__init__.py"
from flask import Flask
from downtime_panda.config import Config

...

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    ...

    # ------------------------------- CONFIGURATION ------------------------------ #
    logger.info("Setting up configuration...")
    app.config.from_object(config_class())
```

!!! warning "Una 'falla' voluta"
    Si noti come, anche dopo quanto detto sopra, le configurazioni dell'applicazione nell'ambiente di staging siano codificate nel file `docker-compose.staging.yml`. In un vero ambiente di produzione, tale pratica sarebbe considerata ovviamente (e giustamente) una ***falla di sicurezza***.

    In questo caso, però, l'ambiente di staging è stato pensato come una copia del possibile ambiente di produzione ma in locale. Per rendere la vita dello sviluppatore più semplice, ogni servizio nel file è già preconfigurato in modo tale da funzionare da subito, fin dal primo `git clone`.

    Se questa cosa non va bene, è sempre possibile sostituire la definizione delle variabili d'ambiente nel file `docker-compose.staging.yml` con un file `.env`: in questo modo si potrebbe mettere nel repository un file `.env.example`, che elenchi tutte le variabili d'ambiente in uso.

    ```ini title=".env.example"
    DTPANDA_SECRET_KEY=
    DTPANDA_DB_URL=
    ...
    ```

    Lo sviluppatore potrà poi copiare tale definizione in un file `.env` dove configurare a proprio piacimento l'applicazione in locale.

    In questo caso, visto che l'ambiente di staging non è pensato per essere messo direttamente in produzione, si è optato per la soluzione più comoda per lo sviluppatore.

Una alternativa più avanzata potrebbe far uso di un servizio separato per mantenere chiavi e segreti cifrati. Si veda la sezione [Gestione della Configurazione più Avanzata](5-future-developments.md#gestione-della-configurazione-piu-avanzata) per maggiori dettagli.

### Deploy come Container Docker

Docker è una tecnologia per la containerizzazione di processi.

Nel repository è presente un `Dockerfile`, che descrive come costruire e mettere su l'applicazione.  Tale file viene elaborato da docker per creare una immagine, un pacchetto contenente sorgenti, librerie, e qualsiasi altra cosa richiesta dall'applicazione per funzionare. Infine, data una immagine, Docker può mettere su un container, un processo eseguito in un ambiente isolato.

Docker non aiuta soltanto isolando i container: grazie a Docker il deploy dell'applicazione è veramente facile, dovendo solo costruire/recuperare l'immagine (in questo caso costruire, tramite `docker build`) ed avviare il container (`docker run`), o ancor più facile utilizzando sistemi per l'orchestrazione dei container (ex. `docker compose`)

### HTTPS

L'accesso sicuro all'applicazione tramite HTTPS non è gestito dall'applicazione stessa; bensì, nel `docker-compose.staging.yml` fornito è montato su un Reverse Proxy, [Caddy](https://caddyserver.com/), che si occupa di elaborare, gestire ed instradare ogni richiesta proveniente dall'esterno verso la rete interna.

Caddy genera di default un certificato autofirmato, che permette di comunicare in modo sicuro con HTTPS senza dover mettere su alcuna configurazione extra.

!!! warning "Certificato autofirmato"
    Essendo un **certificato autofirmato** da una Certificate Authority (CA) interna a Caddy, qualsiasi browser andrà ad informare l'utente che la connessione in realtà non è privata, perché il certificato dell'ente certificatore non è presente tra i certificati installati nella macchina e/o nel browser.

    La soluzione a questo problema è semplice: basta prendere il certificato della CA dal container Caddy, ed installarlo sulla macchina locale.

    A questo scopo è definito un task per recuperare e salvare in locale il certificato della CA di Caddy.

    ```sh
    task staging-copy-cert
    ```

!!! success "Contesto reale"
    Ovviamente, in un contesto reale l'utilizzo di un certificato autofirmato è inaccettabile. In un ambiente di produzione, quello che si dovrebbe fare sarebbe:

    - Comprare/essere in possesso di un dominio
    - Fare affidamento ad un ente certificatore (Ex. [Let's Encrypt](https://letsencrypt.org/)) per creare e rinnovare i certificati HTTPS per quel dominio.

Di seguito è mostrato come nell'ambiente di sviluppo sia possibile ricavare l'API token semplicemente sniffando il traffico HTTP tra il client ed il server.

![Cattura di pacchetti dell'API in HTTP, usando Wireshark](./assets/3.2%20-%20Cattura%20Pacchetto%20API%20HTTP.PNG)

Di seguito, invece, vi è lo stesso tentativo di attacco, ma fatto nel contesto dell'ambiente di staging: la comunicazione presa di mira è quella tra il client ed il reverse proxy Caddy.

![Cattura di pacchetti dell'API in HTTPS, usando Wireshark](./assets/3.3%20-%20Cattura%20Pacchetti%20API%20HTTPS.PNG)

!!! warning "Traffico tra Proxy e Servizio"
    E' bene precisare che comunque il traffico tra il reverse proxy ed il servizio (qui downtime-panda) rimane in HTTP. In un contesto isolato questo può andare bene, ma un attaccante nella rete interna potrebbe tranquillamente intercettare traffico HTTP tra i container.
