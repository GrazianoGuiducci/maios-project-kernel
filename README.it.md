# MAIOS Project Kernel

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
  inclusa ma non installata né attivata.

Gli ingressi specifici per ogni ambiente sono riepilogati in
[`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md).

## Evoluzione recente

La versione `1.6.0` distingue il potenziale della competenza, la rilevanza
emergente, l'uso realizzato e il miglioramento verificato. Aggiunge inoltre un
ciclo aziendale supervisionato e reversibile e rende licenza, notice e
provenienza direttamente ispezionabili nel pacchetto. L'attivazione dell'host
e la proiezione lifecycle opzionale per Codex restano separate dall'estrazione.

La cronologia delle versioni è in [`CHANGELOG.md`](CHANGELOG.md).

## Stato del progetto

- Versione del pacchetto: `1.6.0`
- Proiezione lifecycle opzionale per Codex: inclusa, non installata
- Modalità: configurazione differita tramite intervista iniziale
- Target: nuova cartella / nuovo repository
- Installazione in repository esistenti: non supportata in questa release

Consulta anche [Setup AI](https://maios.it/setup-ai.html) e
[l'Ecosistema MAIOS](https://maios.it/atlas-it.html).

## Repository collegate

- [`d-nd-seed`](https://github.com/GrazianoGuiducci/d-nd-seed) fornisce i
  registri pubblici di capacità e facoltà usati come riferimenti pinned e
  `data_only` nella generazione.
- [`d-nd-ux-ai-seed`](https://github.com/GrazianoGuiducci/d-nd-ux-ai-seed)
  raccoglie i contratti pubblici di comportamento UX per workspace agentici;
  è una superficie collegata dell'ecosistema, non codice incluso nel pacchetto.

Il ruolo e i termini delle fonti incluse sono dettagliati in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) e
[`docs/PROVENANCE.md`](docs/PROVENANCE.md).

## Licenza

Il contenuto di questa repository, esclusi nomi e marchi, è distribuito con
licenza [MIT](LICENSE). Le fonti informative e i relativi termini sono indicati in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md); i nomi e i segni distintivi
sono trattati in [`TRADEMARKS.md`](TRADEMARKS.md).
