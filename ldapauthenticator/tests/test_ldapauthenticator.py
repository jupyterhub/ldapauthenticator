# Inspired by https://github.com/jupyterhub/jupyterhub/blob/master/jupyterhub/tests/test_auth.py


async def test_ldap_auth_allowed(authenticator):
    # proper username and password in allowed group
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert authorized["name"] == "fry"

    # allowed user with proper credentials not in admin_groups
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "fry", "password": "fry"}
    )
    assert not authorized.get("admin", True)

    # allowed user with proper credentials not in admin_groups
    authorized = await authenticator.get_authenticated_user(
        None, {"username": "hermes", "password": "hermes"}
    )
    assert authorized.get("admin", False)


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
