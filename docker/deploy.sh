#!/bin/bash
set -e

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
echo ${DOCKERHUB_TOKEN} | docker login -u ${DOCKERHUB_USERNAME}  --password-stdin

# change work directory to env or prod
cd ~/${DEPLOY_ENV}

# Convert multiple arguments for docker compose to short function
run_compose() {
    # merge yaml files for production
    local compose_files="-f docker-compose.yml -f docker/docker-compose.prod.yml"
    # set default value from env
    local project_name="${DEPLOY_ENV}"

    # check if -p argument exist, override it
    # this is for custom project name during deploy, for example "test"
    if [ "$1" = "-p" ] && [ -n "$2" ]; then
        project_name="$2"
        shift 2
    fi

    # merge yaml files for dev (override some production settings)
    if [ "${DEPLOY_ENV}" == "dev" ]; then
        compose_files="${compose_files} -f docker/docker-compose.dev.yml"
    fi

    # run command
    docker compose \
        -p "${project_name}" \
        ${compose_files} \
        "$@"
}

# Pull web-container image with new tag
run_compose pull -q web

##############  TEST MIGRATIONS ON COPY OF REAL DATABASE ########
# Check if new container makes migrations on copy of prod db
# backup current db for host
mkdir -p /home/deploy/backups/${DEPLOY_ENV}
run_compose exec db bash  -c 'pg_dump --clean --if-exists -U $POSTGRES_USER -d $POSTGRES_DB > /tmp/backup.sql'
backup_file_name=`date '+%Y-%m-%d_%H%M%Z'`_before_action_${DOCKER_TAG_WEB##*-}.sql
run_compose cp db:/tmp/backup.sql /home/deploy/backups/${DEPLOY_ENV}/${backup_file_name}

# now we use different docker project name "test" for test migrations
# remove old test instances if exists
run_compose -p test down -v

# start test postgres
run_compose -p test up -d db
#and wait for postgres starts 10 seconds
sleep 10

# restore test database from fresh backup
run_compose -p test exec -T db bash -c \
'psql -U $POSTGRES_USER -d $POSTGRES_DB --set=ON_ERROR_STOP=1 -f -'\
 < /home/deploy/backups/${DEPLOY_ENV}/${backup_file_name}

# show migrations
run_compose -p test run --rm  web python manage.py showmigrations

# apply  migrations
run_compose -p test run --rm  web python manage.py migrate

# if we here, it means migrations are OK and no errors
# remove test postgres with it's volume
run_compose -p test down -v
##############  END TEST MIGRATIONS ########


# apply migrations on real database
run_compose run --rm  web python manage.py migrate

# refresh current backup for developers
run_compose exec db bash  -c 'pg_dump --clean --if-exists -U $POSTGRES_USER -d $POSTGRES_DB > /tmp/backup.sql'
run_compose cp db:/tmp/backup.sql /home/deploy/backups/${DEPLOY_ENV}/teamclimate.sql

# Start all production containers with new web container
run_compose up -d

# if some container addresses changed, caddy restart is necessary
run_compose restart caddy

#wait for health checking
sleep 5

#show us final result
run_compose ps
