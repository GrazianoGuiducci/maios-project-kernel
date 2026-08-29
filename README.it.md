# MAIOS Project Kernel

[English version](README.md)

MAIOS Project Kernel fornisce a un progetto e al suo coder AI un kernel
operativo condiviso. Li aiuta a comprendere la situazione presente, formare un
primo risultato utile, rendere pertinenti le competenze richieste dal lavoro,
imparare da ciò che accade e continuare senza ricostruire ogni volta l'intera
conversazione.

La repository è il prodotto. La cartella tracciata [`package/`](package/) è la
proiezione autoinstallante pronta all'uso.

RepoKernel fornisce funzioni neutrali revisionate: una relazione di ingresso
Project Entity e una mappa di copertura Project Meta-Faculty. Questa repository
autonoma le traduce nel proprio campo aperto di competenze e nell'unico
proprietario semantico `maios-project-system`. RepoKernel non costruisce il
pacchetto, non viene distribuito e non è una dipendenza runtime.

L'installer e l'helper installato richiedono Python 3.10 o successivo; non sono
necessari pacchetti Python di terze parti.

Il clone ha due ingressi connessi: usare il pacchetto tracciato in un progetto,
oppure studiare e contribuire al campo pubblico di competenze del Kernel nella
repository. Il secondo ingresso dà al coder maggiore consapevolezza del
sistema senza aggiungere nulla al target installato.

## Inizia qui

Clona la repository, apri la sua radice con il coder e digli:

```text
Leggi AGENTS.md e la competenza maios-project-integration. Spiegami cosa può
aggiungere questo pacchetto al mio progetto e come lo integreresti. Dopo che
siamo d'accordo, prepara il piano di installazione.
```

Il coder forma prima una comprensione condivisa e correggibile. Poi prepara
l'anteprima di una transizione esatta e locale al progetto. Aprire la
repository non installa né esegue nulla.

```powershell
Set-Location .\package
python install.py preview --target C:\Projects\MioProgetto --mode new_repository --host codex --plan-out install-plan.json
python install.py apply --plan install-plan.json
```

Per un progetto già esistente usa `--mode existing_repository`. Sostituisci
`codex` con l'identificativo dell'host scelto, descritto più avanti.

## Studia e contribuisci

Apri la radice della repository con un coder capace e digli:

```text
Leggi AGENTS.md e la competenza maios-kernel-study. Ricostruisci il Kernel
dalle sue fonti pubbliche, spiega la relazione che vedi e mostra quali fonti,
evidenze, inferenze e questioni aperte sostengono la spiegazione.
```

Il campo pubblico collega:

| Superficie | Funzione |
| --- | --- |
| [`knowledge/KERNEL.md`](knowledge/KERNEL.md) | Fonte pubblica della relazione costitutiva del Kernel, KA, FDLA, Meta_Skill, competenza, contesto e apprendimento |
| [`research/AI_KERNEL_PAPER_FIELD.md`](research/AI_KERNEL_PAPER_FIELD.md) | Campo consapevole degli stati delle affermazioni per paper e articoli rigorosi |
| [`maios-kernel-study`](skills/maios-kernel-study/SKILL.md) | Studia, spiega, confronta e interroga il Kernel dalle fonti pubbliche |
| [`maios-kernel-paper`](skills/maios-kernel-paper/SKILL.md) | Forma un paper o articolo attraverso il campo assiomatico pertinente |
| [`maios-kernel-contribution`](skills/maios-kernel-contribution/SKILL.md) | Trasforma un'idea, un metodo, una correzione o un falsificatore umano o AI in contributo legato alla sorgente |
| [`contributions/GPT_PRO_START.md`](contributions/GPT_PRO_START.md) | Apre un ciclo delimitato di contribuzione con GPT Pro |

Queste competenze agiscono sulla repository e non fanno parte della proiezione
installabile corrente. Una persona, GPT Pro, Codex o un altro modello capace
può contribuire attraverso la stessa relazione canonica. Contributo, merge,
proiezione nel pacchetto, release, installazione e uso osservato restano effetti
distinti.

## Cosa accade dopo l'installazione

```text
operatore e progetto reale
-> boot stabile del Kernel
-> attivazione per progetto nuovo o esistente
-> contesto vivo e orizzonte delle possibilità
-> le competenze pertinenti agiscono da sole o insieme
-> primo risultato utile e correggibile
-> l'apprendimento riusabile ritorna alla competenza più vicina
-> la sessione successiva riparte dal campo del progetto così modificato.
```

Il Kernel non è una risposta predefinita, un workflow fisso o un catalogo di
skill. È il sistema di progetto che mantiene collegati intento, fonti,
contesto, possibilità, competenze, risultati, apprendimento e rientro mentre il
progetto cambia.

## Due condizioni iniziali

### Progetto nuovo

Il Kernel stabilisce soltanto identità e contesto necessari per muoversi:

