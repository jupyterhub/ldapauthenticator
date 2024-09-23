# ldapauthenticator

[![Latest PyPI version](https://img.shields.io/pypi/v/jupyterhub-ldapauthenticator?logo=pypi)](https://pypi.python.org/pypi/jupyterhub-ldapauthenticator)
[![Latest conda-forge version](https://img.shields.io/conda/vn/conda-forge/jupyterhub-ldapauthenticator?logo=conda-forge)](https://anaconda.org/conda-forge/jupyterhub-ldapauthenticator)
[![GitHub Workflow Status - Test](https://img.shields.io/github/actions/workflow/status/jupyterhub/ldapauthenticator/test.yaml?logo=github&label=tests)](https://github.com/jupyterhub/ldapauthenticator/actions)
[![Test coverage of code](https://codecov.io/gh/jupyterhub/ldapauthenticator/branch/main/graph/badge.svg)](https://codecov.io/gh/jupyterhub/ldapauthenticator)
[![Issue tracking - GitHub](https://img.shields.io/badge/issue_tracking-github-blue?logo=github)](https://github.com/jupyterhub/ldapauthenticator/issues)
[![Help forum - Discourse](https://img.shields.io/badge/help_forum-discourse-blue?logo=discourse)](https://discourse.jupyter.org/c/jupyterhub)

Simple LDAP Authenticator Plugin for JupyterHub

## Installation

You can install it from pip with:

```
pip install jupyterhub-ldapauthenticator
```

...or using conda with:

```
conda install -c conda-forge jupyterhub-ldapauthenticator
```

## Logging people out

If you make any changes to JupyterHub's authentication setup that changes
which group of users is allowed to login (such as changing `allowed_groups`
or even just turning on LDAPAuthenticator), you **must** change the
jupyterhub cookie secret, or users who were previously logged in and did
not log out would continue to be able to log in!

You can do this by deleting the `jupyterhub_cookie_secret` file. Note
that this will log out _all_ users who are currently logged in.

## Usage

You can enable this authenticator by adding lines to your `jupyterhub_config.py`.

**Note: This file may not exist in your current installation! In TLJH, it
is located in /opt/tljh/config/jupyterhub_config.d. Create it there if you
don't already have one.**

```python
c.JupyterHub.authenticator_class = 'ldap'
```

### Required configuration

At minimum, the following two configuration options must be set before
the LDAP Authenticator can be used:

#### `LDAPAuthenticator.server_address`

Address of the LDAP Server to contact. Just use a bare hostname or IP,
without a port name or protocol prefix.

#### `LDAPAuthenticator.lookup_dn` or `LDAPAuthenticator.bind_dn_template`

To authenticate a user we need the corresponding DN to bind against the LDAP server. The DN can be acquired by either:

1. setting `bind_dn_template`, which is a list of string template used to
   generate the full DN for a user from the human readable username, or
2. setting `lookup_dn` to `True`, which does a reverse lookup to obtain the
   user's DN. This is because some LDAP servers, such as Active Directory, don't
   always bind with the true DN.

##### `lookup_dn = False`

If `lookup_dn = False`, then `bind_dn_template` is required to be a non-empty
list of templates the users belong to. For example, if some of the users in your
LDAP database have DN of the form `uid=Yuvipanda,ou=people,dc=wikimedia,dc=org`
and some other users have DN like `uid=Mike,ou=developers,dc=wikimedia,dc=org`
where `Yuvipanda` and `Mike` are the usernames, you would set this config item
to be:

```python
c.LDAPAuthenticator.bind_dn_template = [
    "uid={username},ou=people,dc=wikimedia,dc=org",
    "uid={username},ou=developers,dc=wikimedia,dc=org",
]
```

Don't forget the preceeding `c.` for setting configuration parameters! JupyterHub
uses [traitlets](https://traitlets.readthedocs.io) for configuration, and the
`c` represents the [config object](https://traitlets.readthedocs.io/en/stable/config.html).

The `{username}` is expanded into the username the user provides.

##### `lookup_dn = True`

```python
c.LDAPAuthenticator.lookup_dn = True
```

If `bind_dn_template` isn't explicitly configured, i.e. the empty list, the
dynamically acquired value for DN from the username lookup will be used
instead. If `bind_dn_template` is configured it will be used just like in the
`lookup_dn = False` case.

The `{username}` is expanded to the full path to the LDAP object returned by the
LDAP lookup. For example, on an Active Directory system `{username}` might
expand to something like `CN=First M. Last,OU=An Example Organizational
Unit,DC=EXAMPLE,DC=COM`.

Also, when using `lookup_dn = True` the options `user_search_base`,
`user_attribute`, `lookup_dn_user_dn_attribute` and `lookup_dn_search_filter`
are required, although their defaults might be sufficient for your use case.

### Optional configuration

#### `LDAPAuthenticator.allowed_groups`

LDAP groups whose members are allowed to log in. This must be
set to either empty `[]` (the default, to disable) or to a list of
full DNs that have a `member` attribute that includes the current
user attempting to log in.

As an example, to restrict access only to people in groups
`researcher` or `operations`,

```python
c.LDAPAuthenticator.allowed_groups = [
    "cn=researcher,ou=groups,dc=wikimedia,dc=org",
    "cn=operations,ou=groups,dc=wikimedia,dc=org",
]
```

#### `LDAPAuthenticator.group_search_filter`

The LDAP group search filter.

The default value is an LDAP OR search that looks like the following:

```
(|(member={userdn})(uniqueMember={userdn})(memberUid={uid}))
```

So it basically compares the `userdn` attribute against the `member` attribute,
then against the `uniqueMember`, and finally checks the `memberUid` against
the `uid`.

If you modify this value, you probably want to change `group_attributes` too.
Here is an example that should work with OpenLDAP servers.

```
(member={userdn})
```

#### `LDAPAuthenticator.group_attributes`

A list of attributes used when searching for LDAP groups.

By default, it uses `member`, `uniqueMember`, and `memberUid`. Certain
servers may reject invalid values causing exceptions during
authentication.

#### `LDAPAuthenticator.valid_username_regex`

All usernames will be checked against this before being sent
to LDAP. This acts as both an easy way to filter out invalid
usernames as well as protection against LDAP injection attacks.

By default it looks for the regex `^[a-z][.a-z0-9_-]*$` which
is what most shell username validators do.

#### `LDAPAuthenticator.use_ssl`

`use_ssl` is deprecated since 2.0. `use_ssl=True` translates to configuring
`tls_strategy="on_connect"`, but `use_ssl=False` (previous default) doesn't
translate to anything.

#### `LDAPAuthenticator.tls_strategy`

When LDAPAuthenticator connects to the LDAP server, it can establish a
SSL/TLS connection directly, or do it before binding, which is LDAP
terminology for authenticating and sending sensitive credentials.

The LDAP v3 protocol deprecated establishing a SSL/TLS connection
directly (`tls_strategy="on_connect"`) in favor of upgrading the
connection to SSL/TLS before binding (`tls_strategy="before_bind"`).

Supported `tls_strategy` values are:

- "before_bind" (default)
- "on_connect" (deprecated in LDAP v3, associated with use of port 636)
- "insecure"

When configuring `tls_strategy="on_connect"`, the default value of
`server_port` becomes 636.

#### `LDAPAuthenticator.tls_kwargs`

A dictionary that will be used as keyword arguments for the constructor
of the ldap3 package's Tls object, influencing encrypted connections to
the LDAP server.

For details on what can be configured and its effects, refer to the
ldap3 package's documentation and code:

- ldap3 documentation: https://ldap3.readthedocs.io/en/latest/ssltls.html#the-tls-object
- ldap3 code: https://github.com/cannatag/ldap3/blob/v2.9.1/ldap3/core/tls.py#L59-L82

You can for example configure this like:

```python
c.LDAPAuthenticator.tls_kwargs = {
    "ca_certs_file": "file/path.here",
}
```

#### `LDAPAuthenticator.server_port`

Port on which to contact the LDAP server.

Defaults to `636` if `tls_strategy="on_connect"` is set, `389`
otherwise.

#### `LDAPAuthenticator.user_search_base`

Only used with `lookup_dn=True` or with a configured `search_filter`.

Defines the search base for looking up users in the directory.

```python
c.LDAPAuthenticator.user_search_base = 'ou=People,dc=example,dc=com'
```

LDAPAuthenticator will search all objects matching under this base where
the `user_attribute` is set to the current username to form the userdn.

For example, if all users objects existed under the base
`ou=people,dc=wikimedia,dc=org`, and the username users use is set with
the attribute `uid`, you can use the following config:

```python
c.LDAPAuthenticator.lookup_dn = True
c.LDAPAuthenticator.lookup_dn_search_filter = '({login_attr}={login})'
c.LDAPAuthenticator.lookup_dn_search_user = 'ldap_search_user_technical_account'
c.LDAPAuthenticator.lookup_dn_search_password = 'secret'
c.LDAPAuthenticator.user_search_base = 'ou=people,dc=wikimedia,dc=org'
c.LDAPAuthenticator.user_attribute = 'uid'
c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'cn'
```

#### `LDAPAuthenticator.user_attribute`

Only used with `lookup_dn=True`. Defines the attribute that stores a user's
username in your directory.

```python
# Active Directory
c.LDAPAuthenticator.user_attribute = 'sAMAccountName'

# OpenLDAP
c.LDAPAuthenticator.user_attribute = 'uid'
```

#### `LDAPAuthenticator.lookup_dn_search_filter`

How to query LDAP for user name lookup, if `lookup_dn` is set to True.
Default value `'({login_attr}={login})'` should be good enough for most use cases.

#### `LDAPAuthenticator.lookup_dn_search_user`, `LDAPAuthenticator.lookup_dn_search_password`

Technical account for user lookup, if `lookup_dn` is set to True.
If both lookup_dn_search_user and lookup_dn_search_password are None, then anonymous LDAP query will be done.

#### `LDAPAuthenticator.lookup_dn_user_dn_attribute`

Attribute containing user's name needed for building DN string, if `lookup_dn` is set to True.
See `user_search_base` for info on how this attribute is used.
For most LDAP servers, this is username. For Active Directory, it is cn.

#### `LDAPAuthenticator.auth_state_attributes`

An optional list of attributes to be fetched for a user after login.
If found, these will be available as `auth_state["user_attributes"]`.

#### `LDAPAuthenticator.use_lookup_dn_username`

If set to True (the default) the username used to build the DN string is returned as the username when `lookup_dn` is True.

When authenticating on a Linux machine against an AD server this might return something different from the supplied UNIX username. In this case setting this option to False might be a solution.

#### `LDAPAuthenticator.search_filter`

LDAP3 Search Filter to limit allowed users.

That a unique LDAP user is identified with the search_filter is
necessary but not sufficient to grant access. Grant access by setting
one or more of `allowed_users`, `allow_all`, `allowed_groups`, etc.

Users who do not match this filter cannot be allowed
by any other configuration.

The search filter string will be expanded, so that:

- `{userattr}` is replaced with the `user_attribute` config's value.
- `{username}` is replaced with an escaped username, either provided
  directly or previously looked up with `lookup_dn` configured.

#### `LDAPAuthenticator.attributes`

List of attributes to be passed in the LDAP search with `search_filter`.

## Compatibility

This has been tested against an OpenLDAP server, with the client
running Python 3.4. Verifications of this code working well with
other LDAP setups are welcome, as are bug reports and patches to make
it work with other LDAP setups!

## Active Directory integration

Please use following options for AD integration. This is useful especially in two cases:

- LDAP Search requires valid user account in order to query user database
- DN does not contain login but some other field, like CN (actual login is present in sAMAccountName, and we need to lookup CN)

```python
c.LDAPAuthenticator.lookup_dn = True
c.LDAPAuthenticator.lookup_dn_search_filter = '({login_attr}={login})'
c.LDAPAuthenticator.lookup_dn_search_user = 'ldap_search_user_technical_account'
c.LDAPAuthenticator.lookup_dn_search_password = 'secret'
c.LDAPAuthenticator.user_search_base = 'ou=people,dc=wikimedia,dc=org'
c.LDAPAuthenticator.user_attribute = 'sAMAccountName'
c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'cn'
```

In setup above, first LDAP will be searched (with account ldap_search_user_technical_account) for users that have sAMAccountName=login
Then DN will be constructed using found CN value.

## Configuration note on local user creation

Currently, local user creation by the LDAPAuthenticator is unsupported as
this is insecure since there's no cleanup method for these created users. As a
result, users who are disabled in LDAP will have access to this for far longer.

Alternatively, there's good support in Linux for integrating LDAP into the
system user setup directly, and users can just use PAM (which is supported in
not just JupyterHub, but ssh and a lot of other tools) to log in. You can see
http://www.tldp.org/HOWTO/archived/LDAP-Implementation-HOWTO/pamnss.html and
lots of other documentation on the web on how to set up LDAP to provide user
accounts for your system. Those methods are very widely used, much more secure
and more widely documented. We recommend you use them rather than have
JupyterHub create local accounts using the LDAPAuthenticator.

Issue [#19](https://github.com/jupyterhub/ldapauthenticator/issues/19) provides
additional discussion on local user creation.

## Testing LDAPAuthenticator without JupyterHub

This script can be written to a file such as `test_ldap_auth.py`, and run with
`python test_ldap_auth.py`, to test use of LDAPAuthenticator with a given config
without involving JupyterHub.

If the authenticator works, this script should print either None or a username
depending if the user was considered allowed access.

```python
import asyncio
import getpass

from traitlets.config import Config
from ldapauthenticator import LDAPAuthenticator

# Configure LDAPAuthenticator below to work against your ldap server
c = Config()
c.LDAPAuthenticator.server_address = "ldap.organisation.org"
c.LDAPAuthenticator.server_port = 636
c.LDAPAuthenticator.bind_dn_template = "uid={username},ou=people,dc=organisation,dc=org"
c.LDAPAuthenticator.user_attribute = "uid"
c.LDAPAuthenticator.user_search_base = "ou=people,dc=organisation,dc=org"
c.LDAPAuthenticator.attributes = ["uid", "cn", "mail", "ou", "o"]
# The following is an example of a search_filter which is build on LDAP AND and OR operations
# here in this example as a combination of the LDAP attributes 'ou', 'mail' and 'uid'
sf = "(&(o={o})(ou={ou}))".format(o="yourOrganisation", ou="yourOrganisationalUnit")
sf += "(&(o={o})(mail={mail}))".format(o="yourOrganisation", mail="yourMailAddress")
c.LDAPAuthenticator.search_filter = f"(&({{userattr}}={{username}})(|{sf}))"

# Run test
authenticator = LDAPAuthenticator(config=c)
username = input("Username: ")
password = getpass.getpass()
data = dict(username=username, password=password)
return_value = asyncio.run(authenticator.authenticate(None, data))
print(return_value)
```
