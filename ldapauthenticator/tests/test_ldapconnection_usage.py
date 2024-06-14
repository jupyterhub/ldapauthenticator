"""Tests the usage of both ldap connections of the ldap authenticator.
"""
import os
from unittest.mock import MagicMock, call, ANY
import pytest

from ..ldapauthenticator import LDAPAuthenticator


@pytest.fixture
def authenticator_setup():
    """Provides a configured and mocked authenticator as well as a mocked search and user connection.

    Note: don't be confused with the connection settings here, they just serve as valid configuration and are not used.
    """
    # configure authenticator
    authenticator = LDAPAuthenticator()
    authenticator.server_address = "localhost"
    authenticator.lookup_dn = False
    authenticator.bind_dn_template = "cn={username},ou=people,dc=planetexpress,dc=com"
    authenticator.user_search_base = "ou=people,dc=planetexpress,dc=com"
    authenticator.user_attribute = "uid"
    authenticator.lookup_dn_user_dn_attribute = "cn"
    authenticator.escape_userdn = True
    authenticator.attributes = ["uid", "cn", "mail", "ou"]
    authenticator.use_lookup_dn_username = False
    # leela is being authenticated, she's member of that group
    authenticator.allowed_groups = [
        "cn=ship_crew,ou=people,dc=planetexpress,dc=com",
    ]
    # search user is 'hermes'
    authenticator.lookup_dn_search_user = 'hermes'
    authenticator.lookup_dn_search_password = 'hermes'

    # mock ldap connections: return either the one for the search user or for the user to be authenticated
    connection_search_mock = MagicMock()
    connection_user_mock = MagicMock()
    def connection_mock(*args, **kwargs):
        if 'userdn' in kwargs and kwargs['userdn'] == 'hermes':
            return connection_search_mock
        else:
            return connection_user_mock
    authenticator.get_connection = MagicMock( side_effect = connection_mock )

    # 1) search: bind method should return True
    connection_search_mock.bind = MagicMock( return_value = True )

    # 2) search: lookup dn of user to be authenticated » deactivated

    # 3) user: bound should be False so that bind method is called returning True
    connection_user_mock.bound = False
    connection_user_mock.bind = MagicMock( return_value = True)

    # 4) user: search filter are empty » deactivated

    # 5) search or user: allowed groups » configured in test methods

    # 6) user: get_user_attributes(connection, userdn) » returns dict with entry attributes
    authenticator.get_user_attributes = MagicMock( return_value = { 'uid': 'leela', 'cn': 'Turanga Leela' } )

    return authenticator, connection_search_mock, connection_user_mock


async def test_allowed_groups_check_with_user_connection(authenticator_setup):
    """Checks the method calls on both ldap connections when the `allowed_groups` are check with the
    connection of the user being authenticated (default).
    """
    # unpack + assert object setup
    authenticator, connection_search_mock, connection_user_mock = authenticator_setup
    assert authenticator is not None and connection_search_mock is not None and connection_user_mock is not None
    assert authenticator.lookup_dn is False
    assert not authenticator.search_filter

    # assert default value
    assert authenticator.use_search_user_to_check_groups is False

    # 5) user: allowed groups » simply return True for the one group
    connection_user_mock.search = MagicMock( return_value = True )

    # authenticate leela
    result = await authenticator.authenticate( None, { 'username': 'leela', 'password': 'leela' } )
    assert 'name' in result
    assert result['name'] == 'leela'

    # assert method calls on mocks
    expected_search_mock_calls = [
        call.bind(),
    ]
    assert connection_search_mock.mock_calls == expected_search_mock_calls
    expected_user_mock_calls = [
        call.bind(),
        call.search('cn=ship_crew,ou=people,dc=planetexpress,dc=com', search_scope = ANY, search_filter = ANY, attributes = ANY)
    ]
    assert connection_user_mock.mock_calls == expected_user_mock_calls

async def test_allowed_groups_check_with_search_connection(authenticator_setup):
    """Checks the method calls on both ldap connections when the `allowed_groups` are check with the
    connection of the configured search user.
    """
    # unpack + assert object setup
    authenticator, connection_search_mock, connection_user_mock = authenticator_setup
    assert authenticator is not None and connection_search_mock is not None and connection_user_mock is not None
    assert authenticator.lookup_dn is False
    assert not authenticator.search_filter

    # enable allowed groups check using the search user connection
    authenticator.use_search_user_to_check_groups = True

    # 5) search: allowed groups » simply return True for the one group
    connection_search_mock.search = MagicMock( return_value = True )

    # authenticate leela
    result = await authenticator.authenticate( None, { 'username': 'leela', 'password': 'leela' } )
    assert 'name' in result
    assert result['name'] == 'leela'

    # assert method calls on mocks
    expected_search_mock_calls = [
        call.bind(),
        call.search('cn=ship_crew,ou=people,dc=planetexpress,dc=com', search_scope = ANY, search_filter = ANY, attributes = ANY)
    ]
    assert connection_search_mock.mock_calls == expected_search_mock_calls
    expected_user_mock_calls = [
        call.bind(),
    ]
    assert connection_user_mock.mock_calls == expected_user_mock_calls
