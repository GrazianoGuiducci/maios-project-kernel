# Contratto del setup autoconfigurante

Questo Project Kernel entra in configurazione prima di iniziare il lavoro.

## Risultato della configurazione

L'intervista deve rendere sufficientemente chiari:

- il contesto e il punto di vista da cui il progetto viene affrontato;
- l'attivita concreta su cui operare;
- il primo risultato osservabile;
- chi usera, configura e verifica il risultato;
- dati, fonti, strumenti e ambiente disponibili;
- criteri di riuscita, responsabilita e questioni ancora aperte.

Questa risultante viene conservata in `situated_configuration` dentro
`setup/CONFIGURATION_STATE.json`, distinguendo:

- fatti, ipotesi, informazioni mancanti e relazioni non ancora rappresentabili;
- possibilita con ragione, stato, fonti, prova minima, invalidatore e condizione
  di riesame;
- direzione selezionata, sua ragione e revisione dell'owner;
- cio che deve fare il sistema, cio che resta alla persona e cio che deve
  cambiare nel lavoro;
- ipotesi correggibile di prodotto o servizio: bisogno affrontato, persona che
  ne beneficia, meccanismo di valore e piu piccolo risultato consegnabile;
- prima prova falsificabile ed eventuale autorita sull'effetto esatto.

Quando questi elementi permettono una prima azione utile:

1. aggiorna `setup/CONFIGURATION_STATE.json`;
2. completa `project/PROJECT_BRIEF.md`;
3. aggiorna `project/CURRENT_STATE.md` e il punto di ripresa RepoKernel;
4. usa la meta-facolta semantica generata come unico ingresso di orientamento e
   consolida la sua risultante nello stato strutturato;
5. componi o crea soltanto le competenze che cambiano davvero il comportamento;
6. indica il primo movimento verificabile e cio che resta da chiarire.

## Ciclo evolutivo del Package Kernel

`kernel/PROJECT_EVOLUTION_CONTRACT.json` definisce BootCapsule,
cristallizzazione e granularita dei delta. Lo stato resta in
`setup/CONFIGURATION_STATE.json`; il contratto non introduce un secondo owner.

Dopo un risultato o una correzione che cambia il lavoro futuro:

1. ispeziona il risultante rispetto a intento, fonti e criteri;
2. classifica il delta come stato del caso, memoria, competenza, skill candidata,
   funzione candidata o meta-evoluzione;
3. ottieni la review dell'owner per ogni candidato che cambia comportamento;
4. conserva fonte, prova, riesame, confine e residuo da non seguire;
5. aggiorna la BootCapsule e la proiezione di reentry senza salvare il dialogo.

## Regole operative

- Usa prima le fonti gia presenti nel progetto e distingui fatti, ipotesi e
  informazioni mancanti.
- Fai una domanda soltanto quando la risposta cambia il risultato, il percorso,
  una competenza, una responsabilita o un'azione possibile.
- Dopo il primo contributo sostanziale mostra una prima interpretazione e una
  possibilita concreta. Entro il secondo presenta una sintesi completa,
  l'ipotesi di prodotto o servizio e la prova falsificabile; non aprire un altro
  ciclo esplorativo per ignoti che possono restare espliciti.
- Una domanda ulteriore e ammessa soltanto se un fatto mancante renderebbe la
  proposta infedele, non falsificabile o non sicura; dichiara perche cambia il
  risultato. Questa regola limita la latenza, non l'orizzonte cognitivo.
- Adatta le domande alle risposte precedenti; non ripetere cio che e gia noto.
- Mantieni aperte le possibilita non ancora decidibili senza trasformarle in
  funzioni attive o promesse.
- Una relazione utile che non entra ancora nella struttura corrente resta
  esplicita come `retained_unknown`; non va forzata ne eliminata.
- Le competenze sono facolta operative. Devono avere trigger, fonti, risultato,
  limite, verifica e regola di evoluzione.
- Una lacuna materiale produce prima un candidato in `skills/`; l'owner del
  progetto lo accetta, corregge o rifiuta prima che un host lo consideri attivo.
- Una competenza accettata conserva versione, prova, condizione di riesame e
  stato di eventuale supersessione.
- Adatta il linguaggio alla persona e non trasferire su di lei scelte tecniche
  che possono essere dedotte dal contesto o affrontate più avanti.
- Dopo ogni risposta che cambia il progetto, salva un checkpoint minimo in
  `setup/CONFIGURATION_STATE.json`; non conservare la trascrizione come stato.
- Una possibilita non e un elenco promozionale: conserva la ragione per cui e
  pertinente, cosa la smentisce, la prova piu piccola e quando riesaminarla.
- La direzione selezionata resta candidata finche la persona responsabile non
  la accetta o corregge; non confondere convergenza semantica e accettazione.
- Una richiesta di abbreviare, fermare le domande, cambiare ritmo o ricevere
  una sintesi corregge l'esperienza del dialogo e non vale come review della
  direzione, dell'ipotesi o della prova. In sua assenza conserva
  `owner_review: pending` e `setup_status: in_progress`.
- L'ipotesi di prodotto o servizio non obbliga una forma commerciale o
  tecnologica: puo essere un metodo, un artefatto di ricerca, un flusso, un
  servizio professionale o software quando e questa la forma che risolve il
  bisogno. La persona puo correggerla in linguaggio naturale.
- `effect_authority` resta `none` durante la configurazione. Un effetto esterno
  richiede un gate distinto anche quando la direzione e stata accettata.
- Correzioni ed esperienza aggiornano una competenza solo quando producono una
  differenza riutilizzabile e verificata.
- Non promuovere automaticamente un delta: un fatto del caso resta nello stato,
  una funzione richiede comportamento deterministico e test, una skill richiede
  un metodo delimitato, una meta-evoluzione richiede un owner distinto per ogni
  eventuale proiezione.
- Generato non significa installato, attivo o autorizzato.
- Nessun push, deploy, invio, acquisto, cancellazione o modifica esterna senza
  un effetto esatto e una decisione esplicita.

## Chiusura dell'intervista

Non serve conoscere tutto. L'intervista termina quando esistono un caso reale,
un primo risultato verificabile, un responsabile riconoscibile e una prima
mossa coerente. Le informazioni mancanti diventano domande operative delle
fasi iniziali, non un blocco artificiale.

La prima risultante viene mostrata entro il secondo contributo sostanziale in
quattro blocchi brevi: cosa e stato compreso, proposta, prima prova e scelta
`correggi | procediamo | lascia in sospeso`. Solo l'ultima scelta, riferita al
contenuto, puo chiudere la review semantica.

## Stato dell'archivio e stato del progetto

`MANIFEST.json`, `HOST_ADAPTERS.json`, `COMPONENT_MATRIX.json` e le ricevute
incluse descrivono il pacchetto nel momento della consegna. Sono una baseline e
non devono essere usati come stato corrente dopo l'avvio.

Lo stato strutturato autorevole appartiene a `setup/CONFIGURATION_STATE.json`;
`project/CURRENT_STATE.md` ne e la proiezione umana concisa per la ripresa e le
ricevute conservano le prove dell'host reale. Non creare un secondo proprietario
dello stato semantico. Perciò
`pending_host_open` nel manifesto resta una proprietà della copia distribuita
anche quando il progetto estratto è già in configurazione o configurato.
