#!/bin/bash

# PRESENTATION!
echo "==============================================="
echo "======== Welcome to AMORE: Alternative ========"
echo "=== Manager of Outputs with Reduced Efforts ==="
echo "================ Setup Wizard. ================"
echo "==============================================="
echo

# FUNCTIONS
# Define function which checks for valid root dir url in the stupidest way possible:
#   curl GET a non existent (404) page, check for "eLabFTW" (which should be in the meta description)
# To-do: sanify this check, currently it works very poorly and doesn't differentiate between https and http
check_elabftw() {
    local url="$1/api"
    if curl -s "$url" -k | grep -q "eLabFTW"; then
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
# Get setup variables from config.json
parse_and_export_json() {
    local json_file="$1"
    # Is jq installed?
    if ! command -v jq &> /dev/null; then
        echo "ERROR: jq not installed, skipping read from --file option."
        exit 1
    fi
    while IFS="=" read -r key value; do
        if [[ -n "$key" ]]; then
            export "$key"="$value"
            echo "Exporting: $key=$( echo $value | cut -c1-20 )..."
        fi
    done < <(jq -r "to_entries|map(\"\(.key)=\(.value|tostring)\")|.[]" "$json_file")
    sleep $SLEEP
    echo
}


# Check arguments for options: --force, --literal
# Literal mode: do not normalize the url
literal_mode=false
force_mode=false
SLEEP=1
for arg in "$@"; do
    if [[ "$arg" == "--literal" ]]; then
        literal_mode=true
        break
    fi
done
# Force mode: skip check for elab instance on url
for arg in "$@"; do
    if [[ "$arg" == "--force" ]]; then
        force_mode=true
        break
    fi
done
# Quick mode: no sleeping between instructions
for arg in "$@"; do
    if [[ "$arg" == "--quick" ]]; then
        SLEEP=0
        break
    fi
done
# Look for config file
for arg in "$@"; do
    if [[ "$arg" == "--file" ]]; then
        file_path="./config.json"
        if [[ -f "$file_path" ]]; then
            echo "Config file found: $file_path"
            parse_and_export_json "$file_path"
        else
            echo "File not found: $file_path"
            exit 1
        fi
        break
    fi
done

# STARTING POINT
LICENSE=$(echo $(head -n 1 LICENSE))
echo -e "By proceeding you acknowledge that AMORE is\npublished under $LICENSE."
sleep $SLEEP
echo

# Normalize and check for elab instance if proper flags not specified
if [[ -z "$ELABFTW_BASE_URL" ]]; then
    while true; do
        if [[ "$literal_mode" == false ]]; then
            read -p "Please input the url of a valid eLabFTW instance: " ELABFTW_BASE_URL
            ELABFTW_BASE_URL=$(normalize_url "$ELABFTW_BASE_URL")
        else echo "Warning: Literal mode enabled, URL will be passed as-is."
            echo "Please make sure to include the correct protocol prefix (e.g. http://...)"
            echo "And make sure the URL ends with a trailing slash (e.g. ...host.it/)."
            read -p "Please input the url of a valid eLabFTW instance: " ELABFTW_BASE_URL
        fi
        if [[ "$force_mode" == true ]]; then
            echo "Warning: Force mode enabled, skipping website validation."
            echo "Normalized URL: $ELABFTW_BASE_URL"
            echo
            break
        fi

        echo "Checking..." && sleep $SLEEP
        if check_elabftw "$ELABFTW_BASE_URL"; then
            echo "Valid eLabFTW URL: $ELABFTW_BASE_URL"
            echo
            break
        else
            echo -e "Error: eLabFTW instance not found on $ELABFTW_BASE_URL.\nIf you're sure an instance exists you may\noverride this lock with the --force option."
            echo
        fi
    done
fi

# echo "Please provide your own API key."
# echo "API keys can be generated on your profile"
# echo "See: https://doc.elabftw.net/api.html#generating-a-key"
# echo
# read -s -p "Paste your key here (echo off): " KEY # password-like
# echo # new line
read -p "Only allow secure connections (Y/n)? " secure
secure=${secure,,} # to lowercase
if [[ -z "$secure" ]]; then
    VERIFY_SSL=True
    else case "$secure" in
        y|ye|yes) VERIFY_SSL=True ;;  # 0 = true (yes)
        n|nay|no) VERIFY_SSL=False ;;   # 1 = false (no)
        *) echo I assume you mean 'yes' then... ; VERIFY_SSL=True ;;
    esac
fi

if [[ -z "$API_KEY" ]]; then
    echo "Please provide a temporary API key."
    echo "It will be deleted automatically after successful setup."
    echo "API keys can be generated on your profile."
    echo "See: https://doc.elabftw.net/api.html#generating-a-key"
    echo
    while true; do
        read -s -p "Paste your key here (echo off): " API_KEY # password-like
        if [[ -z "$API_KEY" ]]; then
            echo "Don't leave this field empty."
        else
            break
        fi
    done
fi

if [[ -z "$HOST_PORT" ]]; then
    export HOST_PORT=8080
fi

echo
echo "Building the docker image with following parameters:"
echo -e "URL: $ELABFTW_BASE_URL\nSSL verification: $VERIFY_SSL\nPublishing on port: $HOST_PORT"
read -p "Press enter to continue, or ^C to abort."

echo
echo "Looking for docker..."
sleep $SLEEP
if command -v docker &>/dev/null ; then
    echo "Docker found at $(command -v docker)"
else
    echo "Docker not installed. Refer to: https://docs.docker.com/engine/install/"
    exit 1
fi
# Feel free to remove this block if your init system is different from Systemd
echo "Is docker running?"
sleep $SLEEP
if [ "$( systemctl is-active docker )" == "active" ]; then
    echo "Docker is up and running." && sleep $SLEEP
else
    echo "Docker is not running."
    echo "Have you tried 'systemctl enable --now docker && systemctl start docker'?"
    exit 1
fi
# end

touch config.json
cat > config.json <<EOF
{
    "API_KEY": "$API_KEY",
    "ELABFTW_BASE_URL": "$ELABFTW_BASE_URL",
    "VERIFY_SSL": "$VERIFY_SSL"
}
EOF

docker build \
  --build-arg URL=${ELABFTW_BASE_URL} \
  --build-arg VERIFY=${VERIFY_SSL} \
  -t amore .

rm -f config.json

echo
echo "Docker image ready."
echo "Running the container..."
sleep $SLEEP
docker run -d -p ${HOST_PORT}:5000 --name amore-container --restart always amore && \
    echo && \
    echo "AMORE is now running on http://localhost:${HOST_PORT}." && \
    echo "Thank you for your patience. ♥"
sleep $SLEEP

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This script serves as installer of AMORE on a computer.   #
# Requires Linux and Docker.                                #
# Developed on Linux Mint 22, Nobara Linux 41.              #
# Tested and deployed on Almalinux 9.                       #
#                                                           #
# May no automation provided by this piece of software ever #
# save a single second in the work of a military scientist. #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #