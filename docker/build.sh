#!/bin/bash
set -euo pipefail



project_name="rarvi"
env_file="test.env"
firebase_key=invalid

usage(){
    cat <<EOF
Usage: $0 -f <firebase-service-key> [-p <project-name>] [-e <env-file>]
    -f the path to firebase key, which is used to authenticate with firebase and send card notifications
    -p The optional nome of the project. Default is 'rarvi'.
    -e The optional env file with the environment variables setup. Default is 'test.env' that
    points to env file in this current folder.
EOF
}


if [[ $1 == "-h" || $1 == "--help" ]]; then
    usage
    exit 0
fi

while getopts ":f:p:e:" opt; do
  case $opt in
    f) firebase_key="$OPTARG"
    ;;
    p) project_name="$OPTARG"
    ;;
    e) env_file="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
        usage
        exit 1
    ;;
  esac
done

if [[ $firebase_key == invalid ]];then
  echo "Missing mandatory parameter -f"
  usage
  exit 1
fi
source $env_file
export HOST_FIREBASE_SERVICE_KEY=$firebase_key

mkdir -p volume
openssl rand -out volume/signature.key 32
export HOST_SIGNATURE_KEY=$(pwd)/volume/signature.key
docker compose -f docker-compose.yaml -p $project_name --env-file $env_file up --build -d

echo "You can access the Swagger interface at http://localhost:$API_PORT/docs for testing purposes."
