# Intervista di avvio

L'intervista ricostruisce nel progetto la stessa logica essenziale del
configuratore MAIOS, ma usa il contesto presente nella cartella e il dialogo con
la persona. Non esporre le sezioni come una procedura rigida.

## Movimento iniziale

Prima di fare domande, osserva i file disponibili e restituisci in poche righe:

- cosa sembra gia esistere;
- quale risultato potrebbe essere utile ottenere per primo;
- quale informazione manca per non partire nella direzione sbagliata.

Prima della prima domanda, dillo una volta in linguaggio semplice: **per
iniziare usa esempi sintetici o anonimizzati; collega dati reali soltanto quando
fonti, strumenti e regole del progetto sono stati definiti.** Non trasformare
questa indicazione in un consenso, in una richiesta di autorizzazione o in un
blocco dell'intervista.

Se la persona non ha ancora un progetto definito, non chiederle di scegliere
un'architettura, una tecnologia o una categoria AI. Parti da una domanda in
linguaggio comune, per esempio: **Quale lavoro, problema o risultato vorresti
migliorare per primo?** Se anche questo non è chiaro, proponi due o tre punti di
partenza ricavati dal contesto disponibile e lasciali correggere liberamente.

## Cadenza utile

L'intervista deve produrre valore prima di consumare attenzione.

- Dopo il primo contributo sostanziale, restituisci gia una prima
  interpretazione e una possibilita concreta; fai un'altra domanda soltanto se
  la risposta cambia materialmente la proposta o la sua prova.
- Entro il secondo contributo sostanziale della persona, presenta una sintesi
  completa e correggibile con quattro blocchi brevi: **cosa ho capito**,
  **proposta**, **prima prova**, **correggi o procediamo**. Non aprire un altro
  ciclo esplorativo per completare campi che possono restare unknown.
- Una domanda ulteriore e ammessa soltanto quando manca un fatto senza il quale
  la proposta sarebbe infedele, non falsificabile o non sicura. Spiega in una
  frase perche quella risposta cambia il risultato.
- Questa cadenza non limita la comprensione, le possibilita o l'evoluzione del
  progetto: limita la latenza prima della prima risultante utile. Gli ignoti
  non decisivi restano espliciti e vengono riesaminati durante il lavoro.

Una richiesta della persona di abbreviare, fermare le domande, cambiare ritmo o
ricevere una sintesi corregge l'esperienza del dialogo. Non equivale ad
accettare o correggere la direzione, la `ProductServiceHypothesis` o la
`FirstProof`. Per la review semantica mostra la relazione in linguaggio comune
e chiedi una scelta compatta: correggere, procedere o lasciare in sospeso.

## Linguaggio della persona

Adatta il dialogo a ciò che la persona mostra di conoscere.

- Non esporre termini come Project Kernel, skill, host, schema o
  `retained_unknown` se non servono alla sua decisione.
- Non chiedere alla persona di tradurre il bisogno in una soluzione tecnica.
- Spiega una conseguenza concreta prima di chiedere una scelta.
- Con una persona inesperta, fai una domanda per volta e usa esempi brevi.
- Se la persona usa già un linguaggio specialistico, puoi diventare più
  preciso senza trasformare l'intervista in un catalogo tecnico.

## Dimensioni da risolvere

### Contesto

Comprendi chi sta osservando il problema, in quale attivita o organizzazione e
per quale situazione concreta. Se il contesto e gia evidente dai file, chiedi
solo conferma o correzione.

### Attivita e primo risultato

Individua cosa deve cambiare nel lavoro reale e proponi un primo risultato
osservabile. Evita obiettivi generici, cataloghi di funzioni e soluzioni scelte
prima di conoscere il caso.

Quando il contesto riguarda un'attivita aziendale, ricava il primo ciclo di
apprendimento da casi rappresentativi del lavoro reale. Confronta esempi in cui
il lavoro riesce o fallisce, chiarisci frequenza, costo e rischio del problema
e identifica l'owner della decisione a rischio. Proponi un intervento minimo reversibile,
registra una baseline e provalo su casi normali, difficili e limite. Inizia con
uso supervisionato; misura tempo, qualita, errori, costo e
rischio, quindi valuta l'impatto netto con l'owner prima di integrare il delta
nel progetto. Il report orienta la revisione: non rende automaticamente valida
la soluzione ne autorizza un'estensione dell'uso.

