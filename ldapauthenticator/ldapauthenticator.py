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

    lookup_dn = Bool(
        False,
        config=True,
        help='Look up the user\'s DN based on an attribute'
    )

    user_search_base = Unicode(
        config=True,
        help="""Base for looking up user accounts in the directory.

        Example:

            ou=people,dc=wikimedia,dc=org
        """
    )

    user_attribute = Unicode(
        config=True,
        help="""LDAP attribute that stores the user's username.

        For most LDAP servers, this is uid.  For Active Directory, it is
        sAMAccountName.
        """
    )

    search_filter = Unicode(
        config=True,
        help="LDAP3 Search Filter whose results are allowed access"
    )

    attributes = List(
        config=True,
        help="List of attributes to be searched"
    )

    local_user = List(
        config=True,
        help="List of additional infos (dict of attributes and useradd command) to create local user accounts"
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
        conn = ldap3.Connection(server, user=userdn, password=password)

        if conn.bind():
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
                        self.log.warn('User with {userattr}={username} not found in directory'.format(
                            userattr=self.user_attribute, username=username))
                        return None
                    userdn = conn.response[0]['dn']

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
                self.log.warn('User {username} not in any of the allowed groups'.format(
                    username=userdn
                ))
                return None
            elif self.search_filter:
                conn.search(
                    search_base=self.user_search_base,
                    search_scope=ldap3.SUBTREE,
                    search_filter=self.search_filter.format(userattr=self.user_attribute,username=username),
                    attributes=self.attributes
                )
                if len(conn.response) == 0:
                    self.log.warn('User with {userattr}={username} not found in directory'.format(
                        userattr=self.user_attribute, username=username))
                    return None
                elif len(conn.response) > 1:
                    self.log.warn('User with {userattr}={username} found more than {len}-fold in directory'.format(
                        userattr=self.user_attribute, username=username, len=len(conn.response)))
                    return None
                if self.local_user:
                    import pwd, os
                    try:
                        user = pwd.getpwnam(username)
                    except KeyError: 
                        this = conn.response[0]
                        thisEntry = dict()
                        for attr in self.attributes:
                            thisEntry.update({attr:this["attributes"][attr][0]})
                        for info in self.local_user:
                            ok = True
                            for attr in list(set(self.attributes)&set(info.keys())):
                                if info[attr].replace('*','(',1).replace('*',')',1) == thisEntry[attr]:
                                    ok &= True
                                else:
                                    ok = False
                            if ok:
                                useradd = info['useradd']
                        os.system(useradd.format(**thisEntry))
                        self.log.info('User {userattr}={username} added as local user ({useradd})'.format(
                            userattr=self.user_attribute, username=username, useradd=useradd))
                return username
            else:
                return username
        else:
            self.log.warn('Invalid password for user {username}'.format(
                username=userdn,
            ))
            return None


if __name__ == "__main__":
    import getpass
    c = LDAPAuthenticator()
    c.server_address = "ldap.organisation.org"
    c.server_port = 636
    c.bind_dn_template = "uid={username},ou=people,dc=organisation,dc=org"
    c.user_attribute = 'uid'
    c.user_search_base = 'ou=people,dc=organisation,dc=org'
    c.attributes = ['uid','cn','mail','ou','o']
    # attributes_list is a list of dictionaries of attributes which should be satisfied by a user to be logged in
    # the additional key 'useradd' is only necessary, if local user accounts should be created
    # - the value of this key is the system command to be called to create the local user
    attributes_list = [dict(ou="section1",o="department1",
                useradd="useradd -m -d /home/ldapuser/department1/{uid} -s /bin/false {uid} -c \"{cn} - {mail}\"\n"),
                      dict(ou="section2",o="department1",
                useradd="useradd -m -d /home/ldapuser/department1/{uid} -s /bin/false {uid} -c \"{cn} - {mail}\"\n"),
                      dict(mail="*@marketing.organisation.org",o="department2",
                useradd="useradd -m -d /home/ldapuser/marketing/{uid} -s /bin/false {uid} -c \"{cn} - {mail}\"\n"),
                      dict(ou="finance",o="management",
                useradd="useradd -m -d /home/ldapuser/finance/{uid} -s /bin/false {uid} -c \"{cn} - {mail}\"\n")]
    # the following loop builds the ldap search filter based on the above attributes_list
    sf = ""
    for attr in attributes_list:
        if 'ou' in attr:
            sf += "(&(o={o})(ou={ou}))".format(**attr)
        elif 'mail' in attr:
            sf += "(&(o={o})(mail={mail}))".format(**attr)
    c.search_filter = "(&({{userattr}}={{username}})(|{}))".format(sf)
    # The next line is only necessary, if local user accounts should be created
    c.local_user = attributes_list 
    username = input('Username: ')
    passwd = getpass.getpass()
    data = dict(username=username,password=passwd)
    rs=c.authenticate(None,data)
    print(rs.result())
