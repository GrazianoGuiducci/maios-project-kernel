# Risposta al residuo P2 della recensione di coordinamento

La review ha giudicato approvabile il coordinamento di `3.1.3+coordination.1`
al commit `7bd30bb58acfeeb8928f1dd8c53f4a34b4f50369`. Ha distinto un difetto
preesistente nel ramo iniziale senza storia. La candidata successiva
`3.1.3+coordination.2` conserva quel coordinamento e corregge questo residuo.
La release numerata resta 3.1.3; i tag pubblicati rimangono immutabili.

## Causa e correzione

`owner_state_receipt_errors()` controllava nel caso senza storia soltanto
revisione zero e assenza dell'ultimo evento. Una capacità host osservata, uno
stadio dichiarato verificato o una competenza inserita direttamente in `active`
potevano quindi precedere ogni attestazione. Una prima ammissione successiva
legava l'intero stato con il proprio hash, incorporando l'affermazione precedente.

Il ramo iniziale ora verifica le affermazioni proprie di ciascun owner:

- Per l'host, gli stadi restano `unverified` e le capacità osservate e l'evidenza
  aggregata restano vuote finché non esiste una storia di attestazione.
- Per le competenze, `active` resta vuoto finché non esiste una storia di
  ammissione. `represented` e i corpi di conoscenza sono relazioni distinte.

Lo stesso lettore serve status, continuum e ammissione: l'incoerenza è visibile
in un processo nuovo e una nuova transizione viene rifiutata prima delle
scritture. Il file resta disponibile per il recupero. Anche gli stadi host
incoerenti vengono esposti come non verificati, come già avveniva per le capacità.
L'elenco degli stadi è condiviso fra ammissione e controllo iniziale.

Il controllo non confronta l'intero stato con un template. Estensioni innocue,
capacità ancora sconosciute, competenze rappresentate e corpi vivi rimangono
evolutivi. Una vera prima osservazione fallita può essere registrata e conservare
il proprio significato; una precedente osservazione inventata non può farlo.
Una futura origine alternativa richiederà una relazione esplicitamente gestita
dal suo owner: aggiungere una semplice etichetta non crea quella provenienza.

## Prova nel pacchetto completo

Codex ha riprodotto il residuo attraverso installazioni complete temporanee e
il solo CLI installato, avviato in processi isolati. Le quattro nuove regressioni
sono in [test_initial_owner_state.py](../tests/test_initial_owner_state.py).
La prima esecuzione sulla candidata recensita falliva sui controlli di stato e
ammissione, mentre il caso positivo di estensioni e conoscenza era già valido.

| Caso | Risultato corretto |
| --- | --- |
| Capacità iniziale non attestata, poi attestazione di sola discovery | Capacità non esposta come osservata; prima ammissione rifiutata, file invariato |
| Ciascuno stadio iniziale verificato o fallito, oppure evidenza aggregata senza storia | Stato non valido; nessun prerequisito viene soddisfatto da un'affermazione non attestata |
| Competenza in `active` senza storia, poi evento per un'altra competenza | Incoerenza riconosciuta anche nell'owner indice; evento rifiutato, metodo ancora leggibile |
| Estensioni, unknowns, metodo rappresentato, vera prima osservazione e corpo evoluto | Stato valido, ammissione coerente e successiva lettura disponibili |

La suite della candidata .2 contiene 88 casi; il risultato effettivo e gli
eventuali skip appartengono alla CI del commit esatto. Il pacchetto mantiene
62 file totali e 51 nel payload. Queste prove riguardano persistenza e rientro;
l'uso semantico e l'assimilazione da parte di un secondo modello restano distinti.

## Affinamenti della documentazione

I conteggi 83 e 60/49 sono ora etichettati come evidenza della release 3.1.3;
84 e 62/51 appartengono alla candidata .1 recensita. La conoscenza di adattamento
Hermes richiama anche la discovery di progetto e la decisione esplicita di trust
descritta nella documentazione ufficiale, senza configurare alcun host.

Il ritorno ha cambiato anche la competenza: una ricevuta successiva non fornisce
retroattivamente l'origine mancante di un'affermazione precedente. La correzione
rimane nei consumatori pertinenti e preserva il sapere disponibile. Non avvia
una nuova revisione globale, Form, sito o il prodotto unificato.
