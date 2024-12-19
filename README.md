# AMORE
**Autonomous Management of Outputs for Research Efficiency** (to rename later) is a primitive interface for allowing researchers to upload data on experiments to [eLabFTW](https://github.com/elabftw/elabftw) with minimal effort.

<!-- Buona idea per acronimo: 'Alternative Manager of Outputs with Reduced Efforts' -->
> To-do: translate what follows in English.

## Backend structure
Dietro le quinte il software dovrà permettere all'utente di **creare nuovi campioni**, **gestirne la posizione** e **segnalare guasti e interventi sui macchinari** (risorse) del laboratorio.

### Creazione del campione
Questa utility avrà a sua volta due funzioni:

* Assegnazione nome e ID al campione;
    * [GET] Prende da eLab l'ID dell'ultimo campione;
    * Incrementa di 1 e assegna il nuovo ID al nuovo campione;
    * [Input] Ottiene dall'operatore metadati utili;
    * [POST] Carica sul database il nuovo campione (con i propri metadati e il nuovo ID);
* Uso consumabili (cioè in sostanza il tracciamento dei substrati residui);
    * [Input] Prende in input dall'utente il numero (codice?) del batch di substrati da cui si prelevano i materiali richiesti (che possono essere più di uno);
    * [GET] Prende da eLab il numero di pezzi disponibili per quel batch;
    * [Input] Prende dall'operatore il numero di substrati da utilizzare (N sempre minore del numero di unità disponibili per quel batch);
    * [POST] Sottrae N al numero di unità disponibili su eLab.

#### ID dei campioni
Si è proposto un formato di codice ID per i campioni particolarmente comodo per i ricercatori ma incompatibile con il database preesistente di eLab. Il formato è:

<div style="font-size: 2rem;" align="center">
XX - AA - ###
</div>

Dove XX è il codice della città in cui si è svolto l'esperimento (es. NA per Napoli, RM per Roma, etc.), AA sono le ultime due cifre dell'anno (24, 25, 26...) e ### è l'ID progressivo in formato "eLab-compliant" (001, 002, 003...) che dovrebbe però tornare a zero ogni 1° gennaio.

Possibile soluzione per generare un codice ID simile per i campioni è modificare la struttura del db di eLab, quindi il sorgente del software stesso per usare l'ID completo (nel formato XX-AA-###) come chiave primaria delle varie entry.
<!-- Usare una tabella nuova per ogni anno forse? -->

### Posizione del campione
> TBA

### Guasti e interventi
> TBA

## Frontend structure
La soluzione migliore sarebbe mettere su un form in HTML e Javascript che esporremo nella rete interna via Apache Web Server; il form, il server e AMORE saranno sulla stessa macchina virtuale su cui sta girando eLab.