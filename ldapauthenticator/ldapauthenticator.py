import ldap3
import re
from jupyterhub.auth import Authenticator

from tornado import gen
from traitlets import Unicode, Int, Bool, Union, List


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

    use_ntlm = Bool(
        True,
        config=True,
        help='Use the NTLM authentication protocol'
    )

    use_ssl = Bool(
        True,
        config=True,
        help='Use SSL to encrypt connection to LDAP server'
    )

    bind_dn_template = Unicode(
        config=True,
        help="""
        Template from which to construct the full dn
        when authenticating to LDAP. {username} is replaced
        with the actual username.

        Example:

            uid={username},ou=people,dc=wikimedia,dc=org
        """
    )


    allowed_groups = List(
	config=True,
	help="List of LDAP Group DNs whose members are allowed access"
    )

    valid_username_regex = Unicode(
        r'^[a-z][.a-z0-9_-]*$',
        config=True,
        help="""Regex to use to validate usernames before sending to LDAP

        Also acts as a security measure to prevent LDAP injection. If you
        are customizing this, be careful to ensure that attempts to do LDAP
        injection are rejected by your customization
        """
    )

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']
        password = data['password']

        # Protect against invalid usernames as well as LDAP injection attacks
        if not re.match(self.valid_username_regex, username):
            self.log.warn('Invalid username')
            return None

        # No empty passwords!
        if password is None or password.strip() == '':
            self.log.warn('Empty password')
            return None

        userdn = self.bind_dn_template.format(username=username)

        server = ldap3.Server(
            self.server_address,
            port=self.server_port,
            use_ssl=self.use_ssl
        )
        if self.use_ntlm:
            conn = ldap3.Connection(server, user=userdn, password=password, authentication=ldap3.NTLM)
            self.log.info("using NTLM authentication protocol")
        else:
            conn = ldap3.Connection(server, user=userdn, password=password)

        if conn.bind():
            if self.allowed_groups:
                for group in self.allowed_groups:
                    if conn.search(
                        group,
                        search_scope=ldap3.BASE,
                        search_filter='(member={userdn})'.format(userdn=userdn),
                        attributes=['member']
                    ):
                        return username
            else:
                return username
        else:
            self.log.warn('Invalid password')
            return None