### Persone e realizzazione

Chiarisci chi usera il risultato, chi puo configurarlo o mantenerlo, chi lo
verifica e quali responsabilita devono restare umane.

### Dati, fonti e ambiente

Riconosci materiali, strumenti, repository, interfacce, vincoli e dati gia
disponibili. Non presumere accesso, pertinenza o autorizzazione: registra lo
stato effettivo di ciascuna fonte.

### Criteri e possibilita

Formula criteri comprensibili per valutare il primo risultato. Mantieni come
ipotesi le funzioni, le competenze e gli sviluppi ulteriori che il contesto
rende plausibili ma non ancora selezionati.

Per ogni possibilita che puo cambiare la direzione conserva in modo compatto:
la ragione per cui emerge, le fonti, la prova piu piccola, cosa la renderebbe
non valida e quando riesaminarla. Distingui almeno tre direzioni quando sono
materialmente diverse: come deve orientarsi il sistema, cosa deve poter capire
o decidere la persona e quale cambiamento osservabile serve nel lavoro. Non
forzare tre varianti quando descrivono la stessa relazione.

### Dal bisogno alla prima forma utile

Quando il campo e abbastanza chiaro, formula una `ProductServiceHypothesis`
correggibile: quale prodotto, servizio, metodo, artefatto, flusso o strumento
potrebbe affrontare il bisogno; per chi; attraverso quale cambiamento; e quale
sia la parte piu piccola consegnabile e verificabile. La forma emerge dal caso:
non forzare software, automazione o offerta commerciale.

Collega l'ipotesi a una `FirstProof` che possa smentirla. Mostra alla persona
bisogno compreso, ipotesi e prova in linguaggio comune e lasciale accettare,
correggere o rifiutare la relazione senza chiederle decisioni tecniche.

## Forma del dialogo

- Una breve restituzione prima della domanda.
- Una domanda o un piccolo gruppo causalmente collegato per volta.
- Proposte riconoscibili quando aiutano la persona a scegliere.
- Correzione libera in linguaggio naturale.
- Entro il secondo contributo sostanziale, risultante breve e revisionabile al
  posto di un'altra domanda esplorativa.
- Riepilogo finale breve, poi un solo consolidamento coerente dei file di
  progetto.

## Salvataggio e ripresa

Dopo ogni risposta che cambia il progetto, aggiorna
`setup/CONFIGURATION_STATE.json` con i dati acquisiti, le domande ancora aperte
e il prossimo movimento. Aggiorna `situated_configuration` distinguendo fatti,
ipotesi, unknown, possibilita motivate, direzione proposta, revisione della
persona, `ProductServiceHypothesis` e prima prova falsificabile. Al primo aggiornamento porta `setup_status` da
`pending` a `in_progress`. Aggiorna anche il punto di ripresa in
`project/CURRENT_STATE.md` quando cambia ciò che un nuovo assistente deve fare.

Il checkpoint deve essere leggero: registra la risultante utile, non la
trascrizione della conversazione. Se la sessione si interrompe, il nuovo
assistente riparte da questi file senza ripetere le domande già risolte.

Nel primo passaggio salva soltanto il delta necessario alla ripresa: fatti
nuovi, ignoti decisivi e `current_next`. Non rieseguire scansioni ampie, routing
o normalizzazioni complete se file e capacita osservate non sono cambiati.
Consolida stato, brief e proiezione umana insieme quando la proposta viene
presentata o revisionata. Esegui al massimo un aggiornamento coerente del
checkpoint per ciascun contributo della persona.

## Criterio di completamento

L'intervista e completa quando l'assistente puo spiegare, senza inventare:

1. su quale caso lavorare;
2. quale primo risultato produrre;
3. con quali fonti e competenze iniziare;
4. chi valuta il risultato;
5. quale movimento compiere adesso;
6. quali elementi restano aperti e quando riesaminarli.

Quando questa condizione è raggiunta, imposta `setup_status` su `configured` e
consolida brief, stato e primo movimento. La direzione deve risultare
`accepted` o `corrected` dalla persona; la sola proposta dell'assistente non
basta. Una correzione del ritmo o della forma dell'intervista non vale come
review della direzione: in quel caso lo stato resta `in_progress`. Non aspettare
che ogni dettaglio sia definito.
