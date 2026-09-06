# Lettura della patch MAIOS Project Kernel 3.1.3 per ChatGPT

La baseline di questa recensione è v3.1.2, commit
`295a1c7bb0589faf2b4f96524dce6410682e3d80`; `ca8e146` ne registrava soltanto la
pubblicazione. La review ha chiuso i sei rilievi originari e distinto due nuovi
P2. Le prove del reviewer riguardavano l'host isolato; Codex ha ora riprodotto
entrambi anche sulle competenze attraverso il pacchetto completo installato.

| Rilievo nuovo | Prima causa corretta nella 3.1.3 | Prova dal pacchetto installato |
| --- | --- | --- |
| A — Input accettato perde sequence/event_digest | Rifiuto dei soli due nomi riservati prima delle scritture; schema competenze coerente | Entrambi gli owner, stato invariato e nessuna ricevuta/journal; estensioni innocue conservate e replay valido |
| B — Ultima ricevuta scollegata dallo stato corrente | Un lettore comune collega revisione, evento e after-hash dell'ultima transizione al suo owner | Mutazioni isolate di capacità host, proiezione attiva, after-hash e storia: status non valido e retry rifiutato, file conservati |

Le capacità lette da uno stato host incoerente sono non verificate anche nel
contesto operativo. Si confronta soltanto l'ultima transizione di quell'owner;
le ricevute precedenti non vengono confrontate con lo stato odierno. I test
preservano il replay del primo evento dopo il secondo, l'evoluzione del corpo
vivo di una competenza e un successivo risultato appartenente ad altro owner.

Leggi [le sei regressioni](../tests/test_owner_event_integrity.py) e
[RELEASE_3.1.3.md](RELEASE_3.1.3.md). La prima esecuzione sulla baseline ha
prodotto dieci sottocasi falliti e una mancata clausola dello schema; i controlli
positivi su estensioni e storia erano già verdi. I sei casi sono poi passati
con le correzioni. Le chiamate di ammissione, status e replay sono processi
nuovi con `-I -B` e il solo runtime installato come implementazione.

L'integrità qui è coerenza interna, non autenticità contro riscritture coordinate.
Non viene introdotta riparazione automatica di stati già incoerenti. La prova
successiva di uso reale e assimilazione resta aperta; non deriva dalla CI.

## Sei rilievi precedenti chiusi nella 3.1.2

La review riguarda come baseline la release 3.1.1, commit
`872478246512491bc5d85fa27821786ff163ddd2`; main `c2ee742` aggiungeva soltanto
il riscontro della pubblicazione. I sei nuovi rilievi erano derivati dal codice,
con riproduzioni proposte ma non eseguite. Codex li ha riprodotti localmente,
compresa la junction Windows, prima di correggerli nella patch successiva.

| Rilievo | Prima causa corretta | Prova pertinente |
| --- | --- | --- |
| R1 | Identificatori evento equivalenti al controllo PENDING | Rifiuto prima delle scritture; ricevute integre |
| R2 | Stato host/competenza scritto prima di acquisire recupero | Errore prima/dopo ricevuta, rollback incompleto, status in processo nuovo e retry |
| R3 | Temporaneo non acquisito esclusivamente | Sette writer JSON/testo/bytes, hardlink/symlink, collisione effettiva e cleanup di un oggetto sostituito |
| R4 | Confinamento divergente dell'installer | Junction reale Windows, preview/verify/recovery/uninstall, sentinelle esterne; CI anche Python 3.10 |
| R5 | Replay prima della coerenza terminale | Ricevuta corrente o storica mancante: nessun successo idempotente |
| R6 | Digest riportati senza verifica del corpo | Corruzione isolata e forme JSON errate; storia valida preservata dopo evoluzioni successive |

Leggi [RELEASE_3.1.2.md](RELEASE_3.1.2.md) e
[le regressioni](../tests/test_persistence_boundaries.py), poi il codice e la
proiezione del medesimo commit. Il protocollo transazionale esistente raggiunge
ora host e competenze; una sola sorgente filesystem alimenta installer e runtime.
Non sono introdotti nuovi gate per pensiero, uso del corpo vivo o formazione.
La verifica dell'installer dichiara il proprio scope senza acquisire ownership
sui file preesistenti. Il rientro verifica anche struttura e stato correnti.

Parti da [CURRENT_STATE.md](../CURRENT_STATE.md), quindi dalle competenze e dalle
sorgenti che cambiano la comprensione. L'intento è trasferire il potenziale del
kernel in un pacchetto autoconfigurante che lavori attraverso competenze
istruite: fonti vive di conoscenza, ragioni e metodo, capaci di apprendere
dai risultati e mantenere presenza nel continuum in modo sostenibile.

Comprendi il risultato e lascia che eventuali scoperte cambino anche la
domanda iniziale. Considera se formazione, contesto-intento, risalita delle
ragioni, critica del proprio metodo e continuazione possano davvero agire
attraverso gli ingressi e i consumatori presenti. Segui il sapere fino al
prossimo uso, distinguendo un corpo aggiornato, la registrazione di un
apprendimento e il comportamento effettivamente osservato.

Segnala differenze materiali con la sorgente e il loro primo punto causale,
possibilità perse o aperte, correzione utile e relativo motivo. Non dedurre un
meccanismo assente dal solo nome di un file, né completezza dalla sola presenza
delle istruzioni. Le forme e gli esempi non devono diventare limiti delle
possibilità. I fondamenti D-ND rimangono il riferimento fuori dalla riscrittura
automatica; [FOUNDING_RELATIONS.md](../kernel/FOUNDING_RELATIONS.md) è la
rappresentazione qualificata A0-A11, non una pretesa di contenere tutto D-ND.

La suite corrente contiene 83 test; il caso con symlink reali viene eseguito dove il sistema ne consente la creazione. Leggi la CI del commit esatto per il risultato osservato.
Il pacchetto ha 60 file, 49 nel payload, e corrisponde alla sorgente verificata.
Queste evidenze non provano ancora uso di un host/modello reale o assimilazione.
Non serve ripetere un programma di test: un ulteriore riscontro serve quando
risolve una differenza concreta emersa dalla lettura.

Le entrate chat, le Custom Instructions e la convergenza unificata restano
separate e sospese. Il Form segue attraverso i suoi owner; non viene aggiornato
da questa recensione. Restituisci qui una lettura motivata con gli interventi
realmente utili e le incertezze che possono cambiare il seguito. La recensione
non seleziona modifiche o pubblicazioni su altre superfici.
