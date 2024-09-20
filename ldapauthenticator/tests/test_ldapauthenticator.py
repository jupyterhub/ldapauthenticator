"""
Inspired by https://github.com/jupyterhub/jupyterhub/blob/main/jupyterhub/tests/test_auth.py

Testing data is hardcoded in docker-test-openldap, described at
https://github.com/rroemhild/docker-test-openldap?tab=readme-ov-file#ldap-structure
"""

import pytest
from ldap3.core.exceptions import LDAPSSLConfigurationError

from ..ldapauthenticator import TlsStrategy


async def test_ldap_auth_allowed(authenticator):
    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized["name"] == "fry"


async def test_ldap_auth_disallowed(authenticator):
    # invalid username
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "3fry/", "password": "raw"}
    )
    assert authorized is None

    # incorrect password
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "raw"}
    )
    assert authorized is None

    # blank password
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": ""}
    )
    assert authorized is None

    # nonexistant username
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "flexo", "password": "imposter"}
    )
    assert authorized is None

    # proper username and password but not in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "zoidberg", "password": "zoidberg"}
    )
    assert authorized is None


async def test_ldap_auth_blank_template(authenticator):
    authenticator.bind_dn_template = [authenticator.bind_dn_template, ""]

    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized["name"] == "fry"


async def test_ldap_use_ssl_deprecation(authenticator):
    assert authenticator.tls_strategy == TlsStrategy.before_bind

    # setting use_ssl to True should result in tls_strategy being set to
    # on_connect
    authenticator.use_ssl = True
    assert authenticator.tls_strategy == TlsStrategy.on_connect


async def test_ldap_auth_tls_strategy_on_connect(authenticator):
    """
    Verifies basic function of the authenticator with a given tls_strategy
    without actually confirming use of that strategy.
    """
    authenticator.tls_strategy = "on_connect"

    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized["name"] == "fry"


async def test_ldap_auth_tls_strategy_insecure(authenticator):
    """
    Verifies basic function of the authenticator with a given tls_strategy
    without actually confirming use of that strategy.
    """
    authenticator.tls_strategy = "insecure"

    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized["name"] == "fry"


async def test_ldap_auth_use_lookup_dn(authenticator):
    authenticator.use_lookup_dn_username = True

    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized["name"] == "philip j. fry"


async def test_ldap_auth_search_filter(authenticator):
    authenticator.allowed_groups = []
    authenticator.allow_all = True
    authenticator.search_filter = (
        "(&(objectClass=inetOrgPerson)(ou=	Delivering Crew)(cn={username}))"
    )

    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized is not None
    assert authorized["name"] == "fry"

    # proper username and password but not in search filter
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "zoidberg", "password": "zoidberg"}
    )
    assert authorized is None


async def test_allow_config(authenticator):
    # test various sources of allow config

    # this group allows fry, leela, bender
    authenticator.allowed_groups = ["cn=ship_crew,ou=people,dc=planetexpress,dc=com"]
    authenticator.allowed_users = {"zoidberg"}

    # in allowed_groups
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized is not None
    assert authorized["name"] == "fry"

    # in allowed_users
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "zoidberg", "password": "zoidberg"}
    )
    assert authorized is not None
    assert authorized["name"] == "zoidberg"

    # no match
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "professor", "password": "professor"}
    )
    assert authorized is None
    # allow_all grants access
    if hasattr(authenticator, "allow_all"):
        authenticator.allow_all = True
    else:
        # clear allow config for JupyterHub < 5
        authenticator.allowed_groups = []
        authenticator.allowed_users = set()
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "professor", "password": "professor"}
    )
    assert authorized is not None
    assert authorized["name"] == "professor"


async def test_ldap_auth_state_attributes(authenticator):
    authenticator.auth_state_attributes = ["employeeType"]
    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized["name"] == "fry"
    assert authorized["auth_state"]["user_attributes"] == {
        "employeeType": ["Delivery boy"]
    }


async def test_ldap_auth_state_attributes2(authenticator):
    authenticator.group_search_filter = "(cn=ship_crew)"
    authenticator.group_attributes = ["cn"]
    authenticator.auth_state_attributes = ["description"]
    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "leela", "password": "leela"}
    )
    assert authorized["name"] == "leela"
    assert authorized["auth_state"]["user_attributes"] == {"description": ["Mutant"]}


async def test_ldap_tls_kwargs_config_passthrough(authenticator):
    """
    This test is just meant to verify that tls_kwargs is passed through to the
    ldap3 Tls object when its constructed.
    """
    authenticator.tls_kwargs = {
        "ca_certs_file": "does-not-exist-so-error-expected",
    }
    with pytest.raises(LDAPSSLConfigurationError):
        await authenticator.get_authenticated_user(
            None, {"username": "leela", "password": "leela"}
        )
