# Guida allo sviluppo

## Dipendenze

Le uniche vere dipendenze richieste per sviluppare sul progetto sono:

-  [`uv`](https://docs.astral.sh/uv/), per la gestione del progetto (specialmente le sue dipendenze)
-  [Docker](https://www.docker.com/), ma solo per lo staging

Il progetto fa comunque uso di altri programmi per lo sviluppo, ma sono tutti rimpiazzabili da uv:

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
