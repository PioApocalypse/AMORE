import sys

def main(titolo, descrizione, posizione, localita):
    # Qui puoi elaborare i dati come necessario
    print(f"Titolo: {titolo}")
    print(f"Descrizione: {descrizione}")
    print(f"Posizione: {posizione}")
    print(f"Località: {localita}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python main.py <titolo> <descrizione> <posizione> <localita>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])