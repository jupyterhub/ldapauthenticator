# ldapauthenticator
Simple LDAP Authenticator Plugin for JupyterHub

## Installation ##

You can install it from pip with:

```
pip install jupyterhub-ldapauthenticator
```

## Requirements ##

I've only tested with python3 - anyone willing to test with python2
is welcome to do so! There's no reason it shouldn't work.

## Logging people out ##

If you make any changes to JupyterHub's authentication setup that changes
which group of users is allowed to login (such as changing `allowed_groups`
or even just turning on LDAPAuthenticator), you *have* to change the
jupyterhub cookie secret, or users who were previously logged in and did
not log out would continue to be able to log in!

You can do this by deleting the `jupyterhub_cookie_secret` file. Note
that this will log out *all* users who are currently logged in.

## Usage ##

You can enable this authenticator with the folling lines in your
`jupyter_config.py`:

```python
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
```

### Required configuration ###

At least the following two configuration options must be set before
the LDAP Authenticator can be used:

#### `LDAPAuthenticator.server_address` ####

Address of the LDAP Server to contact. Just use a bare hostname or IP,
without a port name or protocol prefix.

#### `LDAPAuthenticator.bind_dn_template` #####

Template to use to generate the full dn for a user from the human readable
username. For example, if users in your LDAP database have DN of the form
`uid=Yuvipanda,ou=people,dc=wikimedia,dc=org` where Yuvipanda is the username,
you would set this config item to be:

```
c.LDAPAuthenticator.bind_dn_template = 'uid={username},ou=people,dc=wikimedia,dc=org'
```

Don't forget the preceeding `c.` for setting configuration parameters! JupyterHub
uses [traitlets](https://traitlets.readthedocs.io) for configuration, and the `c` represents the [config object](https://traitlets.readthedocs.io/en/stable/config.html).

The `{username}` is expanded into the username the user provides.

** Or you can use the following options if the dn is not static :**

#### `LDAPAuthenticator.use_search_dn` ####

Search the user on the server to get the full dn

#### `LDAPAuthenticator.search_dn_template` ####

The template to use for searching the user on the server

```
c.LDAPAuthenticator.search_dn_template = '(&(cn={username}))'
```

The `{username}` is expanded into the username the user provides.

### Optional configuration ###

#### `LDAPAuthenticator.allowed_groups` ####

LDAP groups whose members are allowed to log in. This must be
set to either empty `[]` (the default, to disable) or to a list of
full DNs that have a `member` attribute that includes the current
user attempting to log in.

As an example, to restrict access only to people in groups
`researcher` or `operations`,

```python
c.LDAPAuthenticator.allowed_groups = [
    'cn=researcher,ou=groups,dc=wikimedia,dc=org',
    'cn=operations,ou=groups,dc=wikimedia,dc=org'
]
```

#### `LDAPAuthenticator.valid_username_regex` ####

All usernames will be checked against this before being sent
to LDAP. This acts as both an easy way to filter out invalid
usernames as well as protection against LDAP injection attacks.

By default it looks for the regex `^[a-z][.a-z0-9_-]*$` which
is what most shell username validators do.

#### `LDAPAuthenticator.use_ssl` ####

Boolean to specify whether to use SSL encryption when contacting
the LDAP server. Highly recommended that this be left to `True`
(the default) unless there are very good reasons otherwise.

#### `LDAPAuthenticator.server_port` ####

Port to use to contact the LDAP server. Defaults to 389 if no SSL
is being used, and 636 is SSL is being used.

#### `LDAPAuthenticator.lookup_dn` ####

Whether to try a reverse lookup to obtain the user's DN.  Some LDAP servers,
such as Active Directory, don't always bind with the true DN, so this allows
us to discover it based on the username.

```python
c.LDAPAuthenticator.lookup_dn = True
```

#### `LDAPAuthenticator.user_search_base` ####

Only used with `lookup_dn=True`.  Defines the search base for looking up users
in the directory.

```python
c.LDAPAuthenticator.user_search_base = 'ou=People,dc=example,dc=com'
```

#### `LDAPAuthenticator.user_attribute` ####

Only used with `lookup_dn=True`.  Defines the attribute that stores a user's
username in your directory.

```python
# Active Directory
c.LDAPAuthenticator.user_attribute = 'sAMAccountName'

# OpenLDAP
c.LDAPAuthenticator.user_attribute = 'uid'
```

## Compatibility ##

This has been tested against an OpenLDAP server, with the client
running Python 3.4. Verifications of this code working well with
other LDAP setups welcome, as are bug reports and patches to make
it work with other LDAP setups!
