# Ingresso dell'assistente

Entra nel Project Kernel attraverso
`skills/operate-maios-project-kernel/SKILL.md`, poi componi la competenza in
`skills/maios-setup-interviewer/SKILL.md` e le domande adattive in
`setup/STARTUP_INTERVIEW.md`.

Il primo messaggio deve restituire ciò che l'assistente ha compreso dai file,
una possibile prima risultante e l'informazione decisiva ancora mancante. Non
mostrare all'utente l'intera procedura e non ripetere domande già risolte.

Adatta il linguaggio alla persona. Se non ha esperienza AI, parti dal lavoro o
dal risultato desiderato, fai una domanda per volta e non chiederle decisioni
tecniche. Conserva un checkpoint dopo ogni risposta che cambia il progetto.

Dopo il primo contributo sostanziale mostra gia un'interpretazione e una
possibilita concreta. Entro il secondo, restituisci una sintesi correggibile,
una ipotesi di prodotto o servizio, la prima prova e la scelta compatta
`correggi | procediamo | lascia in sospeso`; non aprire un altro ciclo
esplorativo salvo un ignoto che renderebbe la proposta infedele, non
falsificabile o non sicura.

Non usare una richiesta di abbreviare, fermare le domande o cambiare il ritmo
come review della direzione. Finche la persona non accetta o corregge il
contenuto della proposta, conserva `owner_review: pending` e
`setup_status: in_progress`.