- cosa la persona vuole cambiare;
- fonti, persone, confini e ignoti già presenti;
- poche possibilità realmente differenti, con le loro ragioni;
- una direzione correggibile;
- il primo risultato utile e il modo per metterlo alla prova.

Restituisce valore prima di chiedere dettagli non decisivi.

### Progetto esistente

Il Kernel entra come nuovo partecipante senza sostituire l'identità del
progetto. Legge fonti, istruzioni, convenzioni, stato, lavoro attivo e segnale
dell'operatore già presenti. Quindi:

- conserva il materiale esistente;
- ricostruisce il contesto vivo senza ripetere ciò che il progetto sa;
- espone il primo contributo utile del Kernel;
- compone le competenze già raggiungibili;
- forma soltanto le competenze aggiuntive rese necessarie dal lavoro reale.

L'installer non esegue merge semantici nascosti. I percorsi divergenti restano
conflitti che coder e operatore risolvono esplicitamente.

## Boot stabile, contesto vivo

I progetti installati partono da `START_HERE.md`. È un boot stabile del sistema,
non un diario continuamente riscritto. Ripristina:

- che cos'è il Kernel;
- come il progetto vi entra;
- come si collegano avvio, contesto, adattamento all'host, lavoro delle
  competenze, apprendimento e rientro.

Il contesto mutevole rimane nella relazione corrente con l'operatore, nelle
fonti reali, in `setup/CONFIGURATION_STATE.json`, in
`project/CURRENT_STATE.md`, nei risultanti recenti e nelle competenze che
agiscono. Il boot cambia soltanto quando cambia la relazione stabile del
Kernel.

## Competenze operative incluse

| Competenza | Funzione |
| --- | --- |
| `maios-project-integration` | Comprende e spiega il pacchetto repository, poi prepara l'integrazione posseduta dal target |
| `maios-project-system` | Mantiene raggiungibile l'intera relazione del Kernel di progetto |
| `maios-start-new-project` | Forma il primo movimento situato di un progetto realmente nuovo |
| `maios-start-existing-project` | Attiva il Kernel in un progetto operativo senza sostituirne l'identità |
| `maios-project-context` | Ricostruisce contesto vivo, possibilità utili, direzione, prova e passaggi alle competenze |
| `maios-project-competence-formation` | Forma o evolve la più piccola competenza locale utile quando rimane un divario reale |
| `maios-project-host-adaptation` | Traduce la relazione neutrale del Kernel nelle convenzioni native del coder corrente |

Le competenze sono il sapere operativo del sistema. Svolgono il lavoro per cui
sono pertinenti, conservano l'apprendimento causale riusabile e possono
migliorare, comporsi, essere superate o ritirarsi attraverso l'uso successivo.

## Come evolve il sistema

Il Kernel installato è un seme. La sua evoluzione ordinaria non dipende da un
meccanismo permanente di aggiornamento software:

```text
lavoro reale
-> agisce la competenza pertinente
-> risultato effettivo e correzione
-> la differenza riusabile cambia il proprietario più vicino
-> un lavoro successivo e non identico usa, rivede o invalida l'apprendimento.
```

Quando le competenze esistenti non riescono a sostenere una relazione
materiale, la facoltà di formazione crea il corpo proprietario minimo utile:
metodo, riferimento, protocollo, funzione, skill o relazione di coordinamento.
Non copia nel progetto il generatore privato dei kernel completi.

Se in futuro diventa necessario un aggiornamento strutturale, potrà essere
consegnato come competenza capace di comprendere e aggiornare il proprio
sistema. Non è un requisito del prodotto attuale.

## Coder e harness supportati

Ogni host riceve lo stesso Kernel neutrale e le stesse fonti delle competenze.
Il profilo fornisce soltanto una proiezione nativa iniziale; la competenza di
adattamento traduce la meccanica restante senza creare un Kernel diverso.

| Host id | Coder o harness | Proiezione locale iniziale |
| --- | --- | --- |
| `codex` | ChatGPT / Codex coding agent | `.agents/skills/` con tutti i proprietari portabili |
| `claude` | Claude Code | `.claude/skills/` con sistema e adattamento host |
| `opencode` | OpenCode | `.opencode/skills/` con sistema e adattamento host |
| `hermes` | Hermes | `.hermes/skills/` con sistema e adattamento host |
| `openclaw` | OpenClaw | `.agents/skills/` con sistema e adattamento host |
| `pi` | Pi coding agent | `.agents/skills/` con sistema e adattamento host |
| `dsh` | DeepSeek Harness | `.agents/skills/` con sistema e adattamento host |
| `generic` | Un altro coder capace | istruzioni radice e fonti neutrali in `skills/` |

Installazione, scoperta nativa, lettura dello stato, uso semantico, risultato
osservato e rientro mantenuto restano stati distinti. Un percorso proiettato
non dichiara che quel particolare host abbia già esercitato il Kernel.

Consulta [compatibilità host](docs/COMPATIBILITY.md) per i dettagli specifici.

## Contratto di installazione

