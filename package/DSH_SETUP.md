# Ingresso DeepSeek Harness (DSH)

DSH è il substrato esecutivo di questo progetto. Non è MAIOS, TM13,
RepoKernel o il Project Kernel. Questo pacchetto non trasferisce identità,
sessioni, provider, credenziali o configurazioni DSH private.

## Apri il project root corretto

1. Estrai lo ZIP in una cartella nuova, preferibilmente fuori da un repository
   Git padre, oppure rendi la cartella estratta un Git root autonomo.
2. Avvia DSH usando la cartella estratta come directory di lavoro del progetto.
3. Usa il preset `standard`. `code` e `cordis` sono candidati compatibili;
   `minimal` non include la discovery delle skill richiesta dal pacchetto.
4. Scrivi: `Leggi START_HERE.md e iniziamo la configurazione.`

In DSH 0.1.1-rc.1 il project root effettivo viene risolto attraverso il marker
`.git` più vicino. Se il pacchetto è soltanto una sottocartella di un repository
padre, DSH può caricare `AGENTS.md` ma cercare `.agents/skills` nel repository
padre. In quel caso la discovery nativa delle skill non è dimostrata finché il
project root non viene corretto.

DSH legge `AGENTS.md` e può leggere anche `CLAUDE.md` come istruzioni di
progetto. Le skill native sono in `.agents/skills`: usa
`operate-maios-project-kernel` come unico ingresso alla meta-facoltà del
Project Kernel, `maios-setup-interviewer` per configurare il caso insieme alla
persona e `maios-project-faculty-router` soltanto quando la composizione delle
facoltà cambia il risultato. I percorsi `.claude/skills` valgono per Claude
Code, non per DSH.

Il setup parte da `setup_status: pending`: osserva il progetto, restituisci una
prima comprensione correggibile e usa l'intervistatore soltanto per gli ignoti
che cambiano la direzione o la prima prova. La prima risultante deve emergere
entro il secondo contributo sostanziale della persona.

## Evidenza separata

`packaged` -> `opened` -> `instructions_discovered` -> `skills_discovered` ->
`kernel_composed` -> `exercised` -> `maintained`.

La presenza dei file prova soltanto `packaged`; la discovery non prova la
composizione; la composizione non prova l'uso; l'uso in una sessione non prova
la reentry mantenuta. Aggiorna `receipts/host-activation/dsh.json` soltanto con
evidenza osservata in una sessione DSH fresca.

Questo adattatore non installa profili, plugin, provider o modelli DSH, non
modifica configurazioni globali, non abilita hook e non concede autorità su
effetti esterni. La baseline verificata è DSH 0.1.1-rc.1; versioni successive
richiedono una nuova prova di project root, istruzioni e discovery delle skill.
