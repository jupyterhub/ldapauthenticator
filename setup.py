from setuptools import setup


version = "1.2.2"


with open("./ldapauthenticator/__init__.py", "a") as f:
    f.write("\n__version__ = '{}'\n".format(version))


setup(
    name="jupyterhub-ldapauthenticator",
    version=version,
    description="LDAP Authenticator for JupyterHub",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jupyterhub/ldapauthenticator",
    author="Yuvi Panda",
    author_email="yuvipanda@riseup.net",
    license="3 Clause BSD",
    packages=["ldapauthenticator"],
    install_requires=["jupyterhub", "ldap3", "tornado", "traitlets"],
)
