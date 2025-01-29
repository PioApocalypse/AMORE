import json

# ED: function to get a user input made as testing ground
def get_user_input():
    title = input("Title: ")
    date = input("Date (YYYY-MM-DD): ") # this thing HAS to go
    body = input("Body: ")

    metadata = {
        "title": title,
        "date": date,
        "body": body
    }

    # save on JSON
    with open('metadata.json', 'w') as md_file:
        json.dump(metadata, md_file)

    print("Data stored in metadata.json.")

# I still have to figure out how THIS works tbh but prof told us to include it:
# note for self: it checks if this file is being run as program (== '__main__') or imported as module (!= '__main__'). TIL.
if __name__ == "__main__":
    get_user_input()