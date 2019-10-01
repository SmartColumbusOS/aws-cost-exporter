#!/bin/bash

echo "Logging into Dockerhub ..."
echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin

echo "Determining image tag for ${TRAVIS_BRANCH} build ..."

if [[ $TRAVIS_BRANCH =~ ^[0-9]+\.[0-9]+\.[0-9]+ ]]; then
    export TAGGED_IMAGE="smartcolumbusos/aws_cost_exporter:${TRAVIS_BRANCH}"
elif [[ $TRAVIS_BRANCH == "master" ]]; then
    export TAGGED_IMAGE="smartcolumbusos/aws_cost_exporter:development"
else
    echo "Branch should not be pushed to Dockerhub"
    exit 0
fi

echo "Pushing to Dockerhub with tag ${TAGGED_IMAGE} ..."

docker tag aws_cost_exporter:build "${TAGGED_IMAGE}"
docker push "${TAGGED_IMAGE}"
