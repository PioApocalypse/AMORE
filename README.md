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
The following ID scheme for new samples is proposed. While technically incompatible with eLab's own primary keys it can be assigned to a resource in the "Title" field - before the compound's name - and it would be way more useful for Naples' reseach team.

<div style="font-size: 2rem;" align="center">
XX-YY-###
</div>

Where XX is a code assigned to the location (e.g. Na for Naples, Rm for Rome, etc.), YY are the last two digits of present year (24, 25, 26...) and ### is a progressive ID (just numbers: 001, 002, 003...) which has to be reset to 001 (or 000) every 1^st^ of January. To generate the full title of the sample (pseudocode): \
`concat(XX,"-",YY,"-",###," -- ",NameOfCompound)`, or `f("%v-%v-%v -- %v", XX, YY, ###, NameOfCompound)`.

Additionally, a numeric ID (integer) is assigned to every sample in the format YY###, which can obviously composed by sum of: `str_to_num(YY) * 1000 + ###`.

<!-- Possibile soluzione per generare un codice ID simile per i campioni è modificare la struttura del db di eLab, quindi il sorgente del software stesso per usare l'ID completo (nel formato XX-AA-###) come chiave primaria delle varie entry.
Usare una tabella nuova per ogni anno forse? -->

### Sample real-time position
> TBA

### Faults and maintainance
> TBA

## Frontend structure
The use of Python library **Flask** has been proposed. On testing ground plain ugly HTML will be preferred instead.

## Checkbox
Issue = problem to solve, obstacle; \
Warning = always pay attention; \
Error = returns error.

### Phase 1 COMPLETE - New sample
- [x] Post test to website
    * Issue #1: `export PYTHONPATH=$(pwd)` necessary for the script to recognise *amore* as module.
    * Issue #2: remember to initialize venv with `python -m venv ./.venv` and `pip install -r requirements.txt`.
    * <strike>Warning: pay attention to the fucking correct port (**8080**, not 8006 - PVE - nor 443 - standard https).</strike> Default port changed to 443.
    * <strike>Error: after successful post, pytest exits with following error:</strike> pytest use removed for good, response was not json.
<strike>
```python
ERROR tests/post_sample.py - requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```
</strike>

- [x] Post test with custom title
- [x] Post test with custom title and standard ID
    * Issue: api apparently doesn't support a POST method to directly create a new sample with extra fields, waiting for eLabFTW 5.2.0. Feature technically implemented.
- [x] Fix issue: use a PATCH request on fresh new sample to inject body, STD-ID, other metadata.

### Phase 2 COMPLETE - Graphical interface
- [x] GUI in plain HTML with simple form, whose post button calls my python script
- [x] Dropdown menus
- [x] Additional extra fields like batch, holder, position, proposal, owner
- [x] Additional fields must be taken from other elabftw resources

### Phase 3 - Other features
- [x] Auto update batch for decrementing number of substrates on every use
    * Only show batches with int('Available pieces') > 0
    * Get value for extra field 'Available pieces' of batch selected on post, patch with 'Available pieces' -1
- [x] Send warning when batch is low on substrates
- [x] Must-discuss idea: upload attachment files to sample
- [ ] <strike>"Search sample" feature</strike> Let's talk about it...
- [x] <strike>Possibly "delete sample" feature</strike> Terrible idea.
- [ ] Make sure position is not shared among different samples [ED: is it even possible?]

### Phase 4 - Error handling, data validation, sanification
- [ ] Sanification of inputs provided - avoid code/SQL injections
- [ ] Warn user if posting fails, say reason
> TBA

### Phase 5 - From dev to prod
- [ ] Base URL and verification check must be provided during installation
    * Base URL and verification check can still be edited in .env file by user
- [ ] Personal API key must be provided by user manually
    * Can I create a login screen and automate the API key creation? I can always delete it on logout...
- [ ] Finish up setup.py file
> TBA

### Phase 6 - Enduser test in production
- [ ] Make sure eLabFTW is properly configured
- [ ] Distribute software via GitHub (open repository)
> TBA
