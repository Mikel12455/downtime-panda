# Guida allo sviluppo

In questa sezione è illustrato il setup del progetto per lo sviluppo

## Setup in breve

Clona il progetto da github

``` sh
git clone https://github.com/Mikel12455/downtime-panda.git
```

Poi, metti su l'ambiente virtuale

``` sh
cd downtime-panda
task setup
```

!!! warning "Se non ho [Taskfile](https://taskfile.dev/)?"

    Se non hai Taskfile installato, puoi invece seguire questi comandi:

    ``` sh
    cd downtime-panda
    uv sync --all-packages
    uv run pre-commit install
    ```

    In questo modo avrai lo stesso setup del comando di sopra, ma come extra avrai Task installato direttamente nel tuo ambiente virtuale!

    Ricordati giusto che ti servirà uv per richiamare le task. In sostanza, invece del comando

    ``` sh
    task do-something
    ```

    dovrai usare

    ``` sh
    uv run task do-something
    ```

### Sviluppo

Messo su l'ambiente virtuale, fai partire il progetto nell'ambiente di sviluppo tramite

``` sh
task dev-up
```

Da un browser vai su `https://localhost:8080/` per vedere le modifiche che apporti al codice in tempo reale!

### Staging

Se vuoi fare qualche test più reale, completo di database PostgreSQL e di Reverse Proxy, usa questo comando

``` sh
task docker-up
```

Questo costruirà un container Docker del progetto, e lo metterà su tramite `#!sh docker compose up`

## Dipendenze

Le uniche vere dipendenze richieste per sviluppare sul progetto sono:

-  [`uv`](https://docs.astral.sh/uv/), per la gestione del progetto (specialmente le sue dipendenze)
-  [Docker](https://www.docker.com/), ma solo per lo staging

Il progetto fa comunque uso di altri programmi per lo sviluppo, ma sono tutti inclusi nell'ambiente virtuale gestito da `uv`

- [`pre-commit`](https://pre-commit.com/): Configura dei git hook per cose come linter, formatter, e in generale controlli del sorgente prima di una commit.
    - Incluso tra le dipendenze `--dev`, quindi non serve installarlo globalmente

- [`mkdocs`](https://www.mkdocs.org/): Costruisce la documentazione che stai leggendo adesso ;)
    - Incluso tra le dipendenze `--dev`, assieme ad altri suoi plugin

- [`Taskfile`](https://taskfile.dev/):
    - Se non lo avete installato globalmente, si può installare nell'ambiente virtuale del progetto tramite

        ```
        uv sync --group task
        ```

        L'unica cosa è che invece di usare `task <un_task>` si deve usare `uv run task <un_task>`
