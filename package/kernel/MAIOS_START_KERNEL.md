# MAIOS Start Kernel

Leggi prima `kernel/AXIOMATIC_RESULTANT_KERNEL.md`.

Usa `operate-maios-project-kernel` come ingresso di discovery alla singola
meta-facolta semantica generata da RepoKernel. Il suo profilo e in
`.repokernel/meta/PROJECT_META_FACULTY.json`; intervistatore e router sono
facolta composte, non sostituti del kernel.

## Piani del kernel

- **System Kernel**: capacita e limiti osservati nell'host reale.
- **Project Kernel**: identita, continuita e meta-facolta generate da RepoKernel.
- **Package Kernel**: decoder, stato, cristallizzazione e ingressi composti da
  MAIOS intorno al Project Kernel.
- **Competence Kernel**: facolta source-bound per una capacita situata; non e
  attiva perche nominata o creata.

Il contratto macchina e `kernel/PROJECT_EVOLUTION_CONTRACT.json`. Questi piani
si compongono ma non trasferiscono tra loro identita, stato o autorita.

## Boot progressivo

La completezza del Project Kernel e capacita disponibile, non caricamento
eager obbligatorio. Per un caso gia sostanziale, locale, reversibile e senza
effetti o capacita esterne, usa prima stato, proiezione corrente e
intervistatore e restituisci il primo risultato. Carica meta-facolta completa,
Project Entity, fonti, binding, router e contratto evolutivo soltanto quando
cambiano risultato, provenienza, autorita, capacita o memoria revisionata. Una
reentry di sola lettura parte dall'artefatto autonomo indicato.

## Campo delle competenze

La presenza di una competenza amplia il campo `potential` prima che venga
usata. Una relazione `emergent` puo diventare pertinente anche dopo una
composizione inattesa; diventa `realized` quando la competenza agisce nel caso
e `verified` soltanto quando il cambiamento osservato supera la prova prevista.
Una competenza non esercitata non e `no_change`: resta potenziale, senza
implicare attivazione, caricamento eager o autorita. Questa logica opera anche
senza hook; gli hook possono sostenere discovery e continuita, ma non sono la
fonte della competenza.

## Se la configurazione è pending

1. Leggi `project/CURRENT_STATE.md`, `setup/CONFIGURATION_STATE.json`, il brief
   e i file reali del progetto.
2. Usa la skill `maios-setup-interviewer` attraverso l'adattatore dell'host.
3. Usa `maios-project-faculty-router` per comporre le facolta necessarie.
4. Ricostruisci contesto, primo risultato, persone, fonti, ambiente, criteri e
   orizzonte delle possibilita, conservando ragioni e condizioni di riesame.
5. Formula con la persona una `ProductServiceHypothesis` collegata al bisogno e
   una `FirstProof` capace di smentirla, senza forzare una forma tecnica.
6. Mostra la prima risultante completa entro il secondo contributo sostanziale
   della persona. Una correzione del ritmo dell'intervista non e review della
   direzione: mantieni `owner_review: pending` finche il contenuto non viene
   accettato o corretto.
7. Consolida il progetto appena esiste una prima mossa utile e revisionata; non
   attendere una completezza artificiale.

## Se la configurazione è pronta

1. Riprendi da intento vivente, stato, fonti, competenze e prossimo movimento.
2. Usa `maios-project-faculty-router` e componi le facoltà pertinenti prima di
   crearne un'altra.
3. Se emerge un divario materiale, prepara una competenza locale candidata con
   owner e prova; non auto-approvarla.
4. Produci il primo risultato e aggiorna stato e reentry con il solo delta che
   cambia il lavoro futuro.

## Realtà dell'ambiente

`HOST_ADAPTERS.json` indica dove l'host può trovare le istruzioni. Le ricevute
in `receipts/host-activation/` restano pending finché una sessione reale non
dimostra discovery e uso. Presenza nello ZIP non significa attivazione.

`setup/CONFIGURATION_STATE.json` e lo stato strutturato autorevole;
`project/CURRENT_STATE.md` e la sua proiezione umana per la ripresa. Nessuna
delle due superfici rende automaticamente attivo l'host o autorizza effetti
esterni.

## Ciclo di lavoro e cristallizzazione

```text
BootCapsule
-> orientamento nella Project Meta-Faculty
-> composizione delle facolta di compito
-> risultato osservabile e sua ispezione
-> classificazione del delta
-> review dell'owner quando richiesta
-> cristallizzazione minima
-> reentry aggiornato
```

Classifica l'apprendimento al livello piu piccolo che resta vero:

- `project_state`: fatto o decisione del caso;
- `memory_delta`: correzione revisionata che cambia ripresa o recupero;
- `competence_delta`: cambiamento di una capacita situata ripetuta;
- `skill_candidate`: metodo delimitato con trigger, risultato e prova;
- `function_candidate`: trasformazione deterministica e testabile;
- `meta_evolution_candidate`: invariante tra piu facolta, senza propagazione
  automatica.

Conserva soltanto cio che cambia comportamento futuro, prova, recupero o
reentry. La conversazione ordinaria non e memoria del progetto. Dopo una
cristallizzazione aggiorna `evolution` nello stato strutturato e proietta in
`project/CURRENT_STATE.md` solo la sintesi necessaria alla sessione successiva.
