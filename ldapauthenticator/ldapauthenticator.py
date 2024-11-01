import enum
import re
from inspect import isawaitable

import ldap3
from jupyterhub.auth import Authenticator
from ldap3.core.exceptions import LDAPBindError
from ldap3.core.tls import Tls
from ldap3.utils.conv import escape_filter_chars
from ldap3.utils.dn import escape_rdn
from traitlets import Bool, Dict, Int, List, Unicode, Union, UseEnum, observe, validate


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
                'instead of configuring use_ssl=True, configure tls_strategy="on_connect" from now on.'
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

    tls_kwargs = Dict(
        config=True,
        help="""
        A dictionary that will be used as keyword arguments for the constructor
        of the ldap3 package's TLS object, influencing encrypted connections to
        the LDAP server.

        For details on what can be configured and its effects, refer to the
        ldap3 package's documentation and code:

        - ldap3 documentation: https://ldap3.readthedocs.io/en/latest/ssltls.html#the-tls-object
        - ldap3 code: https://github.com/cannatag/ldap3/blob/v2.9.1/ldap3/core/tls.py#L59-L82

        You can for example configure this like:

        ```python
        c.LDAPAuthenticator.tls_kwargs = {
            "ca_certs_file": "file/path.here",
        }
        ```
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

        String example:
            uid={username},ou=people,dc=wikimedia,dc=org

        List example:
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
        else:
            rv = proposal.value
        if "" in rv:
            self.log.warning("Ignoring blank 'bind_dn_template' entry!")
            rv = [e for e in rv if e]
        return rv

    @observe("lookup_dn", "bind_dn_template")
    def _require_either_lookup_dn_or_bind_dn_template(self, change):
        if not self.lookup_dn and not self.bind_dn_template:
            raise ValueError(
                "LDAPAuthenticator requires either lookup_dn or "
                "bind_dn_template to be configured"
            )

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

        When combined with `search_filter`, this strictly reduces the allowed users,
        i.e. `search_filter` AND `allowed_groups` must both be satisfied.
        """,
    )

    group_search_filter = Unicode(
        config=True,
        default_value="(|(member={userdn})(uniqueMember={userdn})(memberUid={uid}))",
        help="""
        The search filter template used to locate groups that the user belongs to.

        `{userdn}` and `{uid}` will be replaced with the LDAP user's attributes.

        Certain server types may use different values, and may also
        reject invalid values by raising exceptions.
        """,
    )

    group_attributes = List(
        config=True,
        default_value=["member", "uniqueMember", "memberUid"],
        help="List of attributes in the LDAP group to be searched",
    )

    @observe("allowed_groups", "group_search_filter", "group_attributes")
    def _ensure_allowed_groups_requirements(self, change):
        if not self.allowed_groups:
            return
        if not self.group_search_filter or not self.group_attributes:
            raise ValueError(
                "LDAPAuthenticator.allowed_groups requires both "
                "group_search_filter and group_attributes to be configured"
            )

    valid_username_regex = Unicode(
        r"^[a-z][.a-z0-9_-]*$",
        config=True,
        help="""
        Regex for validating usernames - those that do not match this regex will
        be rejected.

        This config was primarily introduced to prevent LDAP injection
        (https://www.owasp.org/index.php/LDAP_injection), but that is since 2.0
        being mitigated by escaping all sensitive characters when interacting
        with the LDAP server.
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
        Only used with `lookup_dn=True` or with a configured `search_filter`.

        Defines the search base for looking up users in the directory.

        ```python
        c.LDAPAuthenticator.user_search_base = 'ou=People,dc=example,dc=com'
        ```

        LDAPAuthenticator will search all objects under this base where
        the `user_attribute` is set to the current username to form the userdn.

        For example, if all users objects existed under the base
        `ou=people,dc=wikimedia,dc=org`, the username is set with
        the attribute `uid`, you can use the following config:

        ```python
        c.LDAPAuthenticator.lookup_dn = True
        c.LDAPAuthenticator.lookup_dn_search_filter = '({login_attr}={login})'
        c.LDAPAuthenticator.lookup_dn_search_user = 'ldap_search_user_technical_account'
        c.LDAPAuthenticator.lookup_dn_search_password = 'secret'
        c.LDAPAuthenticator.user_search_base = 'ou=people,dc=wikimedia,dc=org'
        c.LDAPAuthenticator.user_attribute = 'uid'
        c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'sAMAccountName'
        ```
        """,
    )

    user_attribute = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help="""
        Only used with `lookup_dn=True` or with a configured `search_filter`.

        Together with `user_search_base`, this attribute will be searched to
        contain the username provided by the user in JupyterHub's login form.

        ```python
        # Active Directory
        c.LDAPAuthenticator.user_attribute = 'sAMAccountName'

        # OpenLDAP
        c.LDAPAuthenticator.user_attribute = 'uid'
        ```
        """,
    )

    lookup_dn_search_filter = Unicode(
        config=True,
        default_value="({login_attr}={login})",
        allow_none=True,
        help="""
        Only used with `lookup_dn=True`.

        How to query LDAP for user name lookup.

        Default value `'({login_attr}={login})'` should be good enough for most
        use cases.
        """,
    )

    lookup_dn_search_user = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help="""
        Only used with `lookup_dn=True`.

        Technical account for user lookup. If both `lookup_dn_search_user` and
        `lookup_dn_search_password` are None, then anonymous LDAP query will be
        done.
        """,
    )

    lookup_dn_search_password = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help="""
        Only used with `lookup_dn=True`.

        Password for a `lookup_dn_search_user`.
        """,
    )

    lookup_dn_user_dn_attribute = Unicode(
        config=True,
        default_value=None,
        allow_none=True,
        help="""
        Only used with `lookup_dn=True`.

        Attribute containing user's name needed for building DN string. See
        `user_search_base` for info on how this attribute is used. For most LDAP
        servers, this is username. For Active Directory, it is `sAMAccountName`.
        """,
    )

    escape_userdn = Bool(
        False,
        config=True,
        help="""
        Removed in 2.0, configuring this no longer has any effect.
        """,
    )

    @observe("escape_userdn")
    def _observe_escape_userdn(self, change):
        self.log.warning(
            "LDAPAuthenticator.escape_userdn was removed in 2.0 and no longer has any effect."
        )

    search_filter = Unicode(
        config=True,
        help="""
        LDAP3 Search Filter to limit allowed users.

        That a unique LDAP user is identified with the search_filter is
        necessary but not sufficient to grant access. Grant access by setting
        one or more of `allowed_users`, `allow_all`, `allowed_groups`, etc.

        Users who do not match this filter cannot be allowed
        by any other configuration.

        The search filter string will be expanded, so that:

        - `{userattr}` is replaced with the `user_attribute` config's value.
        - `{username}` is replaced with an escaped username, either provided
          directly or previously looked up with `lookup_dn` configured.
        """,
    )

    attributes = List(
        config=True,
        help="""
        List of attributes to be passed in the LDAP search with `search_filter`.
        """,
    )

    auth_state_attributes = List(
        config=True,
        help="""
        List of user attributes to be returned in auth_state

        Will be available in `auth_state["user_attributes"]`
        """,
    )

    use_lookup_dn_username = Bool(
        False,
        config=True,
        help="""
        Only used with `lookup_dn=True`.

        If configured True, the `lookup_dn_user_dn_attribute` value used to
        build the LDAP user's DN string is also used as the authenticated user's
        JupyterHub username.

        If this is configured True, its important to ensure that the values of
        `lookup_dn_user_dn_attribute` are unique even after the are normalized
        to be lowercase, otherwise two LDAP users could end up sharing the same
        JupyterHub username.

        With ldapauthenticator 2, the default value was changed to False.
        """,
    )

    def resolve_username(self, username_supplied_by_user):
        """
        Resolves a username (that could be used to construct a DN through a
        template), and a DN, based on a username supplied by a user via a login
        prompt in JupyterHub.

        Returns (username, userdn) if found, or (None, None) if an error occurred,
        or if `username_supplied_by_user` does not correspond to a unique user.
        """
        conn = self.get_connection(
            userdn=self.lookup_dn_search_user,
            password=self.lookup_dn_search_password,
        )
        if not conn:
            self.log.error(
                f"Failed to bind lookup_dn_search_user '{self.lookup_dn_search_user}'"
            )
            return (None, None)

        search_filter = self.lookup_dn_search_filter.format(
            # A search filter matching against string literals, should
            # have the string literals escaped with escape_filter_chars.
            # Escaped characters are `/()*` (and null).
            #
            # ref: https://datatracker.ietf.org/doc/html/rfc4515#section-3
            # ref: https://ldap3.readthedocs.io/en/latest/searches.html?highlight=escape_filter_chars
            #
            login_attr=self.user_attribute,
            login=escape_filter_chars(username_supplied_by_user),
        )
        self.log.debug(
            "Looking up user with:\n"
            f"    search_base = '{self.user_search_base}'\n"
            f"    search_filter = '{search_filter}'\n"
            f"    attributes = '[{self.lookup_dn_user_dn_attribute}]'"
        )
        conn.search(
            search_base=self.user_search_base,
            search_scope=ldap3.SUBTREE,
            search_filter=search_filter,
            attributes=[self.lookup_dn_user_dn_attribute],
        )

        # identify unique search response entry
        n_entries = len(conn.entries)
        if n_entries == 0:
            self.log.warning(
                f"Failed to lookup a DN for username '{username_supplied_by_user}'"
            )
            return (None, None)
        if n_entries > 1:
            self.log.error(
                f"Failed to lookup a unique DN for username '{username_supplied_by_user}'"
            )
            return (None, None)
        entry = conn.entries[0]

        # identify unique attribute value within the entry
        attribute_values = entry.entry_attributes_as_dict.get(
            self.lookup_dn_user_dn_attribute
        )
        if not attribute_values:
            self.log.warning(
                f"Failed to lookup attribute '{self.lookup_dn_user_dn_attribute}' "
                f"for username '{username_supplied_by_user}'"
            )
            return (None, None)
        if len(attribute_values) > 1:
            self.log.error(
                f"A lookup of the username '{username_supplied_by_user}' returned multiple "
                f"values for the attribute '{self.lookup_dn_user_dn_attribute}': "
                f"({', '.join(attribute_values)})"
            )
            return None, None

        userdn = entry.entry_dn
        username = attribute_values[0]
        return (username, userdn)

    def get_connection(self, userdn, password):
        """
        Returns either an ldap3 Connection object automatically bound to the
        user, or None if the bind operation failed for some reason.

        Raises errors on connectivity or TLS issues.

        ldap3 Connection ref:
        - docs: https://ldap3.readthedocs.io/en/latest/connection.html
        - code: https://github.com/cannatag/ldap3/blob/dev/ldap3/core/connection.py
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

        tls = Tls(**self.tls_kwargs)
        server = ldap3.Server(
            self.server_address,
            port=self.server_port,
            use_ssl=use_ssl,
            tls=tls,
        )
        try:
            self.log.debug(f"Attempting to bind {userdn}")
            conn = ldap3.Connection(
                server,
                user=userdn,
                password=password,
                auto_bind=auto_bind,
            )
        except LDAPBindError as e:
            self.log.debug(
                "Failed to bind {userdn}\n{e_type}: {e_msg}".format(
                    userdn=userdn,
                    e_type=e.__class__.__name__,
                    e_msg=e.args[0] if e.args else "",
                )
            )
            return None
        else:
            self.log.debug(f"Successfully bound {userdn}")
            return conn

    def get_user_attributes(self, conn, userdn):
        attrs = {}
        if self.auth_state_attributes:
            found = conn.search(
                search_base=userdn,
                search_scope=ldap3.SUBTREE,
                search_filter="(objectClass=*)",
                attributes=self.auth_state_attributes,
            )
            # FIXME: Handle situations with multiple entries below or comment
            #        why its not important to do.
            #
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
        login_username = data["username"]
        password = data["password"]

        # Protect against invalid usernames as well as LDAP injection attacks
        if not re.match(self.valid_username_regex, login_username):
            self.log.warning(
                "username:%s Illegal characters in username, must match regex %s",
                login_username,
                self.valid_username_regex,
            )
            return None

        # No empty passwords!
        if password is None or password.strip() == "":
            self.log.warning(
                "username:%s Login denied for blank password", login_username
            )
            return None

        bind_dn_template = self.bind_dn_template
        resolved_username = login_username
        if self.lookup_dn:
            resolved_username, resolved_dn = self.resolve_username(login_username)
            if not resolved_dn:
                return None
            if not bind_dn_template:
                bind_dn_template = [resolved_dn]

        # bind to ldap user
        conn = None
        for dn in bind_dn_template:
            # A DN represented as a string should have its attribute values
            # escaped with escape_rdn. Escaped characters are `\,+"<>;=` (and
            # null).
            #
            # ref: https://datatracker.ietf.org/doc/html/rfc4514#section-2.4.
            # ref: https://ldap3.readthedocs.io/en/latest/connection.html?highlight=escape_rdn
            #
            userdn = dn.format(username=escape_rdn(resolved_username))
            conn = self.get_connection(userdn, password)
            if conn:
                break
        if not conn:
            if login_username == resolved_username:
                self.log.warning(
                    f"Failed to bind user '{login_username}' to an LDAP user."
                )
            else:
                self.log.warning(
                    f"Failed to bind login username '{login_username}', "
                    f"with looked up user attribute value '{resolved_username}', "
                    "to an LDAP user."
                )
            return None

        if self.search_filter:
            conn.search(
                search_base=self.user_search_base,
                search_scope=ldap3.SUBTREE,
                search_filter=self.search_filter.format(
                    # A search filter matching against string literals, should
                    # have the string literals escaped with escape_filter_chars.
                    # Escaped characters are `/()*` (and null).
                    #
                    # ref: https://datatracker.ietf.org/doc/html/rfc4515#section-3
                    # ref: https://ldap3.readthedocs.io/en/latest/searches.html?highlight=escape_filter_chars
                    #
                    userattr=self.user_attribute,
                    username=escape_filter_chars(resolved_username),
                ),
                attributes=self.attributes,
            )
            n_entries = len(conn.entries)
            if n_entries == 0:
                self.log.warning(
                    "Configured search_filter found no user associated with "
                    f"userattr='{self.user_attribute}' and username='{resolved_username}'"
                )
                return None
            if n_entries > 1:
                self.log.warning(
                    "Configured search_filter found multiple users associated with "
                    f"userattr='{self.user_attribute}' and username='{resolved_username}', "
                    "a unique match is required."
                )
                return None

        ldap_groups = []
        if self.allowed_groups:
            self.log.debug("username:%s Using dn %s", resolved_username, userdn)
            for group in self.allowed_groups:
                found = conn.search(
                    search_base=group,
                    search_scope=ldap3.BASE,
                    search_filter=self.group_search_filter.format(
                        # A search filter matching against string literals, should
                        # have the string literals escaped with escape_filter_chars.
                        # Escaped characters are `/()*` (and null).
                        #
                        # ref: https://datatracker.ietf.org/doc/html/rfc4515#section-3
                        # ref: https://ldap3.readthedocs.io/en/latest/searches.html?highlight=escape_filter_chars
                        #
                        userdn=escape_filter_chars(userdn),
                        uid=escape_filter_chars(resolved_username),
                    ),
                    attributes=self.group_attributes,
                )
                if found:
                    ldap_groups.append(group)
                    # Returned in auth_state, so fetch the full list

        user_attributes = self.get_user_attributes(conn, userdn)
        self.log.debug("username:%s attributes:%s", login_username, user_attributes)

        username = resolved_username if self.use_lookup_dn_username else login_username
        auth_state = {
            "ldap_groups": ldap_groups,
            "user_attributes": user_attributes,
        }
        return {"name": username, "auth_state": auth_state}

    async def check_allowed(self, username, auth_model):
        if not hasattr(self, "allow_all"):
            # super for JupyterHub < 5
            # default behavior: no allow config => allow all
            if not self.allowed_users and not self.allowed_groups:
                return True
            if self.allowed_users and username in self.allowed_users:
                return True
        else:
            allowed = super().check_allowed(username, auth_model)
            if isawaitable(allowed):
                allowed = await allowed
            if allowed is True:
                return True
        if self.allowed_groups:
            # check allowed groups
            in_groups = set((auth_model.get("auth_state") or {}).get("ldap_groups", []))
            for group in self.allowed_groups:
                if group in in_groups:
                    self.log.debug("Allowing %s as member of group %s", username, group)
                    return True
        if self.search_filter:
            self.log.info(
                "User %s matches search_filter %s, but not allowed by allowed_users, allowed_groups, or allow_all.",
                username,
                self.search_filter,
            )
        return False
