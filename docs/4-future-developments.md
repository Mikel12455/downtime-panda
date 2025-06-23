# Sviluppi Futuri

## Back-End come API pura

Visto che l'applicazione espone una API per prendere gli ultimi token, una idea potrebbe essere dividere il Front-End ed il Back-End in due servizi separati:

- Il Back-End sarebbe puramente una API, scritta in [Flask](https://flask.palletsprojects.com/en/stable/) o anche in [FastAPI](https://fastapi.tiangolo.com/).
- Il Front-End, gestito a parte ad esempio con [node.js](https://nodejs.org/en/about) e [npm](https://www.npmjs.com/), sarebbe giusto una interfaccia per fare chiamate all'API.

I principali vantaggi di questa soluzione sarebbero:

- **Semplificare il Back-End**: Niente più gestione di template Jinja, o di rotte separate per front-end ed API. Ogni rotta diverrebbe una chiamate API che ritorna, ad esempio, file JSON come risposta.
- **Deploy separati**: Si potrebbero mettere su e far evolvere i due servizi in modo separato, gestiti anche da team di sviluppo diversi. Inoltre, sarebbe più facile creare interfacce alternative (ad esempio client desktop/mobile nativi, fatti anche da terze parti).

## Servizi Pubblici & Amministrazione

L'idea originale era monitorare sia servizi "pubblici", consultabili anche da utenti non iscritti, che "privati", consultabili solo da utenti registrati, ma non è stato possibile per mancanza di tempo.

L'implementazione corrente supporta solamente i servizi "privati": gli utenti, tramite la loro iscrizione, cominciano a far monitorare una certa risorsa al servizio. In un certo senso, conoscere l'uri del servizio fa da chiave per poter accedere al monitoraggio dello stesso.

La distinzione di servizi pubblici da privati introduce un problema che richiede una soluzione più "umana" piuttosto che "tecnologica": Se un utente potesse scegliere di rendere un servizio monitorato da lui pubblico a tutti, niente vieterebbe ad un qualsiasi utente di rendere pubblico il servizio di qualcun'altro (ad esempio, un piccolo server a casa di qualcuno che è semplicemente esposto all'esterno per uso personale).

Pertanto, una tale distinzione andrebbe probabilmente risolta introducendo una parte di amministrazione nel sistema. Gli amministratori sarebbero coloro che decidono, eventualmente sotto richiesta di numerosi utenti, se rendere un servizio monitorato da downtime-panda "pubblico".

## Notifiche e Avvisi di Downtime

Una feature molto utile sarebbe mandare avvisi di eventuali downtime dei servizi monitorati, tramite email o altro sistema (ad esempio [ntfy.sh](https://ntfy.sh/)). Quando un servizio va offline, oppure torna online dopo un periodo di inattività, si potrebbe inviare un avviso a chiunque stia monitorando tale servizio.

## Gestione della Configurazione più Avanzata

Come già menzionato nelle sezioni precedenti, la configurazione del progetto è gestita tramite variabili d'ambiente.

Una alternativa a questa pratica è l'utilizzo di un servizio separato per mantenere la configurazione del servizio, utilizzando ad esempio [Hashicorp Vault](https://github.com/hashicorp/vault). L'idea sarebbe mantenere i segreti dell'applicazione (quali credenziali del DB e chiavi di cifratura) in questo servizio, il quale salva queste informazioni su disco cifrate.

L'applicazione dalle variabili d'ambiente dovrà recuperare una ed una sola informazione: Il token per accedere al servizio di configurazione. Questo permette di:

- Ridurre il numero di segreti da gestire nelle variabili d'ambiente
- Implementare la rotazione dei segreti
  - Si può addirittura implementare la creazione ad-hoc dei segreti: ad esempio, creare "al volo" le credenziali di accesso al DB per l'applicazione

Ovviamente, tale gestione non dovrebbe compromettere l'ambiente di sviluppo, che potrebbe continuare a funzionare con le variabili d'ambiente originali oppure con una versione "falsata" (**mocked**) del servizio.
