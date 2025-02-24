from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Raccolta dei dati dal form
    titolo = request.form['titolo']
    descrizione = request.form['descrizione']
    posizione = request.form['posizione']
    localita = request.form['localita']

    # Validazione dei dati (esempio semplice)
    if not titolo or not descrizione or not posizione or not localita:
        return "Tutti i campi sono obbligatori!", 400

    # Passaggio dei dati a main.py
    try:
        result = subprocess.run(
            ['python', 'main.py', titolo, descrizione, posizione, localita],
            capture_output=True, text=True
        )
        return f"Output: {result.stdout}"
    except Exception as e:
        return f"Errore: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)