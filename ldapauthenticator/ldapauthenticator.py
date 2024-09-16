import enum
import re

import ldap3
from jupyterhub.auth import Authenticator
from ldap3.utils.conv import escape_filter_chars
from traitlets import Bool, Int, List, Unicode, Union, UseEnum, observe, validate


class TlsStrategy(enum.Enum):
    """
    Represents a SSL/TLS strategy for LDAPAuthenticator to use when interacting
    with the LDAP server.
    """

    before_bind = 1
    on_connect = 2
    insecure = 3


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

        Defaults to `636` if `tls_strategy="on_connect"` is set, `389`
        otherwise.
        """,
    )

    def _server_port_default(self):
        if self.tls_strategy == TlsStrategy.on_connect:
            return 636  # default SSL port for LDAP
        else:
            return 389  # default plaintext port for LDAP

    use_ssl = Bool(
        None,
        allow_none=True,
        config=True,
        help="""
        `use_ssl` is deprecated since 2.0. `use_ssl=True` translates to configuring
        `tls_strategy="on_connect"`, but `use_ssl=False` (previous default) doesn't
        translate to anything.
        """,
    )

    @observe("use_ssl")
    def _observe_use_ssl(self, change):
        if change.new:
            self.tls_strategy = TlsStrategy.on_connect
            self.log.warning(
                "LDAPAuthenticator.use_ssl is deprecated in 2.0 in favor of LDAPAuthenticator.tls_strategy, "
                'instead of configuring use_ssl=True, configure use tls_strategy="on_connect" from now on.'
            )
        else:
            self.log.warning(
                "LDAPAuthenticator.use_ssl is deprecated in 2.0 in favor of LDAPAuthenticator.tls_strategy, "
                "you can stop configuring use_ssl=False from now on as doing so has no effect."
            )

    tls_strategy = UseEnum(
        TlsStrategy,
        default_value=TlsStrategy.before_bind,
        config=True,
        help="""
        When LDAPAuthenticator connects to the LDAP server, it can establish a
        SSL/TLS connection directly, or do it before binding, which is LDAP
        terminology for authenticating and sending sensitive credentials.

        The LDAP v3 protocol deprecated establishing a SSL/TLS connection
        directly (`tls_strategy="on_connect"`) in favor of upgrading the
        connection to SSL/TLS before binding (`tls_strategy="before_bind"`).

        Supported `tls_strategy` values are:
        - "before_bind" (default)
        - "on_connect" (deprecated in LDAP v3, associated with use of port 636)
        - "insecure"

        When configuring `tls_strategy="on_connect"`, the default value of
        `server_port` becomes 636.
        """,
    )

    bind_dn_template = Union(
        [List(), Unicode()],
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
        """,
    )

    @validate("bind_dn_template")
    def _validate_bind_dn_template(self, proposal):
        """
        Ensure a List[str] is set, filtered from empty string elements.
        """
        rv = []
        if isinstance(proposal.value, str):
            rv = [proposal.value]
        if "" in rv:
            self.log.warning("Ignoring blank 'bind_dn_template' entry!")
            rv = [e for e in rv if e]
        return rv

    allowed_groups = List(
        config=True,
        allow_none=True,
        default_value=None,
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

    group_search_filter = Unicode(
        config=True,
        default_value="(|(member={userdn})(uniqueMember={userdn})(memberUid={uid}))",
        help="""
        The search filter used to locate groups.

        Certain server types may use different values, and may also
        reject invalid values by raising exceptions.
        """,
    )

    group_attributes = List(
        config=True,
        default_value=["member", "uniqueMember", "memberUid"],
        help="List of attributes to be searched",
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
        default_value=None,
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
        c.LDAPAuthenticator.user_attribute = 'uid'
        c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'cn'
        c.LDAPAuthenticator.bind_dn_template = '{username}'
        ```
        """,
    )

    user_attribute = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help="""
        Attribute containing user's name, if `lookup_dn` is set to True.

        See `user_search_base` for info on how this attribute is used.

        For most LDAP servers, this is uid.  For Active Directory, it is
        sAMAccountName.
        """,
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
        Attribute containing user's name needed for  building DN string, if `lookup_dn` is set to True.

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
        """
        Resolves a username supplied by a user to the a user DN when lookup_dn
        is True.
        """
        search_dn = self.lookup_dn_search_user
        if self.escape_userdn:
            search_dn = escape_filter_chars(search_dn)
        conn = self.get_connection(
            userdn=search_dn,
            password=self.lookup_dn_search_password,
        )
        if not conn.bind():
            self.log.warning(
                f"Failed to connect to LDAP server with search user '{search_dn}'"
            )
            return (None, None)

        search_filter = self.lookup_dn_search_filter.format(
            login_attr=self.user_attribute,
            login=escape_filter_chars(username_supplied_by_user),
        )
        self.log.debug(
            "Looking up user with:\n",
            f"    search_base = '{self.user_search_base}'\n",
            f"    search_filter = '{search_filter}'\n",
            f"    attributes = '[{self.lookup_dn_user_dn_attribute}]'",
        )
        conn.search(
            search_base=self.user_search_base,
            search_scope=ldap3.SUBTREE,
            search_filter=search_filter,
            attributes=[self.lookup_dn_user_dn_attribute],
        )
        response = conn.response
        if len(response) == 0 or "attributes" not in response[0].keys():
            self.log.warning(
                f"No entry found for user '{username_supplied_by_user}' "
                f"when looking up attribute '{self.user_attribute}'"
            )
            return (None, None)

        user_dn = response[0]["attributes"][self.lookup_dn_user_dn_attribute]
        if isinstance(user_dn, list):
            if len(user_dn) == 0:
                return (None, None)
            elif len(user_dn) == 1:
                user_dn = user_dn[0]
            else:
                self.log.warn(
                    f"A lookup of the username '{username_supplied_by_user}' returned a list "
                    f"of entries for the attribute '{self.lookup_dn_user_dn_attribute}'. Only "
                    f"the first among these ('{user_dn[0]}') was used. The other entries "
                    f"({', '.join(user_dn[1:])}) were ignored."
                )
                user_dn = user_dn[0]

        return (user_dn, response[0]["dn"])

    def get_connection(self, userdn, password):
        """
        Returns a ldap3 Connection object automatically bound to the user.

        ldap3 Connection ref: https://ldap3.readthedocs.io/en/latest/connection.html
        """
        if self.tls_strategy == TlsStrategy.on_connect:
            use_ssl = True
            auto_bind = ldap3.AUTO_BIND_NO_TLS
        elif self.tls_strategy == TlsStrategy.before_bind:
            use_ssl = False
            auto_bind = ldap3.AUTO_BIND_TLS_BEFORE_BIND
        else:  # TlsStrategy.insecure
            use_ssl = False
            auto_bind = ldap3.AUTO_BIND_NO_TLS

        server = ldap3.Server(
            self.server_address,
            port=self.server_port,
            use_ssl=use_ssl,
        )
        conn = ldap3.Connection(
            server,
            user=userdn,
            password=password,
            auto_bind=auto_bind,
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

    async def authenticate(self, handler, data):
        """
        Note: This function is really meant to identify a user, and
              check_allowed and check_blocked are meant to determine if its an
              authorized user. Authorization is currently handled by returning
              None here instead.

        ref: https://jupyterhub.readthedocs.io/en/latest/reference/authenticators.html#authenticator-authenticate
        """
        username = data["username"]
        password = data["password"]

        # Protect against invalid usernames as well as LDAP injection attacks
        if not re.match(self.valid_username_regex, username):
            self.log.warning(
                "username:%s Illegal characters in username, must match regex %s",
                username,
                self.valid_username_regex,
            )
            return None

        # No empty passwords!
        if password is None or password.strip() == "":
            self.log.warning("username:%s Login denied for blank password", username)
            return None

        # sanity check
        if not self.lookup_dn and not self.bind_dn_template:
            self.log.warning(
                "Login not allowed, please configure 'lookup_dn' or 'bind_dn_template'."
            )
            return None

        bind_dn_template = self.bind_dn_template
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
            userdn = dn.format(username=username)
            self.log.debug(f"Attempting to bind {username} with {userdn}")
            msg = "Status of user bind {username} with {userdn} : {is_bound}"
            try:
                if self.escape_userdn:
                    conn = self.get_connection(escape_filter_chars(userdn), password)
                else:
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
            self.log.warning(f"Invalid password for user '{username}'")
            return None

        if self.search_filter:
            conn.search(
                search_base=self.user_search_base,
                search_scope=ldap3.SUBTREE,
                search_filter=self.search_filter.format(
                    userattr=self.user_attribute,
                    username=escape_filter_chars(username),
                ),
                attributes=self.attributes,
            )
            n_users = len(conn.response)
            if n_users == 0:
                self.log.warning(
                    f"User with '{self.user_attribute}={username}' not found in directory"
                )
                return None
            if n_users > 1:
                self.log.warning(
                    "Duplicate users found! {n_users} users found "
                    f"with '{self.user_attribute}={username}'"
                )
                return None

        if self.allowed_groups:
            if not self.group_search_filter or not self.group_attributes:
                self.log.warning(
                    "Missing group_search_filter or group_attributes. Both are required."
                )
                return None
            self.log.debug("username:%s Using dn %s", username, userdn)
            found = False
            for group in self.allowed_groups:
                found = conn.search(
                    group,
                    search_scope=ldap3.BASE,
                    search_filter=self.group_search_filter.format(
                        userdn=escape_filter_chars(userdn),
                        uid=escape_filter_chars(username),
                    ),
                    attributes=self.group_attributes,
                )
                if found:
                    break
            if not found:
                # If we reach here, then none of the groups matched
                self.log.warning(
                    f"username:{username} User not in any of the allowed groups"
                )
                return None

        if not self.use_lookup_dn_username:
            username = data["username"]

        user_info = self.get_user_attributes(conn, userdn)
        if user_info:
            self.log.debug("username:%s attributes:%s", username, user_info)
            return {"name": username, "auth_state": user_info}
        return username