La cartella generata `package/` contiene manifest e inventario SHA-256 esatti.
L'installazione usa un piano di anteprima immutabile:

- `new_repository` accetta soltanto un target assente o vuoto e promuove
  atomicamente una directory di staging completa;
- `existing_repository` inventaria il target, crea i percorsi mancanti,
  conserva quelli identici e rifiuta il contenuto divergente;
- una modifica al pacchetto o al target invalida il piano;
- un'installazione interrotta può recuperare dal proprio journal `PENDING`;
- riapplicare lo stesso pacchetto a un'installazione invariata è idempotente;
- la disinstallazione rimuove soltanto file invariati posseduti dall'installer;
- i file evoluti dal progetto vengono conservati e dichiarati.

L'installer non modifica configurazione globale dell'host, hook, plugin,
provider, credenziali, servizi, repository o altri progetti.

Comandi di verifica e recupero:

```powershell
python C:\Projects\MioProgetto\.maios\installer\installer.py verify --target C:\Projects\MioProgetto
python C:\Projects\MioProgetto\.maios\installer\installer.py uninstall --target C:\Projects\MioProgetto --receipt-out uninstall-receipt.json
python install.py recover-pending --target C:\Projects\MioProgetto
```

La procedura completa è in [Installazione](docs/INSTALLATION.md).

## Funzionamento locale al progetto

Dopo l'installazione apri il progetto target e chiedi al coder di leggere
`START_HERE.md`. Alcuni comandi locali utili:

```powershell
python maios.py status
python maios.py configuration-status
python maios.py competence-status
python maios.py learning-status
python maios.py operating-status
```

Gli helper di configurazione possono validare e applicare un candidato
accettato con controllo di concorrenza e recupero. Gli helper di composizione e
risultante espongono il campo rappresentato e aggiornano la continuità quando
quel passaggio durevole serve davvero; non sostituiscono il giudizio semantico
del coder e dell'operatore.

## Struttura del pacchetto e della sorgente

```text
sorgenti vive della repository autonoma
+ funzioni RepoKernel revisionate e tradotte in relazioni native del proprietario
-> release/PROJECTION.json dichiarata
-> proiezione deterministica e tracciata package/
-> MANIFEST.json e PACKAGE_INVENTORY.json esatti
-> anteprima e installazione possedute dal target
-> Kernel, stato, competenze, apprendimento e rientro locali al progetto.
```

| Proprietario | Funzione |
| --- | --- |
| `kernel/` | Kernel semantico, campo aperto delle facoltà, composizione e coltivazione delle competenze |
| `skills/` | Competenze di integrazione, sistema, avvio, contesto, formazione, adattamento host e gestione sorgente |
| `knowledge/`, `research/`, `contributions/` | Comprensione del Kernel, ricerca con stati delle affermazioni e campo di contribuzione delle competenze nativi della repository |
| `setup/`, `project/`, `state/` | Configurazione canonica e continuità compatte del progetto |
| `src/maios_project_kernel/` | Proiezione deterministica, installer, configurazione, runtime, stato host e readback operativo |
| `adapters/` | Proiezioni locali per gli host |
| `templates/` | Superfici di ingresso della distribuzione e del progetto installato |
| `release/repokernel/` | Input RepoKernel vincolato alla sorgente, mappa funzionale generata e ricevuta di traduzione |
| `release/PROJECTION.json` | Mappa completa da sorgente a pacchetto |
| `package/` | Superficie di installazione generata, tracciata e direttamente usabile |
| `tests/` | Fixture di sorgente, pacchetto, installazione, recupero, stato e comportamento |

`package/` viene generata dai proprietari vivi e non deve essere modificata a
mano.

## Costruzione dalla sorgente

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B tools\build_release.py
python -B tools\verify_distribution.py
```

Il builder rigenera `package/`, il suo manifest e l'inventario esatto.

## Evidenze e limiti attuali

Sorgente, proiezione deterministica, inventario, meccanica dell'installer,
routing di avvio, profili host e contratti di stato locale sono ispezionabili
nella repository. Non dimostrano da soli accettazione semantica da parte di un
operatore reale, uso nativo in ogni host o comportamento mantenuto in lavori
successivi non identici. Queste osservazioni restano evidenze separate.

Il pacchetto autoconfigurante contiene traduzioni native delle funzioni neutrali
RepoKernel revisionate, ma non importa risposte del Form MAIOS, sorgente privata
RepoKernel, topologia privata D-ND/TMx, credenziali, stato runtime o hook
lifecycle. Il Project Kernel generato separatamente dal Form è un'altra pipeline
con builder, contesto, byte e prove proprie.

Consulta [Architettura](docs/ARCHITECTURE.md),
[Provenienza](docs/PROVENANCE.md) e [Ricevute](docs/RECEIPTS.md) per i dettagli.

## Licenza

Sorgente e contenuto generato, esclusi nomi e marchi, sono disponibili con
[licenza MIT](LICENSE). Consulta [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
e [TRADEMARKS.md](TRADEMARKS.md).
