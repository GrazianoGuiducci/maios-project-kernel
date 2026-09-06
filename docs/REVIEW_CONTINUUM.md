# Lettura della candidata autonoma per ChatGPT

Questa repository contiene le sorgenti complete e il pacchetto generato della
candidata MAIOS Project Kernel `3.0.3+continuum.4`, derivata dalla release 3.0.3.
Il numero della prossima release pubblica resta aperto. Identifica il commit
esatto che riesci a leggere e usa sorgenti e `package/` di quella revisione:
una precedente lettura della repository o della release 3.0.3 non descrive
questa candidata. Se l'accesso restituisce una revisione precedente, rendi
esplicita la differenza prima di attribuirle le modifiche qui descritte.

Questa revisione risponde alle due recensioni della candidata continuum.3,
commit `cd744e257881c13ad1ff8c0619a835154aa5be90`. Il nuovo delta riguarda il
recupero: PENDING v3 conserva il piano originario e distingue mappe pianificate
da creazioni effettive. Il giornale completo viene validato prima di cancellare;
identità del file e hash devono corrispondere alla creazione registrata. File
incerti, anche identici, restano con il giornale. Backup e giornale hanno
creazione esclusiva; un tentativo non acquisito non viene ripulito. Dopo il
commit della ricevuta finale il recupero conserva l'installazione e termina
soltanto la pulizia del giornale. Le precedenti correzioni rimangono implementate.
Le regressioni seguono questi percorsi; non serve ricominciare una revisione generale.

Parti da [CURRENT_STATE.md](../CURRENT_STATE.md), quindi dalle competenze e dalle
sorgenti che cambiano la comprensione. L'intento è trasferire il potenziale del
kernel in un pacchetto autoconfigurante che lavori attraverso competenze
istruite: fonti vive di conoscenza, ragioni e metodo, capaci di apprendere
dai risultati e mantenere presenza nel continuum in modo sostenibile.

Comprendi il risultato e lascia che eventuali scoperte cambino anche la
domanda iniziale. Considera se formazione, contesto-intento, risalita delle
ragioni, critica del proprio metodo e continuazione possano davvero agire
attraverso gli ingressi e i consumatori presenti. Segui il sapere fino al
prossimo uso, distinguendo un corpo aggiornato, la registrazione di un
apprendimento e il comportamento effettivamente osservato.

Segnala differenze materiali con la sorgente e il loro primo punto causale,
possibilità perse o aperte, correzione utile e relativo motivo. Non dedurre un
meccanismo assente dal solo nome di un file, né completezza dalla sola presenza
delle istruzioni. Le forme e gli esempi non devono diventare limiti delle
possibilità. I fondamenti D-ND rimangono il riferimento fuori dalla riscrittura
automatica; [FOUNDING_RELATIONS.md](../kernel/FOUNDING_RELATIONS.md) è la
rappresentazione qualificata A0-A11, non una pretesa di contenere tutto D-ND.

Sono passati tutti i 55 test locali, inclusi i sei casi di recupero mirati.
Il pacchetto ha 58 file, 47 nel payload, e corrisponde alla sorgente verificata.
Queste evidenze non provano ancora uso di un host/modello reale o assimilazione.
Non serve ripetere un programma di test: un ulteriore riscontro serve quando
risolve una differenza concreta emersa dalla lettura.

Le entrate chat, le Custom Instructions e la convergenza unificata restano
separate e sospese. Il Form segue attraverso i suoi owner; non viene aggiornato
da questa recensione. Restituisci qui una lettura motivata con gli interventi
realmente utili e le incertezze che possono cambiare il seguito. La recensione
non seleziona modifiche o pubblicazioni su altre superfici.
