# Sviluppi Futuri

## Back-End come API pura

Visto che l'applicazione espone una API per prendere gli ultimi token, una idea potrebbe essere dividere il Front-End ed il Back-End in due servizi separati:

- Il Back-End sarebbe puramente una API, scritta in [Flask](https://flask.palletsprojects.com/en/stable/) o anche in [FastAPI](https://fastapi.tiangolo.com/).
- Il Front-End, scritto ad esempio tramite [Vue.js](https://vuejs.org/) o framework simili, sarebbe giusto una interfaccia per fare chiamate all'API.

I principali vantaggi di questa soluzione sarebbero:

- **Semplificare il Back-End**: Niente più gestione di template Jinja. Ogni rotta diverrebbe una chiamate API che ritorna, ad esempio, file JSON come risposta.
- **Deploy separati**: Si potrebbero mettere su e far evolvere i due servizi in modo separato, gestiti anche da team di sviluppo diversi. Inoltre, sarebbe più facile creare interfacce alternative (ad esempio client nativi, fatti anche da terze parti)

## Servizi Pubblici & Amministrazione

L'idea originale era monitorare sia servizi "pubblici" che "privati", ma non è stato possibile per mancanza di tempo.

Per il momento sono gli utenti a creare

## Gestione della Configurazione più Avanzata

HashiCorp Vault.
