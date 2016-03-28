from setuptools import setup

setup(
    name='jupyterhub-ldapauthenticator',
    version='1.0',
    description='LDAP Authenticator for JupyterHub',
    url='https://github.com/yuvipanda/ldapauthenticator',
    author='Yuvi Panda',
    author_email='yuvipanda@riseup.net',
    license='3 Clause BSD',
    packages=['ldapauthenticator'],
    install_requires=[
        'ldap3',
    ]
)
