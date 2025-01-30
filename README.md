# AMORE
**Autonomous Management of Outputs for Research Efficiency** (to rename later) is a primitive interface for allowing researchers to upload data on experiments to [eLabFTW](https://github.com/elabftw/elabftw) with minimal effort.

<!-- Buona idea per acronimo: 'Alternative Manager of Outputs with Reduced Efforts' -->
> To-do: translate what follows in English.

## Backend structure
Behind the stage this software should allow the end user to easily **create new samples**, **update their in-real-time position** and **briefly report faults and maintainance operations of machinery** inside the lab.

### Creating new sample
This utility should serve two purposes:

* Assign name and ID to sample;
    * [GET] from eLab ID of latest sample (given location and year);
    * Increment by one to make a new ID to assign to newest sample;
    * [Input] from operator giving useful metadata # TO DEFINE;
        * Can be name of compound, brief description, notes, values of temperature, mass and so on...
    * [POST] everything to eLab's database;
* Use of consumables (substrates);
    * [Input] - operator provides code of the batch(es) from which the substrate(s) was/are taken;
    * [GET] from eLab the number of available pieces from the same batch;
    * [Input] - operator gives number of used substrates (N less than available units);
    * Decrement availability by N;
    * [POST] new number of available units to eLab.

#### On the subject of samples' ID's
The following ID scheme for new samples is proposed. While technically incompatible with eLab's own primary keys it can be assigned to a resource in the "Name" field - before the compound's name - and it would be way more useful for Naples' reseach team.

<div style="font-size: 2rem;" align="center">
XX YY - ###
</div>

Where XX is a code assigned to the location (e.g. NA for Naples, RM for Rome, etc.), YY are the last two digits of present year (24, 25, 26...) and ### is the progressive ID in "eLab-compliant" format (just numbers: 001, 002, 003...) which has to be reset to 001 (or 000) every 1^st^ of January.

<!-- Possibile soluzione per generare un codice ID simile per i campioni è modificare la struttura del db di eLab, quindi il sorgente del software stesso per usare l'ID completo (nel formato XX-AA-###) come chiave primaria delle varie entry.
Usare una tabella nuova per ogni anno forse? -->

### Sample real-time position
> TBA

### Faults and maintainance
> TBA

## Frontend structure
The use of Python library **Flask** has been proposed.