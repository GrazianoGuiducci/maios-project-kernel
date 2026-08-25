# MAIOS Project Kernel

MAIOS Project Kernel è un sistema di progetto portabile e auto-installante per
persone che lavorano con assistenti AI. Parte dalla situazione e dalle fonti
reali della persona, forma presto un risultato correggibile, compone soltanto le
facoltà che cambiano il movimento presente e conserva nel progetto
l'apprendimento revisionato e il rientro.

La versione `2.0.0` è pubblicata sul ramo `main` della repository. Il suo
archivio auto-installante è disponibile su
[maios.it](https://maios.it/downloads/maios-project-kernel-setup-v2.0.0.zip),
insieme al [checksum SHA-256](https://maios.it/downloads/maios-project-kernel-setup-v2.0.0.zip.sha256).
Non è stato creato un tag o una Release GitHub.

Questa versione è una base, non un limite: nuove competenze, nuovi host e nuove
forme di incarnazione potranno entrare quando le circostanze future renderanno
utili le loro relazioni, senza trasformare l'architettura attuale in
un'ontologia fissa.

## Relazione sorgente-pacchetto

La repository è il sistema sorgente vivo. `package/` e lo ZIP sono proiezioni
generate deterministicamente:

```text
sorgenti vive, contratti e prove
-> pacchetto generato e inventario
-> archivio auto-installante
-> piano esatto e ricevuta
-> progetto installato
-> prove separate di discovery, uso, risultato e rientro mantenuto
```

La 2.0.0 comprende:

- kernel semantico source-bound e orizzonte aperto;
- campo causale aperto delle facoltà e composizione situata;
- configuratore MAIOS con unico stato canonico, Context Capsule e SetupSpec
  collegati per hash, proiezioni leggibili, controllo di concorrenza e recupero;
- contesto operativo autologico che espone relazioni di capacità, invalidazioni
  causali, incertezze e autorità correnti senza dichiarare correttezza semantica
  o attivazione;
- readback terminale revisionato che collega risultato reale, impatto sulle
  possibilità, movimento successivo e valutazioni di miglioramento governate
  dal proprietario a configurazione e rientro;
- coltivazione reciproca delle competenze: il lavoro concreto mette alla prova
  la competenza che lo rende possibile, il readback la migliora e il delta
  revisionato cambia i movimenti successivi;
- installer deterministico con `preview`, `apply`, `verify` e `uninstall`, anche
  per repository esistenti senza sovrascritture nascoste;
- adapter locali per Codex, Claude Code, OpenCode, DSH, Hermes e host generico;
- distinzione fra generato, pacchettizzato, installato, scoperto, usato,
  verificato e mantenuto.

## Costruzione

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest discover -s tests -v
python -B tools\build_release.py
python -B tools\verify_distribution.py
```

## Installazione

Dopo aver estratto lo ZIP in una cartella temporanea di distribuzione:

```powershell
python install.py preview --target C:\Projects\MioProgetto --mode new_repository --host codex --plan-out install-plan.json
python install.py apply --plan install-plan.json
```

L'installazione non parte da sola e non cambia configurazioni globali, hook,
plugin, credenziali o altri progetti. Per una repository esistente usare
`existing_repository`: un conflitto divergente blocca il piano.

Questa repository possiede l'ingresso manuale `self_configuring`. Non importa
stato o risposte del Form MAIOS; quel percorso verrà confrontato soltanto dopo
la chiusura autonoma della verticale manuale 2.0.0.

Consulta [installazione](docs/INSTALLATION.md),
[architettura](docs/ARCHITECTURE.md) e
[compatibilità host](docs/COMPATIBILITY.md).
