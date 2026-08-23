# Pacchetto Setup AI autoconfigurante

Questo pacchetto prepara un nuovo progetto insieme all'assistente. Non devi
decidere in anticipo l'architettura o conoscere il linguaggio dell'AI: parti dal
lavoro reale, correggi ciò che l'assistente comprende e arrivate insieme al
primo risultato utile.

## Avvio

1. Crea una cartella nuova e vuota con il nome del progetto.
2. Estrai tutto il contenuto dello ZIP dentro quella cartella.
3. Apri la cartella appena creata nell'host scelto. Per DSH segui
   `DSH_SETUP.md`; per Codex segui `CODEX_SETUP.md`; per gli altri host usa la
   relativa guida indicata in `HOST_ADAPTERS.json`.
4. Scrivi: `Leggi START_HERE.md e iniziamo la configurazione.`

L'assistente osserva la cartella, ti restituisce ciò che ha compreso e comincia con
la sola domanda che serve per orientare il progetto. Se non sai ancora cosa
costruire, descrivi semplicemente il lavoro, il problema o il risultato che ti
interessa: sarà l'assistente a proporre un primo punto di partenza correggibile.

Dal bisogno emerso l'assistente prepara con te un'ipotesi concreta di prodotto
o servizio e una prova minima. Non significa necessariamente creare software o
vendere qualcosa: puo essere anche un metodo, un artefatto di ricerca, un flusso
di lavoro o uno strumento. Prima di consolidarla ti mostra per chi e utile,
quale cambiamento dovrebbe produrre e come potreste accorgervi che l'ipotesi e
sbagliata.

Questa versione avvia un progetto nuovo. Non estrarla sopra un repository gia
esistente: l'integrazione in un progetto esistente richiede un percorso di
merge separato.

Le istruzioni specifiche per Codex sono in `CODEX_SETUP.md`. Sono presenti
anche ingressi equivalenti per Claude Code, OpenCode, Hermes e DeepSeek Harness
(`DSH_SETUP.md`). In DSH la cartella estratta deve essere il project root
effettivo, non una sottocartella di un repository padre. Se un assistente
non legge automaticamente la cartella, incolla il testo di
`START_WITH_YOUR_ASSISTANT.txt`.

L'assistente osserva prima ciò che esiste, raccoglie soltanto il contesto che
cambia il progetto, rende specifico il Project Kernel, compone le competenze
pertinenti e prepara un primo risultato concreto con il suo punto di ripresa.
Le informazioni potranno essere corrette in qualsiasi momento.

La configurazione viene conservata in `setup/CONFIGURATION_STATE.json`,
`project/PROJECT_BRIEF.md` e `project/CURRENT_STATE.md`. Le facoltà operative
sono orientate dalla meta-facolta generata, raggiungibile con
`operate-maios-project-kernel`, e governate da `kernel/MAIOS_START_KERNEL.md`; la skill
`maios-project-faculty-router` seleziona e compone quelle disponibili. Una
competenza nuova viene preparata soltanto quando la composizione non chiude un
bisogno reale e verificabile.

Quando il progetto impara da un risultato o da una correzione, il contratto
`kernel/PROJECT_EVOLUTION_CONTRACT.json` distingue cio che resta nel caso da un
delta di memoria, competenza, skill, funzione o meta-evoluzione. Viene
conservato soltanto cio che cambia il lavoro futuro e che ha ricevuto la review
necessaria.

Il pacchetto contiene un Project Kernel generato da RepoKernel, senza il suo
codice sorgente. La configurazione non installa servizi, non pubblica contenuti
e non attiva integrazioni esterne.

## Adattatore lifecycle opzionale per Codex

Il Project Kernel e le sue metacompetenze funzionano anche senza hook. Per
Codex il pacchetto include inoltre, in `.repokernel/lifecycle/`, un adattatore
consigliato quando il modello e l'host ne traggono beneficio. È incluso ma non
installato: l'estrazione dello ZIP non crea `.codex/` e non modifica la
configurazione dell'app.

Prima di usarlo leggi `.repokernel/lifecycle/INSTALL.md` ed esegui il controllo
senza scritture indicato lì. L'installazione richiede una scelta esplicita del
proprietario del progetto; il pacchetto conserva anche ricevuta e procedura di
rimozione. Disattivarlo o rimuoverlo resta una possibilità di recupero, non il
centro del setup.
