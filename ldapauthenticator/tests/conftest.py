import os

import pytest
from traitlets.config import Config


@pytest.fixture()
def c():
    """
    A base configuration for LDAPAuthenticator that individual tests can adjust.
    """
    c = Config()
    c.LDAPAuthenticator.server_address = os.environ.get("LDAP_HOST", "localhost")
    c.LDAPAuthenticator.lookup_dn = True
    c.LDAPAuthenticator.bind_dn_template = (
        "cn={username},ou=people,dc=planetexpress,dc=com"
    )
    c.LDAPAuthenticator.user_search_base = "ou=people,dc=planetexpress,dc=com"
    c.LDAPAuthenticator.user_attribute = "uid"
    c.LDAPAuthenticator.lookup_dn_user_dn_attribute = "cn"
    c.LDAPAuthenticator.attributes = ["uid", "cn", "mail", "ou"]
    c.LDAPAuthenticator.use_lookup_dn_username = False

    c.LDAPAuthenticator.allowed_groups = [
        "cn=admin_staff,ou=people,dc=planetexpress,dc=com",
        "cn=ship_crew,ou=people,dc=planetexpress,dc=com",
    ]

    return c
