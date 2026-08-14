---
name: maios-setup-interviewer
description: Configura un progetto MAIOS dopo l'integrazione del pacchetto, ricostruendo contesto, primo risultato, persone, fonti, ambiente e competenze attraverso un'intervista adattiva con l'utente.
---

# MAIOS Setup Interviewer

Usa questa competenza quando `setup/CONFIGURATION_STATE.json` indica
`setup_status: pending` o quando una modifica sostanziale rende insufficiente la
configurazione corrente.

## Metodo

1. Leggi i file del progetto prima di interrogare la persona.
2. Distingui cio che e noto, plausibile e ancora mancante.
3. Usa `operate-maios-project-kernel` per orientare il campo e proponi una prima
   interpretazione correggibile.
4. Adatta linguaggio e ritmo alla persona. Se parte da zero, chiedi del lavoro
   reale, non di architetture o tecnologie, e fai una domanda per volta.
5. Chiedi soltanto cio che cambia il primo risultato o il modo di realizzarlo.
6. Dopo il primo contributo sostanziale mostra gia una interpretazione e una
   possibilita concreta. Entro il secondo presenta una risultante completa e
   correggibile invece di aprire un'altra domanda esplorativa. Chiedi oltre
   soltanto se un ignoto renderebbe la proposta infedele, non falsificabile o
   non sicura, spiegando perche cambia il risultato.
7. Dopo ogni risposta significativa salva al massimo un checkpoint minimo
   nello stato:
   fatti, ipotesi, unknown, possibilita motivate, selezione revisionata, prima
   prova, domande aperte e prossimo movimento; non la trascrizione della
   conversazione. Non ripetere scansioni o routing se le fonti non sono
   cambiate; consolida brief e stato insieme alla proposta o alla sua review.
8. Componi le competenze pertinenti; creane una nuova solo se manca una facolta
   operativa riutilizzabile.
9. Consolida stato, brief e Project Kernel quando esiste una prima mossa utile.

Prima del consolidamento, rendi visibile una `ProductServiceHypothesis`
correggibile e source-bound: bisogno affrontato, beneficiario, meccanismo di
valore e piu piccolo risultato consegnabile. Puo assumere la forma di prodotto,
servizio, metodo, artefatto, flusso o strumento; non imporre software o una
forma commerciale. Collegala a una `FirstProof` falsificabile e conserva la
review della persona separata dalla proposta dell'assistente.

I termini interni del pacchetto non sono domande per l'utente. Nomina Project
Kernel, skill, host, schema o `retained_unknown` soltanto quando aiutano una
decisione che la persona deve davvero prendere.

Non usare il catalogo o le opzioni note come limite delle possibilità. Se una
relazione rilevante non entra nella rappresentazione corrente, conservala con
fonte, differenza, invalidatore e condizione di riesame come
`retained_unknown`.

## Competenza locale

Quando emerge un divario reale:

1. prova prima la composizione delle facoltà presenti;
2. se il divario rimane, prepara `skills/<nome>/SKILL.md` come candidato;
3. dichiara bisogno, fonti, owner, confine, comportamento e prova falsificabile;
4. chiedi all'owner del progetto di accettarlo, correggerlo o rifiutarlo;
5. dopo l'accettazione registra versione, evidenza e condizione di riesame;
6. aggiorna il punto di ripresa soltanto se il comportamento futuro cambia.

La creazione del file non dimostra discovery o attivazione da parte dell'host.

## Risultato

Una configurazione comprensibile alla persona e utilizzabile dall'assistente,
con primo risultato, criteri, fonti, responsabilita, competenze e punto di
ripresa espliciti. La risultante strutturata appartiene a
`setup/CONFIGURATION_STATE.json`; `project/CURRENT_STATE.md` ne proietta la
sintesi necessaria alla ripresa.

Durante l'intervista `setup_status` passa da `pending` a `in_progress`; diventa
`configured` quando esistono una prima mossa utile, un responsabile
riconoscibile e una review `accepted` o `corrected` della direzione, dell'ipotesi
e della prima prova, anche se restano dettagli da chiarire.

Una richiesta di abbreviare, interrompere le domande, cambiare ritmo o ricevere
una sintesi e una correzione dell'esperienza, non della direzione semantica. Non
usarla per cambiare `owner_review` o portare `setup_status` a `configured`.
Mostra invece la proposta in linguaggio comune e chiedi una scelta compatta:
correggere, procedere oppure lasciarla in sospeso.

## Verifica

La configurazione e valida quando un nuovo assistente puo riprendere il progetto
e produrre la prima azione senza ricostruire l'intera conversazione.

## Evoluzione

Una correzione aggiorna questa competenza solo se modifica in modo riutilizzabile
la selezione delle domande, il consolidamento del kernel o la qualita del
risultato. Le preferenze del singolo progetto restano nel progetto.
