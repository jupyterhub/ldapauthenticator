from setuptools import setup

setup(
    name='jupyterhub-ldapauthenticator',
    version='1.0',
    description='LDAP Authenticator for JupyterHub',
    url='https://github.com/oneklc/ldapauthenticator',
    author='klc',
    author_email='oneklc@gmail.com',
    license='3 Clause BSD',
    packages=['ldapauthenticator'],
    install_requires=[
        'ldap3','traitlets', 'tornado', 'jupyterhub'
    ]
)
