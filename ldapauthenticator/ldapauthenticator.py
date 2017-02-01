import ldap3
import re

from jupyterhub.auth import Authenticator
from tornado import gen
from traitlets import Unicode, Int, Bool, Union, List


class LDAPAuthenticator(Authenticator):
    server_address = Unicode(
        config=True,
        help="""
        Address of the LDAP server to contact.

        Could be an IP address or hostname.
        """
    )
    server_port = Int(
        config=True,
        help="""
        Port on which to contact the LDAP server.

        Defaults to `636` if `use_ssl` is set, `389` otherwise.
        """
    )

    def _server_port_default(self):
        if self.use_ssl:
            return 636  # default SSL port for LDAP
        else:
            return 389  # default plaintext port for LDAP

    use_ssl = Bool(
        True,
        config=True,
        help="""
        Use SSL to communicate with the LDAP server.

        Highly recommended! Your LDAP server must be configured to support this, however.
        """
    )

    bind_dn_template = Union(
        [List(),Unicode()],
        config=True,
        help="""
        Template from which to construct the full dn
        when authenticating to LDAP. {username} is replaced
        with the actual username used to log in.

        If your LDAP is set in such a way that the userdn can not
        be formed from a template, but must be looked up with an attribute
        (such as uid or sAMAccountName), please see `lookup_dn`. It might
        be particularly relevant for ActiveDirectory installs.

        Unicode Example:
            uid={username},ou=people,dc=wikimedia,dc=org
        
        List Example:
            [
            	uid={username},ou=people,dc=wikimedia,dc=org,
            	uid={username},ou=Developers,dc=wikimedia,dc=org
        	]
        """
    )

    allowed_groups = List(
        config=True,
        allow_none=True,
        default=None,
        help="""
        List of LDAP group DNs that users could be members of to be granted access.

        If a user is in any one of the listed groups, then that user is granted access.
        Membership is tested by fetching info about each group and looking for the User's
        dn to be a value of one of `member` or `uniqueMember`, *or* if the username being
        used to log in with is value of the `uid`.

        Set to an empty list or None to allow all users that have an LDAP account to log in,
        without performing any group membership checks.
        """
    )

    # FIXME: Use something other than this? THIS IS LAME, akin to websites restricting things you
    # can use in usernames / passwords to protect from SQL injection!
    valid_username_regex = Unicode(
        r'^[a-z][.a-z0-9_-]*$',
        config=True,
        help="""
        Regex for validating usernames - those that do not match this regex will be rejected.

        This is primarily used as a measure against LDAP injection, which has fatal security
        considerations. The default works for most LDAP installations, but some users might need
        to modify it to fit their custom installs. If you are modifying it, be sure to understand
        the implications of allowing additional characters in usernames and what that means for
        LDAP injection issues. See https://www.owasp.org/index.php/LDAP_injection for an overview
        of LDAP injection.
        """
    )

    lookup_dn = Bool(
        False,
        config=True,
        help="""
        Form user's DN by looking up an entry from directory

        By default, LDAPAuthenticator finds the user's DN by using `bind_dn_template`.
        However, in some installations, the user's DN does not contain the username, and
        hence needs to be looked up. You can set this to True and then use `user_search_base`
        and `user_attribute` to accomplish this.
        """
    )

    user_search_base = Unicode(
        config=True,
        default=None,
        allow_none=True,
        help="""
        Base for looking up user accounts in the directory, if `lookup_dn` is set to True.

        LDAPAuthenticator will search all objects matching under this base where the `user_attribute`
        is set to the current username to form the userdn.

        For example, if all users objects existed under the base ou=people,dc=wikimedia,dc=org, and
        the username users use is set with the attribute `uid`, you can use the following config:

        ```
        c.LDAPAuthenticator.lookup_dn = True
        c.LDAPAuthenticator.user_search_base = 'ou=people,dc=wikimedia,dc=org'
        c.LDAPAuthenticator.user_attribute = 'uid'
        ```
        """
    )

    user_attribute = Unicode(
        config=True,
        default=None,
        allow_none=True,
        help="""
        Attribute containing user's name, if `lookup_dn` is set to True.

        See `user_search_base` for info on how this attribute is used.

        For most LDAP servers, this is uid.  For Active Directory, it is
        sAMAccountName.
        """
    )

    lookup_by_login = Bool(
        default_value=False,
        config=True,
        help="""
        If set to True, then execute LDAP query to get proper DN.

        This can be used to translate sAMAccountName to CN in AciveDirectory using custom query.
        If lookup_by_login_search_user and lookup_by_login_search_password then query is performed using specified user.
        This is required if ActiveDirectory has disabled anonymous search.

        Example setup:

        c.LDAPAuthenticator.lookup_by_login = True
        c.LDAPAuthenticator.lookup_by_login_search_base = 'DC=company,DC=com'
        c.LDAPAuthenticator.lookup_by_login_search_filter = '({login_attr}={login})'
        c.LDAPAuthenticator.lookup_by_login_search_user = 'ldap_search_user'
        c.LDAPAuthenticator.lookup_by_login_search_password = 'secret'
        c.LDAPAuthenticator.lookup_by_login_ldap_login_attribute = 'sAMAccountName'
        c.LDAPAuthenticator.lookup_by_login_ldap_username_attribute = 'CN'
        """
    )

    lookup_by_login_search_base = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help=""""""
    )

    lookup_by_login_search_filter = Unicode(
        config=True,
        default_value='({login_attr}={login})',
        allow_none=True,
        help=""""""
    )

    lookup_by_login_search_user = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help=""""""
    )

    lookup_by_login_search_password = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help=""""""
    )

    lookup_by_login_ldap_login_attribute = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help=""""""
    )

    lookup_by_login_ldap_username_attribute = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help=""""""
    )

    def resolve_username(self, username_supplied_by_user):
        if self.lookup_by_login:
            server = ldap3.Server(
                self.server_address,
                port=self.server_port,
                use_ssl=self.use_ssl
            )

            search_filter = self.lookup_by_login_search_filter.format(
                login_attr=self.lookup_by_login_ldap_login_attribute,
                login=username_supplied_by_user
            )
            self.log.debug(
                "Looking up user with search_base={search_base}, search_filter='{search_filter}', attributes={attributes}".format(
                    search_base=self.lookup_by_login_search_base,
                    search_filter=search_filter,
                    attributes=self.lookup_by_login_ldap_username_attribute
                )
            )

            conn = ldap3.Connection(server, user=self.lookup_by_login_search_user, password=self.lookup_by_login_search_password)
            is_bound = conn.bind()
            if not is_bound:
                self.log.warn("Can't connect to LDAP")
                return None

            conn.search(
                search_base=self.lookup_by_login_search_base,
                search_scope=ldap3.SUBTREE,
                search_filter=search_filter,
                attributes=[self.lookup_by_login_ldap_username_attribute]
            )

            if len(conn.response) == 0:
                self.log.warn('username:%s No such user entry found when looking up with attribute %s', username_supplied_by_user,
                              self.lookup_by_login_ldap_login_attribute)
                return None
            return conn.response[0]['attributes'][self.lookup_by_login_ldap_username_attribute]
        else:
            return username_supplied_by_user

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']
        password = data['password']
        # Get LDAP Connection
        def getConnection(userdn, username, password):
            server = ldap3.Server(
                self.server_address,
                port=self.server_port,
                use_ssl=self.use_ssl
            )
            self.log.debug('Attempting to bind {username} with {userdn}'.format(
                    username=username,
                    userdn=userdn
            ))
            conn = ldap3.Connection(server, user=userdn, password=password)
            return conn
        
        # Protect against invalid usernames as well as LDAP injection attacks
        if not re.match(self.valid_username_regex, username):
            self.log.warn('username:%s Illegal characters in username, must match regex %s', username, self.valid_username_regex)
            return None

        # No empty passwords!
        if password is None or password.strip() == '':
            self.log.warn('username:%s Login denied for blank password', username)
            return None
        
        isBound = False
        self.log.debug("TYPE= '%s'",isinstance(self.bind_dn_template, list))
        # In case, there are multiple binding templates
        if isinstance(self.bind_dn_template, list):
            for dn in self.bind_dn_template:
                userdn = dn.format(username=self.resolve_username(username))
                conn = getConnection(userdn, username, password)
                isBound = conn.bind()
                self.log.debug('Status of user bind {username} with {userdn} : {isBound}'.format(
                    username=username,
                    userdn=userdn,
                    isBound=isBound
                ))                
                if isBound:
                    break
        else:
            userdn = self.bind_dn_template.format(username=self.resolve_username(username))
            conn = getConnection(userdn, username, password)
            isBound = conn.bind()

        if isBound:
            if self.allowed_groups:
                if self.lookup_dn:
                    # In some cases, like AD, we don't bind with the DN, and need to discover it.
                    conn.search(
                        search_base=self.user_search_base,
                        search_scope=ldap3.SUBTREE,
                        search_filter='({userattr}={username})'.format(
                            userattr=self.user_attribute,
                            username=username
                        ),
                        attributes=[self.user_attribute]
                    )

                    if len(conn.response) == 0:
                        self.log.warn('username:%s No such user entry found when looking up with attribute %s', username, self.user_attribute)
                        return None
                    userdn = conn.response[0]['dn']

                self.log.debug('username:%s Using dn %s', username, userdn)
                for group in self.allowed_groups:
                    groupfilter = (
                        '(|'
                        '(member={userdn})'
                        '(uniqueMember={userdn})'
                        '(memberUid={uid})'
                        ')'
                    ).format(userdn=userdn, uid=username)
                    groupattributes = ['member', 'uniqueMember', 'memberUid']
                    if conn.search(
                        group,
                        search_scope=ldap3.BASE,
                        search_filter=groupfilter,
                        attributes=groupattributes
                    ):
                        return username
                # If we reach here, then none of the groups matched
                self.log.warn('username:%s User not in any of the allowed groups', username)
                return None
            else:
                return username
        else:
            self.log.warn('Invalid password for user {username}'.format(
                username=userdn,
            ))
            return None
