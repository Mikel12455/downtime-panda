# Principali Caratteristiche dell'Applicazione

In questa sezione sono elencate le principali caratteristiche dell'applicazione, che siano correlate alla sicurezza o meno.

## Generale

### Ping di servizi 🏓

Il principale servizio offerto dall'applicazione è il monitoraggio dello stato di risorse o servizi in rete: l'utente chiede all'applicazione, ad esempio, di monitorare lo stato di un sito web, e questa farà, in background, richieste periodiche al sito web per verificarne lo stato.

Questa feature è implementata tramite il pacchetto [APScheduler](https://apscheduler.readthedocs.io/en/latest/), gestito dall'estensione [Flask-APScheduler](https://viniciuschiele.github.io/flask-apscheduler/).

### Versionamento delle Migrazioni del DB 🗃

Lo schema dell'intero DB è versionato grazie all'uso di [Alembic](https://alembic.sqlalchemy.org/en/latest/), gestito tramite l'estensione [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/index.html).

La cartella `migrations/versions` versiona ogni modifica fatta allo schema del DB, in modo da poter ricreare lo stesso db ovunque.

### Ambiente di test, sviluppo e staging 👨‍💻

Questo progetto offre tre ambienti diversi:

- **Test**: E' l'ambiente usato da `pytest` per far girare gli unit test. Fa uso di un database SQLite in memoria, ricreato ogni volta per ogni singolo test.
- **Sviluppo**: E' l'ambiente per sviluppare. L'applicazione *gira localmente* su `localhost:8080`, è abilitata al *DEBUG* e all'*autorefresh* dopo ogni modifica, e fa uso di un *database `SQLite`* creato automaticamente in `src/instance/dtpanda.db`. Il file del database è ignorato da `git`.
- **Staging**: E' un ambiente che cerca di copiare un ambiente di produzione. Monta su non solo l'applicazione, ma anche un database Postgres e un Reverse Proxy con Caddy. Funziona grazie a `docker compose`

Per quanto non sia direttamente una feature di sicurezza, avere questi tre ambienti ha comunque un effetto indiretto sulla stessa:

- L'ambiente di test permette di verificare automaticamente il **corretto funzionamento** dell'applicazione, individuando eventuali **regressioni e bug** scaturiti dall'aggiunta di nuove feature.
- L'ambiente di sviluppo cerca di essere quanto meno oneroso nell'utilizzo da parte dello sviluppatore. Con i log di Debug abilitati e il refresh della pagina automatico dopo ogni nuova feature, si cerca di rendere lo sviluppo quanto più rapido possibile.
- L'ambiente di staging offre un modo di testare l'applicazione in un ambiente simile a quello di produzione. L'idea è così catturare problemi che non sarebbe possibile verificare durante il solo sviluppo (ad esempio, scaturiti dall'uso di un Reverse Proxy tra l'utente e l'applicazione)

### Pre-Commit, Task e MkDocs 📄

Più dei "nice-to-have" che delle vere e proprie funzionalità dell'applicazione, hanno comunque la loro utilità.


## Sicurezza

### Gestione dell'utente

### Accesso all'API tramite Token



### Configurazione sicura

Come consigliato per la [Twelve-Factor App](https://12factor.net/config), la configurazione del codice andrebbe fatta usando le variabili d'ambiente del sistema che ospita l'app. In questo modo si evita di legare la configurazione al codice, e si evitano problemi comuni come includere dati sensibili nel Sistema di Controllo delle Versioni (VCS).

Il file `config.py` contiene le classi che definiscono la configurazione dell'applicazione. L'uso di una classe per la configurazione dell'applicazione Flask è una pratica [documentata dai manutentori stessi](https://flask.palletsprojects.com/en/stable/config/).

All'avio dell'applicazione, la classe `Config` viene caricata.

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

### HTTPS

L'accesso sicuro all'applicazione tramite HTTPS non è gestito dall'applicazione stessa; bensì, nel `docker-compose.staging.yml` fornito è montato su un Reverse Proxy che si occupa
