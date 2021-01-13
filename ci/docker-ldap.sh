#!/usr/bin/env bash
# source this file to setup LDAP
# for local testing (as similar as possible to docker)

set -e

NAME="hub-test-ldap"
DOCKER_RUN="docker run -d --name $NAME"
RUN_ARGS="-p 389:10389 -p 636:10636 rroemhild/test-openldap"

docker rm -f "$NAME" 2>/dev/null || true

$DOCKER_RUN $RUN_ARGS
