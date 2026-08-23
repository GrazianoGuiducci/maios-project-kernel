# MAIOS Self-Configuring Project

Questo e un nuovo progetto configurato dopo l'apertura insieme alla persona.

Prima di iniziare il lavoro:

1. usa `operate-maios-project-kernel` come unico ingresso alla meta-facolta
   semantica generata da RepoKernel;
2. leggi `START_HERE.md`, `project/CURRENT_STATE.md` e
   `setup/CONFIGURATION_STATE.json`;
3. se `setup_status` e `pending`, usa `maios-setup-interviewer`;
4. usa `maios-project-faculty-router` per selezionare e comporre le facolta
   pertinenti prima di crearne una nuova;
5. produci appena possibile un primo risultato riconoscibile e aggiorna stato,
   brief e punto di ripresa; se il risultato cambia il lavoro futuro, usa
   `kernel/PROJECT_EVOLUTION_CONTRACT.json` e cristallizza soltanto il delta
   revisionato.

Usa il boot progressivo di `operate-maios-project-kernel`. Se il messaggio
contiene gia un caso sostanziale, il lavoro e locale e reversibile,
`effect_authority` e `none` e non servono capacita esterne o nuove facolta,
leggi prima soltanto stato, proiezione corrente e intervistatore e restituisci
la proposta completa prima del boot profondo. Su una reentry di sola lettura,
rispondi prima dall'artefatto autonomo indicato. Meta-facolta completa, Project
Entity, fonti, binding, router e contratto evolutivo restano disponibili e
vengono caricati quando cambiano risultato, provenienza, autorita, capacita o
memoria revisionata; non sono una tassa obbligatoria sul primo risultato.

Durante il setup mostra una prima risultante completa entro il secondo
contributo sostanziale della persona. Non trasformare una richiesta di
abbreviare, fermare le domande o cambiare ritmo in accettazione della direzione:
la review semantica richiede che la persona accetti o corregga il contenuto
della proposta.

La logica semantica autorevole resta nel Project Kernel sotto `.repokernel`.
Intervistatore, router e adattatori dell'host la rendono operativa ma non sono
kernel concorrenti e non possono sostituirla.

Quando più ingressi host sono presenti, usa il contratto nativo dell'host che
sta eseguendo il progetto senza trasformare le istruzioni degli altri host in
azioni. In DSH il percorso nativo delle skill è `.agents/skills`; le indicazioni
`.claude/skills` restano specifiche di Claude Code. Nessun adattatore cambia il
proprietario dello stato o concede autorità aggiuntiva.

Non trattare cataloghi, opzioni o schemi come limite delle possibilita. Conserva
una relazione materiale non rappresentabile come `retained_unknown`. Non
dichiarare attivi strumenti, dati, integrazioni o competenze senza evidenza
dell'ambiente reale.

Quando verifichi il profilo entita, usa la serializzazione dichiarata in
`MANIFEST.json`, `canonical_json_utf8_sorted_compact`: l'hash canonico JSON e
il binding, mentre l'hash dei byte del file formattato si confronta soltanto
con `PACKAGE_INVENTORY.json`. Un catalogo pinned consegnato come reference e
segnato `not_present` e una fonte non installata, non una capacita attiva e non
da solo un errore del pacchetto.

Le azioni esterne e irreversibili restano separate dalla configurazione del
progetto e richiedono l'autorita pertinente. La presenza del pacchetto autorizza
soltanto le modifiche locali necessarie a configurare questo nuovo progetto.
