# Avvio con Codex

1. Estrai lo ZIP in una cartella nuova e vuota.
2. Apri Codex e scegli **Apri cartella**.
3. Seleziona la cartella estratta, non il file ZIP.
4. Scrivi: `Leggi START_HERE.md e iniziamo la configurazione.`

Non serve preparare un prompt tecnico. Codex legge `AGENTS.md`, trova le
competenze incluse, entra nel Project Kernel attraverso
`.agents/skills/operate-maios-project-kernel/SKILL.md` e conduce l'intervista
partendo dal lavoro che descrivi.
Puoi interrompere e riprendere: dopo ogni risposta significativa lo stato del
progetto viene salvato nella cartella.

Il Project Kernel e le metacompetenze sono già utilizzabili senza hook. Il
pacchetto contiene anche l'adattatore lifecycle opzionale in
`.repokernel/lifecycle/`; leggi `INSTALL.md` in quella cartella e usa prima il
comando `--check`. Nessun file `.codex/` viene installato automaticamente.

ChatGPT nel browser non legge automaticamente la cartella: allega almeno
`START_WITH_YOUR_ASSISTANT.txt`, `AGENTS.md`, `START_HERE.md`,
`project/CURRENT_STATE.md` e i file del progetto necessari al contesto.
