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
        ```
        """,
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
            userdn=search_dn, password=self.lookup_dn_search_password
        )
        is_bound = conn.bind()
        if not is_bound:
            msg = "Failed to connect to LDAP server with search user '{search_dn}'"
            self.log.warning(msg.format(search_dn=search_dn))
            return None, None

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
            return None, None

        ret = (
            conn.response[0]["attributes"][self.lookup_dn_user_dn_attribute],
            conn.response[0]["dn"],
        )
        return ret

    def get_connection(self, userdn, password):
        server = ldap3.Server(
            self.server_address, port=self.server_port, use_ssl=self.use_ssl
        )
        auto_bind = (
            self.use_ssl and ldap3.AUTO_BIND_TLS_BEFORE_BIND or ldap3.AUTO_BIND_NO_TLS
        )
        conn = ldap3.Connection(
            server, user=userdn, password=password, auto_bind=auto_bind
        )
        return conn

    @gen.coroutine
    def authenticate(self, handler, data):
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

        if self.lookup_dn:
            username, resolved_dn = self.resolve_username(username)
            if not username:
                return None
            if isinstance(username, list):
                username = username[0]

        if self.lookup_dn:
            if str(self.lookup_dn_user_dn_attribute).upper() == "CN":
                # Only escape commas if the lookup attribute is CN
                username = re.subn(r"([^\\]),", r"\1\,", username)[0]

        bind_dn_template = self.bind_dn_template
        if not bind_dn_template and self.lookup_dn:
            bind_dn_template = [resolved_dn]
        if isinstance(bind_dn_template, str):
            # bind_dn_template should be of type List[str]
            bind_dn_template = [bind_dn_template]

        is_bound = False
        for dn in bind_dn_template:
            if not dn:
                self.log.warning("Ignoring blank 'bind_dn_template' entry!")
                continue
            userdn = dn.format(username=username)
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
                is_bound = conn.bind()
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

        if self.use_lookup_dn_username:
            return username
        else:
            return data["username"]


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
