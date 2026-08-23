# MAIOS Project Kernel

> Bozza generata dal sistema il 23 agosto 2026. **Non ancora revisionata.**

[English version](README.md)

MAIOS Project Kernel è un pacchetto autoconfigurante per iniziare un nuovo
progetto insieme a un assistente AI. Non richiede di conoscere in anticipo
l'architettura, le skill o persino il prodotto da costruire: parte dal lavoro
reale della persona, rende esplicito ciò che ha compreso e propone un primo
risultato correggibile.

Il pacchetto porta nel progetto identità, memoria operativa, fonti, capacità,
criteri di riuscita e continuità. La persona conserva il controllo sulle
decisioni; installazioni, pubblicazioni e integrazioni esterne non vengono
attivate implicitamente.

## Scarica e inizia

La via consigliata è la pagina
[Releases](https://github.com/GrazianoGuiducci/maios-project-kernel/releases/latest),
che contiene lo ZIP installabile e il relativo SHA-256.

1. Crea una cartella nuova e vuota per il progetto.
2. Estrai al suo interno tutto il contenuto dello ZIP.
3. Apri la cartella con il tuo assistente.
4. Scrivi: `Leggi START_HERE.md e iniziamo la configurazione.`

Questa release è destinata a **un progetto nuovo**. Non va estratta sopra un
repository esistente: quel caso richiede un percorso di integrazione separato.

Il contenuto installabile è ispezionabile nella directory [`package/`](package/).
Le istruzioni complete sono in [`package/START_HERE.md`](package/START_HERE.md).

## Due ingressi, la stessa funzione

MAIOS offre due modi per arrivare a un Project Kernel situato:

- **Pacchetto autoconfigurante:** il contesto viene scoperto dopo il download,
  attraverso un dialogo iniziale con la persona.
- **[Form MAIOS](https://maios.it/form.html):** parte da informazioni già
  strutturate, che vengono discusse e affinate prima della generazione.

Nel primo caso l'assistente aiuta anche chi non sa ancora cosa sia possibile
fare nel proprio dominio. Nel secondo, parte da un contesto più definito. Il
risultato cercato è lo stesso: una struttura operativa posseduta dal progetto,
capace di orientare il lavoro e di evolvere senza perdere il perché delle
decisioni.

## Che cosa contiene

- un Project Kernel generato e pronto a essere specificato nel contesto reale;
- un'intervista iniziale che trasforma problemi, attività e possibilità in un
  primo orientamento correggibile;
- stato di configurazione, brief e punto di ripresa del progetto;
- una meta-facoltà che seleziona e compone le capacità pertinenti;
- un contratto evolutivo che distingue memoria di caso, competenza, skill,
  funzione e meta-evoluzione;
- ingressi e guide per Codex, Claude Code, OpenCode, Hermes e DeepSeek
  Harness (DSH);
- una proiezione lifecycle opzionale per Codex, con controllo dei conflitti,
  inclusa ma non installata né attivata;
- ricevute iniziali che distinguono ciò che è incluso da ciò che è stato
  realmente rilevato e attivato sull'host.

La presenza di una guida non equivale a compatibilità già provata in ogni
versione dell'host. Le condizioni correnti sono descritte in
[`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md).

## Evoluzione recente

La versione `1.5.0` aggiunge una proiezione nativa per DSH: la cartella estratta
è il project root DSH, `AGENTS.md` è l'ingresso e le skill portabili restano in
`.agents/skills/`. Non richiede plugin, provider, modello, hook o configurazione
globale DSH. L'adattatore è incluso, ma una prova su un host DSH appena avviato
resta necessaria prima di dichiararne l'attivazione comportamentale. La
proiezione lifecycle Codex introdotta nella versione `1.4.0` rimane opzionale e
indipendente.

La cronologia completa e verificabile è in [`CHANGELOG.md`](CHANGELOG.md).

## Project Kernel e RepoKernel non sono la stessa cosa

**RepoKernel** è il metakernel generativo privato che compila strutture di
progetto. **MAIOS Project Kernel** è il risultato distribuibile: il progetto lo
riceve, lo usa, lo possiede e può farlo evolvere.

Questa repository non contiene né concede in licenza il sorgente di RepoKernel.
Contiene il Project Kernel generato, i suoi adattatori, le facoltà locali e la
documentazione necessaria per usarlo. La separazione completa è descritta in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Stati che non vanno confusi

```text
generato -> incluso nel pacchetto
scaricato -> acquisito dalla persona
estratto -> presente nella nuova cartella
configurato -> specificato insieme alla persona
rilevato -> visto dall'assistente o dall'host
attivato -> provato nel contesto reale
```

Uno stato non implica automaticamente il successivo. Questa distinzione evita
che la sola presenza dei file venga scambiata per una capacità operativa già
verificata.

## Privacy e autorità

La configurazione è locale al progetto. Il pacchetto non installa servizi, non
invia dati, non pubblica contenuti e non abilita integrazioni esterne da solo.
Ogni effetto esterno resta soggetto all'autorizzazione richiesta dall'ambiente
e dalla persona.

## Verifica e sviluppo

```powershell
python tools/verify_distribution.py
python tools/build_release.py
```

Il primo comando controlla struttura, manifest, percorsi e confine RepoKernel.
Il secondo genera uno ZIP riproducibile in `dist/` e stampa il relativo
SHA-256. La provenienza della release è documentata in
[`docs/PROVENANCE.md`](docs/PROVENANCE.md).

## Stato del progetto

- Versione del pacchetto: `1.5.0`
- Proiezione lifecycle opzionale per Codex: inclusa, non installata
- Adattatore host DSH: incluso; comportamento su host nuovo non ancora attestato
- Modalità: configurazione differita tramite intervista iniziale
- Target: nuova cartella / nuovo repository
- Installazione in repository esistenti: non supportata in questa release
- Sorgente RepoKernel: non incluso

Consulta anche [Setup AI](https://maios.it/setup-ai.html) e
[l'Ecosistema MAIOS](https://maios.it/atlas-it.html).

## Repository collegate

- [`d-nd-seed`](https://github.com/GrazianoGuiducci/d-nd-seed) fornisce i
  registri pubblici di capacità e facoltà usati come riferimenti pinned e
  `data_only` nella generazione.
- [`d-nd-ux-ai-seed`](https://github.com/GrazianoGuiducci/d-nd-ux-ai-seed)
  raccoglie i contratti pubblici di comportamento UX per workspace agentici;
  è una superficie collegata dell'ecosistema, non codice incluso nel pacchetto.
- **RepoKernel** genera il Project Kernel, ma rimane un prodotto privato: il suo
  repository non è collegato né distribuito qui.

Il ruolo e i termini di ciascuna fonte sono dettagliati in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) e
[`docs/PROVENANCE.md`](docs/PROVENANCE.md).

## Licenza

Il contenuto di questa repository, esclusi nomi e marchi, è distribuito con
licenza [MIT](LICENSE). RepoKernel resta escluso. Le fonti informative e i
relativi termini sono indicati in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md); i nomi e i segni distintivi
sono trattati in [`TRADEMARKS.md`](TRADEMARKS.md).
