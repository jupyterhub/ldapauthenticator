# Inspired by https://github.com/jupyterhub/jupyterhub/blob/master/jupyterhub/tests/test_auth.py
from unittest.mock import Mock


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


async def test_ldap_auth_ssl(authenticator):
    authenticator.use_ssl = True
    authenticator.server_port = 636

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
    authenticator.use_lookup_dn_username = False


async def test_ldap_auth_search_filter(authenticator):
    authenticator.allowed_groups = []
    authenticator.search_filter = (
        "(&(objectClass=inetOrgPerson)(ou=	Delivering Crew)(cn={username}))"
    )

    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized["name"] == "fry"

    # proper username and password but not in search filter
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "zoidberg", "password": "zoidberg"}
    )
    assert authorized is None


async def test_ldap_auth_state_attributes(authenticator):
    authenticator.auth_state_attributes = ["employeeType"]
    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized["name"] == "fry"
    assert authorized["auth_state"] == {"employeeType": ["Delivery boy"]}


async def test_ldap_refresh_user(authenticator):
    authenticator.allowed_groups = [
        "cn=admin_staff,ou=people,dc=planetexpress,dc=com",
        "cn=ship_crew,ou=people,dc=planetexpress,dc=com",
    ]

    authenticator.enable_refresh = True
    mock = Mock()
    attrs = {"name": "zoidberg"}
    mock.configure_mock(**attrs)

    is_valid = await authenticator.refresh_user(mock, None)
    assert is_valid == False

    attrs = {"name": "leela"}
    mock.configure_mock(**attrs)

    is_valid = await authenticator.refresh_user(mock, None)
    assert is_valid == True


async def test_ldap_refresh_user_disabled(authenticator):
    authenticator.allowed_groups = [
        "cn=admin_staff,ou=people,dc=planetexpress,dc=com",
        "cn=ship_crew,ou=people,dc=planetexpress,dc=com",
    ]

    authenticator.enable_refresh = False
    mock = Mock()
    attrs = {"name": "zoidberg"}
    mock.configure_mock(**attrs)

    is_valid = await authenticator.refresh_user(mock, None)
    assert is_valid == True

    attrs = {"name": "leela"}
    mock.configure_mock(**attrs)

    is_valid = await authenticator.refresh_user(mock, None)
    assert is_valid == True
