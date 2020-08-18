import re

import ldap3
from jupyterhub.auth import Authenticator
from ldap3.utils.conv import escape_filter_chars
from tornado import gen
from traitlets import Bool
from traitlets import Int
from traitlets import List
from traitlets import Unicode
from traitlets import Union


class LDAPAuthenticator(Authenticator):
    server_address = Unicode(
        config=True,
        help="""
        Address of the LDAP server to contact.

        Could be an IP address or hostname.
        """,
    )
    server_port = Int(
        config=True,
        help="""
        Port on which to contact the LDAP server.

        Defaults to `636` if `use_ssl` is set, `389` otherwise.
        """,
    )

    def _server_port_default(self):
        if self.use_ssl:
            return 636  # default SSL port for LDAP
        else:
            return 389  # default plaintext port for LDAP

    use_ssl = Bool(
        False,
        config=True,
        help="""
        Use SSL to communicate with the LDAP server.

        Deprecated in version 3 of LDAP. Your LDAP server must be configured to support this, however.
        """,
    )

    bind_dn_template = Union(
        [List(), Unicode()],
        config=True,
        help="""
        Template from which to construct the full dn
        when authenticating to LDAP. {username} is replaced
        with the user's resolved username (i.e. their CN attribute).
        {login} is replaced with the actual username used to login.

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

        Active Directory Example:
            DOMAIN\{login}
        """,
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
        """,
    )

    # FIXME: Use something other than this? THIS IS LAME, akin to websites restricting things you
    # can use in usernames / passwords to protect from SQL injection!
    valid_username_regex = Unicode(
        r"^[a-z][.a-z0-9_-]*$",
        config=True,
        help="""
        Regex for validating usernames - those that do not match this regex will be rejected.

        This is primarily used as a measure against LDAP injection, which has fatal security
        considerations. The default works for most LDAP installations, but some users might need
        to modify it to fit their custom installs. If you are modifying it, be sure to understand
        the implications of allowing additional characters in usernames and what that means for
        LDAP injection issues. See https://www.owasp.org/index.php/LDAP_injection for an overview
        of LDAP injection.
        """,
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
        """,
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
        c.LDAPAuthenticator.lookup_dn_search_filter = '({login_attr}={login})'
        c.LDAPAuthenticator.lookup_dn_search_user = 'ldap_search_user_technical_account'
        c.LDAPAuthenticator.lookup_dn_search_password = 'secret'
        c.LDAPAuthenticator.user_search_base = 'ou=people,dc=wikimedia,dc=org'
        c.LDAPAuthenticator.user_attribute = 'sAMAccountName'
        c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'cn'
        c.LDAPAuthenticator.bind_dn_template = '{username}'
        ```
        """,
    )

    group_search_base = Unicode(
        config=True,
        default=user_search_base,
        allow_none=True,
        help="""
        Base for looking up groups in the directory. Defaults to the value of user_search_base if unset.

        For example:
        ```
        c.LDAPAuthenticator.group_search_base = 'ou=groups,dc=wikimedia,dc=org'
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
        """,
    )

    memberof_attribute = Unicode(
        config=True,
        default_value='memberOf',
        allow_none=False,
        help="""
        Attribute attached to user objects containing the list of groups the user is a member of.

        Defaults to 'memberOf', you probably won't need to change this.
        """
    )

    get_groups_from_user = Bool(
        False,
        config=True,
        help="""
        If set, this will confirm a user's group membership by querying the
        user object in LDAP directly, and querying the attribute set in
        `memberof_attribute` (defaults to `memberOf`).

        If unset (the default), then each authorised group set in
        `allowed_group` is queried from LDAP and matched against the user's DN.

        This should be set when the LDAP server is Microsoft Active Directory,
        and you probably also want to set the `activedirectory` configuration
        setting to 'true' as well'
        """
    )

    activedirectory = Bool(
        False,
        config=True,
        help="""
        If set, this treats the remote LDAP server as a Microsoft Active
        Directory instance, and will optimise group membership queries where
        `allow_groups` is used. This requires `get_groups_from_user` to be
        enabled.

        This allows nested groups to be resolved when using Active Directory.

        Example Active Directory configuration:
        ```
        c.LDAPAuthenticator.bind_dn_template = 'DOMAIN\{login}'
        c.LDAPAuthenticator.lookup_dn = False
        c.LDAPAuthenticator.activedirectory = True
        c.LDAPAuthenticator.get_groups_from_user = True
        c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'distinguishedName'
        c.LDAPAuthenticator.lookup_dn_search_filter = '({login_attr}={login})'
        c.LDAPAuthenticator.lookup_dn_search_user = 'readonly'
        c.LDAPAuthenticator.lookup_dn_search_password = 'notarealpassword'
        c.LDAPAuthenticator.user_attribute = 'sAMAccountName'
        c.LDAPAuthenticator.user_search_base = 'OU=Users,DC=example,DC=org'
        c.LDAPAuthenticator.group_search_base = 'OU=Groups,DC=example,DC=org'

        c.LDAPAuthenticator.admin_users = {'Administrator'}
        c.LDAPAuthenticator.allowed_groups = [
            'CN=JupyterHub_Users,OU=Groups,DC=example,DC=org']
        ```
        """
    )

    lookup_dn_search_filter = Unicode(
        config=True,
        default_value="({login_attr}={login})",
        allow_none=True,
        help="""
        How to query LDAP for user name lookup, if `lookup_dn` is set to True.
        """,
    )

    lookup_dn_search_user = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help="""
        Technical account for user lookup, if `lookup_dn` is set to True.

        If both lookup_dn_search_user and lookup_dn_search_password are None, then anonymous LDAP query will be done.
        """,
    )

    lookup_dn_search_password = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help="""
        Technical account for user lookup, if `lookup_dn` is set to True.
        """,
    )

    lookup_dn_user_dn_attribute = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help="""
        Attribute containing user's name needed for building DN string, if `lookup_dn` is set to True.

        See `user_search_base` for info on how this attribute is used.

        For most LDAP servers, this is username.  For Active Directory, it is cn.
        """,
    )

    escape_userdn = Bool(
        False,
        config=True,
        help="""
        If set to True, escape special chars in userdn when authenticating in LDAP.

        On some LDAP servers, when userdn contains chars like '(', ')', '\' authentication may fail when those chars
        are not escaped.
        """,
    )

    search_filter = Unicode(
        config=True, help="LDAP3 Search Filter whose results are allowed access"
    )

    attributes = List(config=True, help="List of attributes to be searched")

    auth_state_attributes = List(
        config=True, help="List of attributes to be returned in auth_state for a user"
    )

    use_lookup_dn_username = Bool(
        True,
        config=True,
        help="""
        If set to true uses the `lookup_dn_user_dn_attribute` attribute as username instead of the supplied one.

        This can be useful in an heterogeneous environment, when supplying a UNIX username to authenticate against AD.
        """,
    )

    def resolve_username(self, username_supplied_by_user):
        search_dn = self.lookup_dn_search_user
        if self.escape_userdn:
            search_dn = escape_filter_chars(search_dn)
        conn = self.get_connection(
            userdn=search_dn,
            password=self.lookup_dn_search_password,
        )
        is_bound = conn.bind()
        if not is_bound:
            msg = "Failed to connect to LDAP server with search user '{search_dn}'"
            self.log.warning(msg.format(search_dn=search_dn))
            return (None, None)

        search_filter = self.lookup_dn_search_filter.format(
            login_attr=self.user_attribute, login=username_supplied_by_user
        )
        msg = "\n".join(
            [
                "Looking up user with:",
                "    search_base = '{search_base}'",
                "    search_filter = '{search_filter}'",
                "    attributes = '{attributes}'",
            ]
        )
        self.log.debug(
            msg.format(
                search_base=self.user_search_base,
                search_filter=search_filter,
                attributes=self.user_attribute,
            )
        )
        conn.search(
            search_base=self.user_search_base,
            search_scope=ldap3.SUBTREE,
            search_filter=search_filter,
            attributes=[self.lookup_dn_user_dn_attribute],
        )
        response = conn.response
        if len(response) == 0 or "attributes" not in response[0].keys():
            msg = (
                "No entry found for user '{username}' "
                "when looking up attribute '{attribute}'"
            )
            self.log.warning(
                msg.format(
                    username=username_supplied_by_user, attribute=self.user_attribute
                )
            )
            return (None, None)

        user_dn = response[0]["attributes"][self.lookup_dn_user_dn_attribute]
        if isinstance(user_dn, list):
            if len(user_dn) == 0:
                return (None, None)
            elif len(user_dn) == 1:
                user_dn = user_dn[0]
            else:
                msg = (
                    "A lookup of the username '{username}' returned a list "
                    "of entries for the attribute '{attribute}'. Only the "
                    "first among these ('{first_entry}') was used. The other "
                    "entries ({other_entries}) were ignored."
                )
                self.log.warn(
                    msg.format(
                        username=username_supplied_by_user,
                        attribute=self.lookup_dn_user_dn_attribute,
                        first_entry=user_dn[0],
                        other_entries=", ".join(user_dn[1:]),
                    )
                )
                user_dn = user_dn[0]

        return (user_dn, response[0]["dn"])

    def get_connection(self, userdn, password):
        server = ldap3.Server(
            self.server_address, port=self.server_port, use_ssl=self.use_ssl
        )
        auto_bind = (
            ldap3.AUTO_BIND_NO_TLS if self.use_ssl else ldap3.AUTO_BIND_TLS_BEFORE_BIND
        )
        conn = ldap3.Connection(
            server, user=userdn, password=password, auto_bind=auto_bind
        )
        return conn

    def get_user_attributes(self, conn, userdn):
        attrs = {}
        if self.auth_state_attributes:
            found = conn.search(
                userdn, "(objectClass=*)", attributes=self.auth_state_attributes
            )
            if found:
                attrs = conn.entries[0].entry_attributes_as_dict
        return attrs

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data["username"]
        password = data["password"]

        def get_user_groups(username):
            if self.activedirectory:
                self.log.debug('Active Directory enabled')
                user_dn = self.resolve_username(username)
                search_filter='(member:1.2.840.113556.1.4.1941:={dn})'.format(dn=escape_filter_chars(user_dn))
                search_attribs=['cn'] # We don't actually care, we just want the DN
                search_base=self.group_search_base,
                self.log.debug('LDAP Group query: user_dn:[%s] filter:[%s]', user_dn, search_filter)
            else:
                search_filter=self.lookup_dn_search_filter.format(login_attr=self.user_attribute, login=username)
                search_attribs=[self.memberof_attribute]
                search_base=self.user_search_base,
                self.log.debug('LDAP Group query: username:[%s] filter:[%s]', username, search_filter)

            conn.search(
                search_base=self.group_search_base,
                search_scope=ldap3.SUBTREE,
                search_filter=search_filter,
                attributes=search_attribs)

            if self.activedirectory:
                user_groups = []

                if len(conn.response) == 0:
                    return None

                for g in conn.response:
                    user_groups.append(g['dn'])
                return user_groups
            else:
                if len(conn.response) == 0 or 'attributes' not in conn.response[0].keys():
                    self.log.debug('User %s is not a member of any groups (via memberOf)', username)
                    return None
                else:
                    return conn.response[0]['attributes'][self.memberof_attribute]

        # Protect against invalid usernames as well as LDAP injection attacks
        if not re.match(self.valid_username_regex, username):
            self.log.warning(
                "username:%s Illegal characters in username, must match regex %s",
                username,
                self.valid_username_regex,
            )
            return None

        # Allow us to reference the actual username the user typed (rather than
        # what we might resolve it to later)
        login = username

        # No empty passwords!
        if password is None or password.strip() == "":
            self.log.warning("username:%s Login denied for blank password", username)
            return None

        # bind_dn_template should be of type List[str]
        bind_dn_template = self.bind_dn_template
        if isinstance(bind_dn_template, str):
            bind_dn_template = [bind_dn_template]

        # sanity check
        if not self.lookup_dn and not bind_dn_template:
            self.log.warning(
                "Login not allowed, please configure 'lookup_dn' or 'bind_dn_template'."
            )
            return None

        if self.lookup_dn:
            username, resolved_dn = self.resolve_username(username)
            if not username:
                return None
            if str(self.lookup_dn_user_dn_attribute).upper() == "CN":
                # Only escape commas if the lookup attribute is CN
                username = re.subn(r"([^\\]),", r"\1\,", username)[0]
            if not bind_dn_template:
                bind_dn_template = [resolved_dn]

        is_bound = False
        for dn in bind_dn_template:
            if not dn:
                self.log.warning("Ignoring blank 'bind_dn_template' entry!")
                continue
            userdn = dn.format(username=username, login=login)
            if self.escape_userdn:
                userdn = escape_filter_chars(userdn)
            msg = "Attempting to bind {username} with {userdn}"
            self.log.debug(msg.format(username=username, userdn=userdn))
            msg = "Status of user bind {username} with {userdn} : {is_bound}"
            try:
                conn = self.get_connection(userdn, password)
            except ldap3.core.exceptions.LDAPBindError as exc:
                is_bound = False
                msg += "\n{exc_type}: {exc_msg}".format(
                    exc_type=exc.__class__.__name__,
                    exc_msg=exc.args[0] if exc.args else "",
                )
            else:
                is_bound = True if conn.bound else conn.bind()
            msg = msg.format(username=username, userdn=userdn, is_bound=is_bound)
            self.log.debug(msg)
            if is_bound:
                break

        if not is_bound:
            msg = "Invalid password for user '{username}'"
            self.log.warning(msg.format(username=username))
            return None

        if self.search_filter:
            search_filter = self.search_filter.format(
                userattr=self.user_attribute, username=username
            )
            conn.search(
                search_base=self.user_search_base,
                search_scope=ldap3.SUBTREE,
                search_filter=search_filter,
                attributes=self.attributes,
            )
            n_users = len(conn.response)
            if n_users == 0:
                msg = "User with '{userattr}={username}' not found in directory"
                self.log.warning(
                    msg.format(userattr=self.user_attribute, username=username)
                )
                return None
            if n_users > 1:
                msg = (
                    "Duplicate users found! "
                    "{n_users} users found with '{userattr}={username}'"
                )
                self.log.warning(
                    msg.format(
                        userattr=self.user_attribute, username=username, n_users=n_users
                    )
                )
                return None

        if self.allowed_groups:
            self.log.debug("username:%s Using dn %s", username, userdn)
            found = False

            if self.get_groups_from_user:
                user_groups = get_user_groups(login)
                if user_groups is None:
                    self.log.debug('Username %s has no group membership', username)
                    return None
                else:
                    self.log.debug('Username %s is a member of %d groups', username, len(user_groups))
                    for group in self.allowed_groups:
                        if group in user_groups:
                            self.log.info('User %s is a member of permitted group %s', username, group)
                            return username
            else:
    for group in self.allowed_groups:
        group_filter = (
            "(|"
            "(member={userdn})"
            "(uniqueMember={userdn})"
            "(memberUid={uid})"
            ")"
        )
        group_filter = group_filter.format(userdn=userdn, uid=username)
        group_attributes = ["member", "uniqueMember", "memberUid"]
        found = conn.search(
            group,
            search_scope=ldap3.BASE,
            search_filter=group_filter,
            attributes=group_attributes,
        )
        if found:
            break
            if not found:
                # If we reach here, then none of the groups matched
                msg = "username:{username} User not in any of the allowed groups"
                self.log.warning(msg.format(username=username))
                return None

        if not self.use_lookup_dn_username:
            username = data["username"]

        user_info = self.get_user_attributes(conn, userdn)
        if user_info:
            self.log.debug("username:%s attributes:%s", username, user_info)
            return {"name": username, "auth_state": user_info}
        return username

if __name__ == "__main__":
    import getpass

    c = LDAPAuthenticator()
    c.server_address = "ldap.organisation.org"
    c.server_port = 636
    c.bind_dn_template = "uid={username},ou=people,dc=organisation,dc=org"
    c.user_attribute = "uid"
    c.user_search_base = "ou=people,dc=organisation,dc=org"
    c.attributes = ["uid", "cn", "mail", "ou", "o"]
    # The following is an example of a search_filter which is build on LDAP AND and OR operations
    # here in this example as a combination of the LDAP attributes 'ou', 'mail' and 'uid'
    sf = "(&(o={o})(ou={ou}))".format(o="yourOrganisation", ou="yourOrganisationalUnit")
    sf += "(&(o={o})(mail={mail}))".format(o="yourOrganisation", mail="yourMailAddress")
    c.search_filter = "(&({{userattr}}={{username}})(|{}))".format(sf)
    username = input("Username: ")
    passwd = getpass.getpass()
    data = dict(username=username, password=passwd)
    rs = c.authenticate(None, data)
    print(rs.result())
