import os

import pytest

from ..ldapauthenticator import LDAPAuthenticator


def pytest_collection_modifyitems(items):
    """add asyncio marker to all async tests"""
    for item in items:
        if inspect.iscoroutinefunction(item.obj):
            item.add_marker("asyncio")
        if hasattr(inspect, "isasyncgenfunction"):
            # double-check that we aren't mixing yield and async def
            assert not inspect.isasyncgenfunction(item.obj)


@pytest.fixture(scope="session")
def authenticator():
    authenticator = LDAPAuthenticator()
    authenticator.server_address = os.environ.get("LDAP_HOST", "localhost")
    authenticator.lookup_dn = True
    authenticator.bind_dn_template = "cn={username},ou=people,dc=planetexpress,dc=com"
    authenticator.user_search_base = "ou=people,dc=planetexpress,dc=com"
    authenticator.user_attribute = "uid"
    authenticator.lookup_dn_user_dn_attribute = "cn"
    authenticator.escape_userdn = True
    authenticator.attributes = ["uid", "cn", "mail", "ou"]
    authenticator.use_lookup_dn_username = False

    authenticator.allowed_groups = [
        "cn=admin_staff,ou=people,dc=planetexpress,dc=com",
        "cn=ship_crew,ou=people,dc=planetexpress,dc=com",
    ]

    return authenticator
