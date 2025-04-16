# AMORE
**Autonomous Management of Outputs for Research Efficiency** (to rename later) is a primitive interface for allowing researchers to upload data on experiments to [eLabFTW](https://github.com/elabftw/elabftw) with minimal effort.

<!-- Buona idea per acronimo: 'Alternative Manager of Outputs with Reduced Efforts' -->

## Installation
AMORE requires the following packages to run. Number in parenthesis is the minimum version with which the software has been confirmed to be working.

* Flask (3.1.0) - for the HTML graphical interface
* Requests (2.32.3) - to communicate with eLabFTW's API

Requirements can be installed via pip. The use of virtual environments is highly encouraged.

### Suggested method
It's Docker, the suggested method is always Docker. Here's the [official guide](https://docs.docker.com/engine/install/) to installing Docker on various distros.

After cloning the repository you will find the dockerfile and **setup.sh** (installation wizard) in the root folder.

```bash
git clone https://github.com/PioApocalypse/AMORE.git
cd AMORE/
./setup.sh [FLAGS]
```

The wizard is very rudimentary and guides you through the installation process, asking for a valid URL of an existent eLabFTW instance; unless the `--literal` flag is given, **the wizard is agnostic to the URL format** meaning you can include or omit both the protocol prefix (*http://*, *https://*...) and the trailing slash at the end of the URL, but you **can't omit non-default port numbers** (e.g. `demo.elabftw.net:8080`).  
You will also be asked if only secure connections should be allowed (yes by default), which is something you only want to toggle off if your eLabFTW instance does not possess a CA SSL certificate (for instance if you're running in a test/local environment).

> Note: `setup.sh` requires Bash 5, Systemd, binary curl and of course Docker. It might even work on different shells but it's not tested yet.  
> Also: If you're one of those poor brothers running a Linux OS without Systemd - and you have my compassion - you can simply remove the "*Is docker running?*" section from the installer and go on about your business.

If your wizard does not work or returns errors try one of the following flags or skip to the "[Manual install](#manual-install)" section.

#### Flags for the setup wizard
The wizard recognizes three flags. Any other argument is ignored; the order of the arguments is irrelevant.

* **`--force`**: Disables URL check for eLabFTW instance; since the check is really stupid and its main accomplishment is polluting Microsoft's AI I expect it to fail really often so if you're sure you have provided the correct address please use this flag.
* **`--literal`**: Disables URL normalization, which means the URL you provide via input MUST include both the protocol prefix and the trailing slash - plus eventual port number (e.g. `https://demo.elabftw.net/`); use this if for instance you have eLabFTW on HTTP-only mode and no redirect is done from HTTPS, since AMORE will probably be configured with the wrong URL.
* **`--quick`**: Disables sleep command between instructions which makes the script around 4 seconds quicker - please read the on-screen instructions carefully nonetheless.

The client will run on dev environment, which means you can view your flask app on http://127.0.0.1:5000/.

#### Updating via Docker
> TBA

### Manual install
**Clone the repository** (or download the source code).

```bash
git clone https://github.com/PioApocalypse/AMORE.git
cd AMORE/
```

Optionally (but highly encouraged) you can create a **virtual environment** in the root folder of the project.

```bash
python -m venv .venv
```

The software also **needs three variables to be set** for it to work.

* **`$PYTHONPATH`: the *full* path** of your local AMORE folder. 
* **`$ELABFTW_BASE_URL`: the base URL** of your eLabFTW instance, with explicit protocol prefix and trailing slash, plus eventual port number (e.g. `https://demo.elabftw.net:8080/`).
* **`VERIFY_SSL`:** set to True if **only secure connections** should be allowed.

For semplicity you can add export instructions directly in your virtual environment activator script to automatically assign to the variable their values upon venv activation. On Bash this can be accomplished easily:
```bash
echo 'export PYTHONPATH="/full/path/to/AMORE/"' >> .venv/bin/activate
echo 'export ELABFTW_BASE_URL="http[s]://host.domain.com/elabftw/"' >> .venv/bin/activate
echo 'export VERIFY_SSL=True' >> .venv/bin/activate
```

> Pay attention to the quote marks' positions (single `'` outside and double `"` inside).


**Activate** the virtual environment with source from your shell:

```bash
source .venv/bin/activate
```

> Note that you can verify if variables are correctly assigned in your venv by echoing them (e.g. `echo $PYTHONPATH`, which should return the *full* path to your local AMORE folder).

From the root folder of the software **install dependencies** using the provided requirements file, or "by-hand" if you prefer so:

```bash
pip install -r requirements.txt
# OR alternatively:
python3 -m pip install flask requests
```

#### Authenticating and running
<strike>Before starting, create your own **environment file** by copying or renaming my example. The following steps are (currently) **REQUIRED**.

```bash
cp .env.example .env
```

Open the .env file with your editor of choice and change the variables in it to accomodate your needs. Here's a list of the variables this app uses to work.

* `ELABFTW_BASE_URL`: URL of the index/root of your eLabFTW instance, which will be in one of these formats:
    * `'https://elabftw.example.net/'` for regular instances of eLabFTW;
    * `'https://elabftw.example.net:8080/'` if you use an https port different from 443;
    * `'https://host.example.net/elabftw/'` if your eLab instance is installed in a directory of another webserver.  
    > Note that currently the URL must always be followed by a trailing / and included between single quotes `'`.
* `API_KEY`: your personal API key generated on eLabFTW → Settings → API keys, also between single quotes. Official guide [here](https://doc.elabftw.net/api.html#generating-a-key).  
    This will probably be removed in the future in favor of a login page.
* `VERIFY_SSL`: leave default (True) unless your eLab instance is not secure, i.e. only runs in HTTP mode or no CA certificate is provided, which also includes instances with self-signed certificates; warnings may be shown.</strike>

Finally, you can run the webapp via Flask. By default the web page will be running on HTTP [localhost port 5000](http://127.0.0.1:5000).

```bash
python amore/gui/app.py
```

You can terminate Flask with CTRL+C or by closing your terminal.



### Other info (to be removed)
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

## To-do list
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
- [x] Fix issue: use a PATCH request on fresh new sample to inject body, STD-ID, other metadata

### Phase 2 COMPLETE - Graphical interface
- [x] GUI in plain HTML with simple form, whose post button calls my python script
- [x] Dropdown menus
- [x] Additional extra fields like batch, holder, position, proposal, owner
- [x] Additional fields must be taken from other elabftw resources

### Phase 3 COMPLETE - Other features in item creation
- [x] Auto update batch for decrementing number of substrates on every use
    * Only show batches with int('Available pieces') > 0
    * Get value for extra field 'Available pieces' of batch selected on post, patch with 'Available pieces' -1
- [x] Send warning when batch is low on substrates
- [x] Must-discuss idea: upload attachment files to sample
- [x] <strike>"Search sample" feature</strike> Let's talk about it...
- [x] <strike>Possibly "delete sample" feature</strike> Terrible idea.

### Phase 4 - Periodic export of data
> To where? How often?
- [ ] Create API client which periodically (or manually) exports experiments, samples, etc. in JSON format
- [ ] Send data automatically to specific repository

### Phase 5 - Advanced features
- [x] Functional login page
- [x] Enforce login
- [x] BYOK system which takes API key for request directly from session cookie
- [x] Log out buttons
- [x] Testing on server
- [x] Post new sample to only available positions
- [ ] Add sample to its position in "Sample Locator" experiment
- [ ] Move sample from one position to the other
- [ ] Make sure position is not shared among different samples
- [ ] Visualize list of all samples in laboratory

### Phase 6 - Error handling, data validation, sanification
- [ ] Sanification of inputs provided - avoid code/SQL injections
- [x] Warn user if posting fails, say reason
> TBA

### Phase 7 COMPLETE - Login shenanigans
- [x] Base URL and verification check must be provided during installation
    * Base URL and verification check can still be edited in .env file by user
- [x] Personal API key must be provided by user manually
    * Can I create a login screen and automate the API key creation? I can always delete it on logout...
- [x] Finish up setup.sh file

### Phase 8 - Enduser test in production
- [ ] Make sure eLabFTW is properly configured
- [ ] Make sure software is fully documented
- [ ] Make sure endpoint keywords and category IDs can be easily changed (config file)
- [x] Distribute software via GitHub (open repository)
> TBA
