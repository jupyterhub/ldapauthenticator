# Contributing

Welcome! As a [Jupyter](https://jupyter.org) project, you can follow the [Jupyter contributor guide](https://docs.jupyter.org/en/latest/contributing/content-contributor.html).

Make sure to also follow [Project Jupyter's Code of Conduct](https://github.com/jupyter/governance/blob/main/conduct/code_of_conduct.md)
for a friendly and welcoming collaborative environment.

This guide was adapted from the [contributing guide in the main `jupyterhub` repo.](https://github.com/jupyterhub/jupyterhub/blob/main/CONTRIBUTING.md)

## Setting up a development environment

JupyterHub requires Python >= 3.7.

As a Python project, a development install of JupyterHub follows standard practices for installation and testing.

Note: if you have Docker installed locally, you can run all of the subsequent commands inside of a container after you run the following initial commands:

```shell
# starts an openldap server inside a docker container
./ci/docker-ldap.sh

# starts a python docker image
docker run --rm -it -v $PWD:/usr/local/src --workdir=/usr/local/src --net=host python:3.11 bash
```

1. Do a development install with pip

   ```bash
   pip install --editable ".[test]"
   ```

1. Set up pre-commit hooks for automatic code formatting, etc.

   ```bash
   pip install pre-commit

   pre-commit install --install-hooks
   ```

   You can also invoke the pre-commit hook manually at any time with

   ```bash
   pre-commit run
   ```

To clean up your development LDAP deployment, run:

```
docker rm -f test-openldap
```

## Testing

It's a good idea to write tests to exercise any new features,
or that trigger any bugs that you have fixed to catch regressions.

You can run the tests with:

```bash
# starts an openldap server inside a docker container
./ci/docker-ldap.sh

# run tests
pytest
```

The tests live in `ldapauthenticator/tests`.

When writing a new test, there should usually be a test of
similar functionality already written and related tests should
be added nearby.

When in doubt, feel free to ask.
