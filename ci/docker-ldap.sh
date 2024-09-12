#!/usr/bin/env bash
set -e

# This file (re-)starts an openldap server to test against within a docker
# container based on the image rroemhild/test-openldap.
#
# ref: https://github.com/rroemhild/docker-test-openldap
# ref: https://github.com/rroemhild/docker-test-openldap/pkgs/container/docker-test-openldap
#
# Stop any existing test-openldap container
docker rm --force test-openldap 2>/dev/null || true
# Start a container, and expose some ports, where 389 and 636 are the local
# system's ports that are redirected to the started container.
#
# - 389:10389 (ldap)
# - 636:10636 (ldaps)
#
# Image updated 2024-09-12 to the latest commit's build
# https://github.com/rroemhild/docker-test-openldap/commit/2645f2164ffb51ec4b5b4a9af0065ad7f2ffc1cf
#
IMAGE=ghcr.io/rroemhild/docker-test-openldap@sha256:107ecba713dd233f6f84047701d1b4dda03307d972814f2ae1db69b0d250544f
docker run --detach --name=test-openldap -p 389:10389 -p 636:10636 $IMAGE

# It takes a bit more than one second for the container to become ready
sleep 3
