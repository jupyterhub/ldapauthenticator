# Changelog



## [1.3]


### [1.3.0] - NOT YET RELEASED

#### Fixes
* Avoid binding the connection twice [#142](https://github.com/jupyterhub/ldapauthenticator/pull/142) ([@m2hofi94](https://github.com/m2hofi94))
* Gracefully handle username lookups with list return values [#117](https://github.com/jupyterhub/ldapauthenticator/pull/117) ([@metrofun](https://github.com/metrofun))
* Misc cleanup + fixes [#95](https://github.com/jupyterhub/ldapauthenticator/pull/95) ([@dhirschfeld](https://github.com/dhirschfeld)) - *Empty DN templates are now ignored*, `search_filter` and `allowed_groups` are no longer mutually exclusive*.

#### Improvements
* Allow authentication with empty bind_dn_template when using lookup_dn [#106](https://github.com/jupyterhub/ldapauthenticator/pull/106) ([@behrmann](https://github.com/behrmann))
* Ignore username returned by resolve_username [#105](https://github.com/jupyterhub/ldapauthenticator/pull/105) ([@behrmann](https://github.com/behrmann)) - *`use_lookup_dn_username` configuration option added*
* Lookup additional LDAP user info [#103](https://github.com/jupyterhub/ldapauthenticator/pull/103) ([@manics](https://github.com/manics)) - *user_info_attributes is now saved in auth_state for a valid user*.

#### Maintenance
* Fix CI linting failures and add testing of Py38 [#157](https://github.com/jupyterhub/ldapauthenticator/pull/157) ([@consideRatio](https://github.com/consideRatio))
* Add long description for pypi [#155](https://github.com/jupyterhub/ldapauthenticator/pull/155) ([@manics](https://github.com/manics))
* Add badges according to team-compass [#154](https://github.com/jupyterhub/ldapauthenticator/pull/154) ([@consideRatio](https://github.com/consideRatio))
* Travis deploy tags to PyPI [#153](https://github.com/jupyterhub/ldapauthenticator/pull/153) ([@manics](https://github.com/manics))
* Add bind_dn_template to Active Directory instructions [#147](https://github.com/jupyterhub/ldapauthenticator/pull/147) ([@irasnyd](https://github.com/irasnyd))
* Expand contributor's guide [#135](https://github.com/jupyterhub/ldapauthenticator/pull/135) ([@marcusianlevine](https://github.com/marcusianlevine))
* Add Travis CI setup and simple tests [#134](https://github.com/jupyterhub/ldapauthenticator/pull/134) ([@marcusianlevine](https://github.com/marcusianlevine))
* Update project url in setup.py [#92](https://github.com/jupyterhub/ldapauthenticator/pull/92) ([@dhirschfeld](https://github.com/dhirschfeld))
* Update README.md [#85](https://github.com/jupyterhub/ldapauthenticator/pull/85) ([@dhirschfeld](https://github.com/dhirschfeld))
* Bump version to 1.2.2 [#84](https://github.com/jupyterhub/ldapauthenticator/pull/84) ([@dhirschfeld](https://github.com/dhirschfeld))

## Contributors to this release
([GitHub contributors page for this release](https://github.com/jupyterhub/ldapauthenticator/graphs/contributors?from=2018-06-14&to=2020-01-31&type=c))

[@behrmann](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Abehrmann+updated%3A2018-06-14..2020-01-31&type=Issues) | [@betatim](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Abetatim+updated%3A2018-06-14..2020-01-31&type=Issues) | [@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3AconsideRatio+updated%3A2018-06-14..2020-01-31&type=Issues) | [@dhirschfeld](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adhirschfeld+updated%3A2018-06-14..2020-01-31&type=Issues) | [@irasnyd](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Airasnyd+updated%3A2018-06-14..2020-01-31&type=Issues) | [@m2hofi94](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Am2hofi94+updated%3A2018-06-14..2020-01-31&type=Issues) | [@manics](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amanics+updated%3A2018-06-14..2020-01-31&type=Issues) | [@marcusianlevine](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amarcusianlevine+updated%3A2018-06-14..2020-01-31&type=Issues) | [@meeseeksmachine](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ameeseeksmachine+updated%3A2018-06-14..2020-01-31&type=Issues) | [@metrofun](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ametrofun+updated%3A2018-06-14..2020-01-31&type=Issues) | [@ramkrishnan8994](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aramkrishnan8994+updated%3A2018-06-14..2020-01-31&type=Issues) | [@titansmc](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Atitansmc+updated%3A2018-06-14..2020-01-31&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ayuvipanda+updated%3A2018-06-14..2020-01-31&type=Issues)



## [1.2]

### [1.2.2] - 2018-06-14

Minor patch release for incorrectly escaping commas in `resolved_username`

#### Fixes
* Fix comma escape in `resolved_username` [#83](https://github.com/jupyterhub/ldapauthenticator/pull/83) ([@dhirschfeld](https://github.com/dhirschfeld))

#### Improvements
* Add manifest to package license [#74](https://github.com/jupyterhub/ldapauthenticator/pull/74) ([@mariusvniekerk](https://github.com/mariusvniekerk)) - *Adds license file to the sdist*

## Contributors to this release
([GitHub contributors page for this release](https://github.com/jupyterhub/ldapauthenticator/graphs/contributors?from=2018-06-08&to=2018-06-14&type=c))

[@dhirschfeld](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adhirschfeld+updated%3A2018-06-08..2018-06-14&type=Issues) | [@mariusvniekerk](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amariusvniekerk+updated%3A2018-06-08..2018-06-14&type=Issues)


### [1.2.1] - 2018-06-08

Minor patch release for bug in `resolved_username` regex.

#### Fixes
* Fix resolved_username regex [#75](https://github.com/jupyterhub/ldapauthenticator/pull/75) ([@dhirschfeld](https://github.com/dhirschfeld))

#### Improvements
* Improve packaging [#77](https://github.com/jupyterhub/ldapauthenticator/pull/77) ([@dhirschfeld](https://github.com/dhirschfeld)) - *Decoupled runtime dependencies from the build process*

#### Maintenance
* Minor cleanup of setup.py [#73](https://github.com/jupyterhub/ldapauthenticator/pull/73) ([@dhirschfeld](https://github.com/dhirschfeld))

#### Contributors to this release

[@dhirschfeld](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adhirschfeld+updated%3A2018-06-07..2018-06-08&type=Issues)


### [1.2.0] - 2018-06-07

#### Merged PRs
* Escape comma in resolved_username [#68](https://github.com/jupyterhub/ldapauthenticator/pull/68) ([@dhirschfeld](https://github.com/dhirschfeld))
* Fixed really bad error [#64](https://github.com/jupyterhub/ldapauthenticator/pull/64) ([@jcrubioa](https://github.com/jcrubioa))
* Don't force TLS bind if not using SSL. [#61](https://github.com/jupyterhub/ldapauthenticator/pull/61) ([@GrahamDumpleton](https://github.com/GrahamDumpleton))
* Catch exception thrown in getConnection [#56](https://github.com/jupyterhub/ldapauthenticator/pull/56) ([@dhirschfeld](https://github.com/dhirschfeld))
* Update LICENSE [#48](https://github.com/jupyterhub/ldapauthenticator/pull/48) ([@fm75](https://github.com/fm75))
* Switching to StartTLS instead of ssl [#46](https://github.com/jupyterhub/ldapauthenticator/pull/46) ([@toxadx](https://github.com/toxadx))
* Add yuvipanda's description of local user creation [#43](https://github.com/jupyterhub/ldapauthenticator/pull/43) ([@willingc](https://github.com/willingc))
* Update ldapauthenticator.py [#40](https://github.com/jupyterhub/ldapauthenticator/pull/40) ([@sauloal](https://github.com/sauloal))
* import union traitlet [#34](https://github.com/jupyterhub/ldapauthenticator/pull/34) ([@dirkcgrunwald](https://github.com/dirkcgrunwald))
* User CN name lookup with specific query [#32](https://github.com/jupyterhub/ldapauthenticator/pull/32) ([@mateuszboryn](https://github.com/mateuszboryn))
* Add better documentation for traitlets [#26](https://github.com/jupyterhub/ldapauthenticator/pull/26) ([@yuvipanda](https://github.com/yuvipanda))
* Extending ldapauthenticator to allow arbitrary LDAP search-filters  [#24](https://github.com/jupyterhub/ldapauthenticator/pull/24) ([@nklever](https://github.com/nklever))
* Support for multiple bind templates [#23](https://github.com/jupyterhub/ldapauthenticator/pull/23) ([@kishorchintal](https://github.com/kishorchintal))

#### Contributors to this release

[@beenje](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Abeenje+updated%3A2016-11-21..2018-06-07&type=Issues) | [@deebuls](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adeebuls+updated%3A2016-11-21..2018-06-07&type=Issues) | [@dhirschfeld](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adhirschfeld+updated%3A2016-11-21..2018-06-07&type=Issues) | [@dirkcgrunwald](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adirkcgrunwald+updated%3A2016-11-21..2018-06-07&type=Issues) | [@fm75](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Afm75+updated%3A2016-11-21..2018-06-07&type=Issues) | [@GrahamDumpleton](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3AGrahamDumpleton+updated%3A2016-11-21..2018-06-07&type=Issues) | [@jcrubioa](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ajcrubioa+updated%3A2016-11-21..2018-06-07&type=Issues) | [@kishorchintal](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Akishorchintal+updated%3A2016-11-21..2018-06-07&type=Issues) | [@mateuszboryn](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amateuszboryn+updated%3A2016-11-21..2018-06-07&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aminrk+updated%3A2016-11-21..2018-06-07&type=Issues) | [@nklever](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Anklever+updated%3A2016-11-21..2018-06-07&type=Issues) | [@pratik705](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Apratik705+updated%3A2016-11-21..2018-06-07&type=Issues) | [@sauloal](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Asauloal+updated%3A2016-11-21..2018-06-07&type=Issues) | [@toxadx](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Atoxadx+updated%3A2016-11-21..2018-06-07&type=Issues) | [@willingc](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Awillingc+updated%3A2016-11-21..2018-06-07&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ayuvipanda+updated%3A2016-11-21..2018-06-07&type=Issues)



## [1.1] - 2016-11-21

#### Merged PRs
* More options for ldap group membership [#22](https://github.com/jupyterhub/ldapauthenticator/pull/22) ([@m0zes](https://github.com/m0zes))
* Add info on invalidating existing logins [#18](https://github.com/jupyterhub/ldapauthenticator/pull/18) ([@yuvipanda](https://github.com/yuvipanda))
* Add more verbose logging for login failures [#17](https://github.com/jupyterhub/ldapauthenticator/pull/17) ([@yuvipanda](https://github.com/yuvipanda))
* Clarify usage of 'c.' [#16](https://github.com/jupyterhub/ldapauthenticator/pull/16) ([@yuvipanda](https://github.com/yuvipanda))
* Add support for looking up the account DN post-bind [#12](https://github.com/jupyterhub/ldapauthenticator/pull/12) ([@skemper](https://github.com/skemper))

#### Contributors to this release

[@m0zes](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Am0zes+updated%3A2016-03-28..2016-11-21&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aminrk+updated%3A2016-03-28..2016-11-21&type=Issues) | [@skemper](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Askemper+updated%3A2016-03-28..2016-11-21&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ayuvipanda+updated%3A2016-03-28..2016-11-21&type=Issues)



## [v1.0] - 2016-03-28

Initial release.
