# Contributing

Welcome! As a [Jupyter](https://jupyter.org) project, we follow the [Jupyter contributor guide](https://jupyter.readthedocs.io/en/latest/contributor/content-contributor.html).

Make sure to also follow [Project Jupyter's Code of Conduct](https://github.com/jupyter/governance/blob/main/conduct/code_of_conduct.md)
for a friendly and welcoming collaborative environment.

This guide was adapted from the [contributing guide in the main `jupyterhub` repo.](https://github.com/jupyterhub/jupyterhub/blob/main/CONTRIBUTING.md)

## Setting up a development environment

JupyterHub requires Python >= 3.5.

As a Python project, a development install of JupyterHub follows standard practices for installation and testing.

Note: if you have Docker installed locally, you can run all of the subsequent commands inside of a container after you run the following initial commands:

```
./ci/docker-ldap.sh
docker run -v $PWD:/usr/local/src --workdir /usr/local/src --net=host --rm -it python:3.6 bash
```

1. Do a development install with pip

    ```bash
    cd ldapauthenticator
    python3 -m pip install --editable .
    ```

1. Install the development requirements,
   which include things like testing tools

    ```bash
    python3 -m pip install -r dev-requirements.txt
    ```
1. Set up pre-commit hooks for automatic code formatting, etc.

    ```bash
    pre-commit install
    ```

    You can also invoke the pre-commit hook manually at any time with

    ```bash
    pre-commit run
    ```

To clean up your development LDAP deployment, run:
```
docker rm -f ldap
```

## Contributing

JupyterHub has adopted automatic code formatting so you shouldn't
need to worry too much about your code style.
As long as your code is valid,
the pre-commit hook should take care of how it should look.
You can invoke the pre-commit hook by hand at any time with:

```bash
pre-commit run
```

which should run any autoformatting on your code
and tell you about any errors it couldn't fix automatically.
You may also install [black integration](https://github.com/ambv/black#editor-integration)
into your text editor to format code automatically.

If you have already committed files before setting up the pre-commit
hook with `pre-commit install`, you can fix everything up using
`pre-commit run --all-files`.  You need to make the fixing commit
yourself after that.

## Testing

It's a good idea to write tests to exercise any new features,
or that trigger any bugs that you have fixed to catch regressions.

You can run the tests with:

```bash
pytest -v
```

The tests live in `ldapauthenticator/tests`.

When writing a new test, there should usually be a test of
similar functionality already written and related tests should
be added nearby.

When in doubt, feel free to ask.
