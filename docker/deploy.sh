#!/bin/bash

# this script needs this variables to be set
#  DOCKER_TAG_WEB (full container url like dockerlogin/repo:v1.0.0 )
#  DOCKERHUB_TOKEN (for login to dockerhub)
#  DOCKERHUB_USERNAME (for login to dockerhub)
#  DEPLOY_ENV (prod or dev)

required_vars=("DOCKER_TAG_WEB" "DOCKERHUB_TOKEN" "DOCKERHUB_USERNAME" "DEPLOY_ENV")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Ошибка: Переменная $var не задана"
        exit 1
    fi
done

# login to DockerHub
#echo ${DOCKERHUB_TOKEN} | docker login -u ${DOCKERHUB_USERNAME}  --password-stdin

# change work directory to env or prod
#cd ~/${DEPLOY_ENV}

# Convert multiple arguments for docker compose to short function
run_compose() {
    # merge yaml files for production
    local compose_files="-f docker-compose.yml -f docker/docker-compose.prod.yml"

    # merge yaml files for dev (override some production settings)
    if [ "${DEPLOY_ENV}" == "dev" ]; then
        compose_files="${compose_files} -f docker/docker-compose.dev.yml"
    fi

    # run command
    docker compose \
        -p "${DEPLOY_ENV}" \
        ${compose_files} \
        "$@"
}

# Pull web-container image with new tag
run_compose pull web

# Start all together
run_compose up -d

# if some container addresses changed, restart caddy is necessary
run_compose restart caddy

#show us result
run_compose ps

