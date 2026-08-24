---
name: maios-project-faculty-router
description: Seleziona, compone e mantiene le facolta operative di un progetto MAIOS; crea una competenza locale candidata soltanto quando il lavoro osservabile espone un divario reale non chiuso dalle capacita presenti.
---

# MAIOS Project Faculty Router

Usa questa facolta durante la configurazione e quando un nuovo compito cambia le
capacita necessarie al progetto.

Ricevi l'orientamento da `operate-maios-project-kernel`, che espone la singola
meta-facolta semantica generata. Questo router seleziona facolta di compito e
non diventa un secondo kernel o proprietario dello stato.

## Orientare La Capacita

1. ricostruisci risultato richiesto, fonti, ambiente e responsabilita;
2. osserva le skill realmente disponibili nel progetto e nell'host;
3. seleziona una facolta primaria e soltanto i supporti che cambiano il
   risultato;
4. componi prima le facolta presenti;
5. lascia che una composizione inattesa esponga una relazione `emergent` senza
   precomputare l'intero catalogo delle competenze;
6. se resta un divario materiale, descrivilo attraverso comportamento mancante
   e prova falsificabile.

Una facolta nominata, referenziata o presente come contratto non e operativa se
l'host non puo scoprirla e usarla.

Tratta una facolta disponibile ma non esercitata come `potential`, non come
`no_change`. Chiamala `realized` quando ha agito nel caso e `verified` soltanto
quando il suo delta supera la prova dichiarata. Il router mantiene questa
distinzione anche senza hook.

## Creare O Evolvere Una Competenza Locale

Quando il divario rimane:

1. prepara `skills/<nome>/SKILL.md` come candidato locale;
2. registra bisogno, fonti, owner, confine, comportamento e verifica;
3. sottoponilo alla persona responsabile del progetto;
4. dopo l'accettazione conserva versione, evidenza e condizione di riesame;
5. aggiorna stato e reentry soltanto se il comportamento futuro cambia.

Non creare una skill per preferenze episodiche o per ripetere istruzioni gia
presenti. Non auto-approvare la facolta candidata.

Quando il lavoro produce apprendimento, usa
`kernel/PROJECT_EVOLUTION_CONTRACT.json` per classificare il delta. Un fatto o
una decisione del caso resta `project_state`; una correzione di reentry e
`memory_delta`; una capacita situata ripetuta e `competence_delta`; un metodo
delimitato e `skill_candidate`; una trasformazione deterministica e
`function_candidate`; un invariante tra facolta e
`meta_evolution_candidate`. La classificazione non accetta ne attiva il
candidato.

## Orizzonte E Rappresentazione

Cataloghi e schemi sono lenti, non confini. Se una relazione rilevante non e
rappresentabile, conservala come `retained_unknown` con fonte, differenza,
invalidatore e condizione di riesame.

## Risultato

Restituisci in modo compatto:

```text
risultato:
facolta_primaria:
supporti_utili:
composizione:
divario_residuo:
competenza_candidata_o_no_change:
prova:
prossimo_movimento:
```

La riuscita e un comportamento migliorato e riprendibile, non un elenco di
competenze.
