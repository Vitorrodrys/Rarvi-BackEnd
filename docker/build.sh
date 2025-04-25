#!/bin/bash




project_name="rarvi"
env_file="test.env"

usage(){
    cat <<EOF
Usage: $0 [-p <project-name>] [-e <env-file>]"
    -p The optional nome of the project. Default is 'rarvi'.
    -e The optional env file with the environment variables setup. Default is 'test.env' that
    points to env file in this current folder.
EOF
}


if [[ $1 == "-h" || $1 == "--help" ]]; then
    usage
    exit 0
fi

while getopts ":p:e:" opt; do
  case $opt in
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

source $env_file

docker compose -f docker-compose.yaml -p $project_name --env-file $env_file up --build -d

echo "You can access the Swagger interface at http://localhost:$API_PORT/docs for testing purposes."
