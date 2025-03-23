#!/bin/bash

# PRESENTATION!
echo "==============================================="
echo "======== Welcome to AMORE: Alternative ========"
echo "=== Manager of Outputs with Reduced Efforts ==="
echo "================ Setup Wizard. ================"
echo "==============================================="
echo

# FUNCTIONS
# define function which checks for valid root dir url in the stupidest way possible: DOES IT REDIRECT?
check_elabftw() {
    local url=$1
    if curl -s "$url" -k | grep -q "Redirecting to /dashboard.php"; then
        return 0
    else
        return 1
    fi
}
# normalize url to conform to AMORE
normalize_url() {
    local url=$1
    # remove any protocol prefix
    url=${url#http://}
    url=${url#https://}
    # remove any trailing slash
    url=${url%/}
    # add https:// prefix and trailing slash
    echo "https://$url/"
}


LICENSE=$(echo $(head -n 1 LICENSE))
echo -e "By proceeding you acknowledge that AMORE is\npublished under $LICENSE."
sleep 1
echo

# force mode: do not check for elab instance
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
    URL=$(normalize_url "$URL")
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

echo "Please provide your own API key."
echo "API keys can be generated on your profile"
echo "See: https://doc.elabftw.net/api.html#generating-a-key"
echo
read -s -p "Paste your key here (echo off): " KEY # password-like
echo # new line
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
read -p "Press enter to continue."

docker build \
  --build-arg URL=${URL} \
  --build-arg KEY="${KEY}" \
  --build-arg VERIFY=${VERIFY} \
  -t amore .

echo
echo "Docker image ready."
echo "Running the container..."
sleep 1
docker run -d -p 5000:5000 --name amore-container amore

echo
echo "AMORE is now running on http://localhost:5000."
echo "Thank you for your patience. ♥"
sleep 1