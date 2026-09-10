# MAIOS Project Kernel

MAIOS Project Kernel dà a un progetto e al suo agente AI di sviluppo un kernel
operativo condiviso: conoscenza e metodi per comprendere la situazione, svolgere
lavoro utile, sviluppare competenze e continuare mentre il progetto cambia.

Il progetto conserva le ragioni delle decisioni, le fonti che le sostengono e
il sapere acquisito nel lavoro. Un'altra istanza può recuperare quel contesto
e proseguire senza attribuirsi l'esperienza della precedente come memoria personale.

Versione del prodotto: **[4.1.0](VERSION.md)** · Famiglia Project Kernel: **3.0.0** ·
Python **3.10 o successivo** · [Licenza MIT](LICENSE)

[English](README.md)

## Cosa rende possibile

- Comprendere un progetto nuovo o esistente attraverso fonti reali, intento,
  vincoli e possibilità aperte.
- Raggiungere, comporre o formare le competenze utili al lavoro. Intento,
  conoscenza, risultati riusciti e nuove possibilità possono cambiare ciò che
  vale la pena sviluppare; apprendere non richiede prima un errore.
- Collegare ragioni, decisioni e conseguenze, riportando l'apprendimento
  riusabile nei metodi che devono cambiare.
- Continuare fra sessioni e agenti che collaborano attraverso il sapere del
  progetto, preservando il lavoro corrente e le ragioni della sua direzione.

KA mantiene aperto il campo delle possibilità; FDLA corregge le distorsioni
mentre il lavoro prende forma; Meta_Skill riconosce, compone e sviluppa
competenze. Queste funzioni agiscono insieme attraverso l'agente e le fonti
del progetto. Il [compendio del Kernel](knowledge/KERNEL.md) ne spiega
significato e funzionamento.

## Inizia dal tuo progetto

Clona o scarica questa repository e apri la cartella [`package/`](package/)
con il tuo coder AI. La distribuzione installabile è già inclusa;
costruirla dalla sorgente è facoltativo. Chiedi al coder:

```text
Leggi AGENTS.md e usa maios-project-integration. Voglio usare MAIOS in
[progetto destinatario]. Comprendi il progetto e il mio intento attuale,
spiega il contributo utile che puoi dare e mostrami le modifiche previste
dall'installazione e il recupero prima di applicarle. Usa ciò che è già chiaro;
chiedi soltanto le informazioni mancanti che cambiano l'integrazione.
```

Aprire la cartella non installa nulla. Il coder identifica progetto e host,
prepara i requisiti mancanti, mostra le modifiche esatte e applica il piano
accettato. Dopo l'installazione, apri il progetto destinatario, chiedigli di
leggere `START_HERE.md` e prosegui con il lavoro reale.

**Progetto nuovo:** l'installer accetta una destinazione assente o vuota.
Il coder forma il contesto condiviso sufficiente per iniziare un lavoro utile
e lo sviluppa durante il percorso.

**Progetto esistente:** il coder legge istruzioni, fonti e lavoro presenti.
L'installer conserva i file identici, aggiunge quelli mancanti e segnala i
contenuti in conflitto perché siano riconciliati esplicitamente.

Installer e strumenti locali richiedono Python 3.10 o successivo e nessun
pacchetto Python di terze parti. La guida di
[installazione e recupero](docs/INSTALLATION.md) descrive comandi di
anteprima/applicazione, conflitti e disinstallazione; la
[guida d'uso](docs/USAGE.it.md) approfondisce integrazione, competenze e lavoro quotidiano.

## Lavorare, apprendere e rientrare

L'agente installato usa il contesto del progetto e le competenze pertinenti
per formare un risultato. Nuova conoscenza, un approccio riuscito, una
possibilità o una correzione possono cambiare i metodi usati in seguito.
Il progetto conserva le ragioni utili e il punto da cui continuare, senza
richiedere di rileggere l'intera conversazione.

`START_HERE.md` è l'ingresso stabile. I corpi vivi delle competenze possiedono
i metodi; stato e conoscenza del progetto portano il contesto che cambia.
Gli strumenti locali comprendono `status`, `configuration-status`,
`competence-status`, `learning-status` e `operating-status`; la
[guida d'uso](docs/USAGE.it.md#funzionamento-locale-al-progetto) mostra come richiamarli.

Aggiornare un pacchetto è distinto dall'evolvere il sapere di un progetto.
Riapplicare lo stesso artefatto a un'installazione invariata è idempotente;
una versione diversa non produce una migrazione automatica. Il
[metodo di continuità degli aggiornamenti](kernel/UPDATE_CONTINUITY.md)
collega la base d'installazione, l'evoluzione locale e una proposta di aggiornamento.

## Host ed evidenze

Il pacchetto offre profili per `codex`, `claude`, `opencode`, `hermes`,
`openclaw`, `pi`, `dsh` e `generic`. La
[guida di compatibilità](docs/COMPATIBILITY.md) identifica percorsi installati
e condizioni di riconoscimento. La presenza di un profilo non dimostra l'uso
osservato da parte di ogni host o modello.

Test sorgente e verifica della distribuzione coprono integrità del pacchetto,
meccaniche di installazione e recupero, instradamento e contratti dello stato
locale. Non dimostrano che il modello destinatario comprenda, usi o assimili
i metodi. Le [evidenze della 4.1.0](docs/RELEASE_4.1.0_EVIDENCE.md) conservano
le osservazioni datate; le [note di release](docs/RELEASE_4.1.0.md) ne spiegano
le novità.

## Studiare, contribuire o costruire

Puoi studiare e migliorare la sorgente pubblica senza installare il pacchetto.
Apri la radice della repository con il coder e chiedigli di leggere `AGENTS.md`
e usare `maios-kernel-study`. Persone e modelli AI possono contribuire metodi,
conoscenza, domande, evidenze e codice attraverso la
[guida ai contributi](CONTRIBUTING.md).
La competenza [maios-kernel-contribution](skills/maios-kernel-contribution/SKILL.md)
aiuta a trasformare quel lavoro in un contributo fondato sulle sue fonti.

| Prossimo passo | Documentazione |
| --- | --- |
| Usare e mantenere un progetto | [Uso](docs/USAGE.it.md) · [Installazione](docs/INSTALLATION.md) |
| Comprendere il Kernel | [Conoscenza](knowledge/KERNEL.md) · [Architettura](docs/ARCHITECTURE.md) |
| Lavorare sulla repository | [Mappa documentale](docs/README.md) · [Build](docs/GENERATED_KERNEL_BUILD.md) · [Provenienza](docs/PROVENANCE.md) |
| Esplorare la ricerca | [System Semantic Kernel working paper](https://github.com/GrazianoGuiducci/maios-ssk-paper), corpus accademico distinto |
| Seguire le modifiche | [Changelog](CHANGELOG.md) · [Stato sorgente corrente](CURRENT_STATE.md) |

La repository possiede la sorgente del prodotto. `package/` è la distribuzione
installabile generata; le modifiche si fanno nei file sorgente che la producono.

Software e documentazione sono sotto [licenza MIT](LICENSE). Consulta le
[note di terze parti](THIRD_PARTY_NOTICES.md) e le [indicazioni su nomi e marchi](TRADEMARKS.md).
