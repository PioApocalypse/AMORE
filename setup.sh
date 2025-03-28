#!/bin/bash

# PRESENTATION!
echo "==============================================="
echo "======== Welcome to AMORE: Alternative ========"
echo "=== Manager of Outputs with Reduced Efforts ==="
echo "================ Setup Wizard. ================"
echo "==============================================="
echo

# FUNCTIONS
# Define function which checks for valid root dir url in the stupidest way possible: DOES IT REDIRECT?
# To-do: sanify this check, currently it works very poorly and doesn't differentiate between https and http
check_elabftw() {
    local url=$1
    if curl -s "$url" -k | grep -q "Redirecting to /dashboard.php"; then
        return 0
    else
        return 1
    fi
}
# Normalize url to conform to AMORE
normalize_url() {
    local url=$1
    # Remove any protocol prefix
    url=${url#http://}
    url=${url#https://}
    # Remove any trailing slash
    url=${url%/}
    # Add https:// prefix and trailing slash
    echo "https://$url/"
}


LICENSE=$(echo $(head -n 1 LICENSE))
echo -e "By proceeding you acknowledge that AMORE is\npublished under $LICENSE."
sleep 1
echo

# Check arguments for options: --force, --literal
# Literal mode: do not normalize the url
literal_mode=false
for arg in "$@"; do
    if [[ "$arg" == "--literal" ]]; then
        literal_mode=true
        break
    fi
done
# Force mode: skip check for elab instance on url
force_mode=false
for arg in "$@"; do
    if [[ "$arg" == "--force" ]]; then
        force_mode=true
        break
    fi
done

# normalize and check for elab instance
while true; do
    read -p "Please input the url of a valid eLabFTW instance: " URL
    if [[ "$literal_mode" == false ]]; then
        URL=$(normalize_url "$URL")
    else echo "Warning: Literal mode enabled, URL will be passed as-is."
        echo "Please make sure to include the correct protocol prefix (e.g. http://...)"
        echo "And make sure the URL ends with a trailing slash (e.g. ...host.it/)."
    fi
    if [[ "$force_mode" == true ]]; then
        echo "Warning: Force mode enabled, skipping website validation."
        echo "Normalized URL: $URL"
        echo
        break
    fi

    echo "Checking..." && sleep 1
    if check_elabftw "$URL"; then
        echo "Valid eLabFTW URL: $URL"
        echo
        break
    else
        echo -e "Error: eLabFTW instance not found on $URL.\nIf you're sure an instance exists you may\noverride this lock with the --force option."
        echo
    fi
done

# echo "Please provide your own API key."
# echo "API keys can be generated on your profile"
# echo "See: https://doc.elabftw.net/api.html#generating-a-key"
# echo
# read -s -p "Paste your key here (echo off): " KEY # password-like
# echo # new line
read -p "Only allow secure connections (Y/n)? " secure
secure=${secure,,} # to lowercase
if [[ -z "$secure" ]]; then
    VERIFY=True
    else case "$secure" in
        y|ye|yes) VERIFY=True ;;  # 0 = true (yes)
        n|nay|no) VERIFY=False ;;   # 1 = false (no)
        *) echo I assume you mean 'yes' then... ; VERIFY=True ;;
    esac
fi


echo
echo "Building the docker image with following parameters:"
echo -e "URL: $URL\nSSL verification: $VERIFY"
read -p "Press enter to continue, or ^C to abort."

docker build \
  --build-arg URL=${URL} \
  --build-arg VERIFY=${VERIFY} \
  -t amore .

echo
echo "Docker image ready."
echo "Running the container..."
sleep 1
docker run -d -p 5000:5000 --name amore-container --restart always amore && \
    echo && \
    echo "AMORE is now running on http://localhost:5000." && \
    echo "Thank you for your patience. ♥"
sleep 1

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This script serves as installer of AMORE on a computer.   #
# Requires Linux and Docker.                                #
# Developed on Linux Mint 22, Nobara Linux 41.              #
# Tested and deployed on Almalinux 9.                       #
#                                                           #
# May no automation provided by this piece of software ever #
# save a single second in the work of a military scientist. #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #