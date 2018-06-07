from setuptools import setup

from ldapauthenticator import __version__ as version


setup(
    name='jupyterhub-ldapauthenticator',
    version=version,
    description='LDAP Authenticator for JupyterHub',
    url='https://github.com/yuvipanda/ldapauthenticator',
    author='Yuvi Panda',
    author_email='yuvipanda@riseup.net',
    license='3 Clause BSD',
    packages=['ldapauthenticator'],
    install_requires=[
        'jupyterhub',
        'ldap3',
        'tornado',
        'traitlets',
    ]
)
