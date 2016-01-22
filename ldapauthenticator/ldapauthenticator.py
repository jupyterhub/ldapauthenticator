import ldap3
from jupyterhub.auth import Authenticator

from tornado import gen
from traitlets import Unicode, Int, Bool


class LDAPAuthenticator(Authenticator):
    server_address = Unicode(
        config=True,
        help='Address of LDAP server to contact'
    )
    server_port = Int(
        config=True,
        help='Port on which to contact LDAP server',
    )

    def _server_port_default(self):
        if self.use_ssl:
            return 636  # default SSL port for LDAP
        else:
            return 389  # default plaintext port for LDAP

    use_ssl = Bool(
        True,
        config=True,
        help='Use SSL to encrypt connection to LDAP server'
    )
    username_template = Unicode(
        config=True,
        help="""
        Template from which to construct the full username
        when authenticating to LDAP. {username} is replaced
        with the actual username.

        Example:

            uid={username},ou=people,dc=wikimedia,dc=org
        """
    )

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']
        password = data['password']

        full_dn = self.username_template.format(username=username)

        server = ldap3.Server(
            self.server_address,
            port=self.server_port,
            use_ssl=self.use_ssl
        )
        conn = ldap3.Connection(server, user=full_dn, password=password)

        if conn.bind():
            return username
        else:
            return None
