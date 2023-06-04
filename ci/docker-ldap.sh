#!/usr/bin/env bash
set -e

# This file (re-)starts an openldap server to test against within a docker
# container based on the image rroemhild/test-openldap.
#
# ref: https://github.com/rroemhild/docker-test-openldap
# ref: https://hub.docker.com/r/rroemhild/test-openldap/
#
# Stop any existing test-openldap container
docker rm --force test-openldap 2>/dev/null || true
# Start a container, and expose some ports, where 389 and 636 are the local
# system's ports that are redirected to the started container.
#
# - 389:10389 (ldap)
# - 636:10636 (ldaps)
#
docker run --detach --name=test-openldap -p 389:10389 -p 636:10636 rroemhild/test-openldap:2.1
