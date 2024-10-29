# Changelog

## 2.0

### 2.0.1 - 2024-10-29

([full changelog](https://github.com/jupyterhub/ldapauthenticator/compare/2.0.0...2.0.1))

#### Bugs fixed

- fix: Ensure a list `bind_dn_template` is properly validated [#289](https://github.com/jupyterhub/ldapauthenticator/pull/289) ([@mahendrapaipuri](https://github.com/mahendrapaipuri))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/ldapauthenticator/graphs/contributors?from=2024-10-18&to=2024-10-29&type=c))

[@mahendrapaipuri](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amahendrapaipuri+updated%3A2024-10-18..2024-10-29&type=Issues)

### 2.0.0 - 2024-10-18

([full changelog](https://github.com/jupyterhub/ldapauthenticator/compare/1.3.2...2.0.0))

#### Breaking Changes

- `python>=3.9`, `jupyterhub>=4.1.6`, and `ldap3>=2.9.1` is now required.
  ([#245](https://github.com/jupyterhub/ldapauthenticator/pull/245),
  [#256](https://github.com/jupyterhub/ldapauthenticator/pull/256))
- Configuring `auth_state_attributes` now leads to user information being put in
  `auth_state["user_attributes"]` and not directly in `auth_state`.
  ([#269](https://github.com/jupyterhub/ldapauthenticator/pull/269))
- `use_lookup_dn_username` now defaults to False and is opt-in instead of
  opt-out. To retain previous behavior if you had `lookup_dn` set True without
  `use_lookup_dn_username` explicitly set, configure `use_lookup_dn_username` to
  True. ([#280](https://github.com/jupyterhub/ldapauthenticator/pull/280))
- `lookup_dn` now rejects an authenticating user if multiple DNs are returned
  during lookup. ([#276](https://github.com/jupyterhub/ldapauthenticator/pull/276))
- In the edge case if both...

  1. the following config is used:
     - `lookup_dn = True`,
     - `lookup_dn_user_dn_attribute = "cn"`
     - `use_lookup_dn_username = True` (previous default value)
  2. and one or more users previously signed in at least once had a comma in
     their `cn` attribute's value

  then such users will get a new JupyterHub username going forward looking like
  `"lastname, firstname"` instead of looking like `"lastname\\, firstname"`.
  ([#267](https://github.com/jupyterhub/ldapauthenticator/pull/267))

#### Deprecations

- `use_ssl` has been deprecated, instead configure `tls_strategy` going forward.
  Configuring `use_ssl=True` should be updated with `tls_strategy="on_connect"`,
  and configuring `use_ssl=False` could be updated to either be
  `tls_strategy="before_bind"` (default) or `tls_strategy="insecure"`.
  ([#258](https://github.com/jupyterhub/ldapauthenticator/pull/258))
- `escape_userdn` has been deprecated, usernames used to construct DNs are now
  always escaped according to LDAP protocol specification of how DNs should be
  represented in string format.
  ([#267](https://github.com/jupyterhub/ldapauthenticator/pull/267))

#### New features added

- Add LDAPAuthenticator.version_info [#282](https://github.com/jupyterhub/ldapauthenticator/pull/282) ([@consideRatio](https://github.com/consideRatio))
- Add `tls_kwargs` config to configure underlying ldap3 package tls [#273](https://github.com/jupyterhub/ldapauthenticator/pull/273) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Add `tls_strategy` and deprecate `use_ssl` [#258](https://github.com/jupyterhub/ldapauthenticator/pull/258) ([@consideRatio](https://github.com/consideRatio), [@manics](https://github.com/manics), [@loic-vial](https://github.com/loic-vial), [@1kastner](https://github.com/1kastner))
- Allow users to configure group search filter and attributes (`group_search_filter` and `group_attributes` config) [#168](https://github.com/jupyterhub/ldapauthenticator/pull/168) ([@kinow](https://github.com/kinow), [@consideRatio](https://github.com/consideRatio), [@manics](https://github.com/manics), [@ordlucas](https://github.com/ordlucas), [@mananpreetsingh](https://github.com/mananpreetsingh))

#### Enhancements made

- Docs updates, and a few tweaks to the allow config [#286](https://github.com/jupyterhub/ldapauthenticator/pull/286) ([@manics](https://github.com/manics), [@minrk](https://github.com/minrk))
- Register authenticator class with jupyterhub as ldap [#249](https://github.com/jupyterhub/ldapauthenticator/pull/249) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))

#### Bugs fixed

- Require a unique DN to be found when using lookup_dn [#276](https://github.com/jupyterhub/ldapauthenticator/pull/276) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Fix duplicated bind operation, only one is needed [#270](https://github.com/jupyterhub/ldapauthenticator/pull/270) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Escape username within DN correctly and remove `escape_userdn` [#267](https://github.com/jupyterhub/ldapauthenticator/pull/267) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Escape user- or ldap-provided strings in ldap search filters [#238](https://github.com/jupyterhub/ldapauthenticator/pull/238) ([@m-erhardt](https://github.com/m-erhardt), [@consideRatio](https://github.com/consideRatio))

#### Maintenance and upkeep improvements

- Remove empty scripts file [#287](https://github.com/jupyterhub/ldapauthenticator/pull/287) ([@manics](https://github.com/manics), [@minrk](https://github.com/minrk))
- Comment consistently about escape_rdn and escape_filter_chars [#284](https://github.com/jupyterhub/ldapauthenticator/pull/284) ([@consideRatio](https://github.com/consideRatio))
- Validate config on startup when possible (allowed_groups, lookup_dn, bind_dn_template) [#283](https://github.com/jupyterhub/ldapauthenticator/pull/283) ([@consideRatio](https://github.com/consideRatio))
- tests: pass config to constructor instead of configuring after [#281](https://github.com/jupyterhub/ldapauthenticator/pull/281) ([@consideRatio](https://github.com/consideRatio))
- Change `use_lookup_dn_username` default value to False [#280](https://github.com/jupyterhub/ldapauthenticator/pull/280) ([@consideRatio](https://github.com/consideRatio))
- Fix a log message about lookup_dn_user_dn_attribute [#278](https://github.com/jupyterhub/ldapauthenticator/pull/278) ([@consideRatio](https://github.com/consideRatio))
- refactor: distinguish login_username from resolved_username [#277](https://github.com/jupyterhub/ldapauthenticator/pull/277) ([@consideRatio](https://github.com/consideRatio))
- Add missing docs for `search_filter` and `attributes` and improve logging for `search_filter` [#275](https://github.com/jupyterhub/ldapauthenticator/pull/275) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Improve logging, docstring, and variable naming in `resolve_username` function [#274](https://github.com/jupyterhub/ldapauthenticator/pull/274) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- align `allowed_groups` with other `allowed_` config, consistent in JupyterHub 5 [#269](https://github.com/jupyterhub/ldapauthenticator/pull/269) ([@minrk](https://github.com/minrk), [@consideRatio](https://github.com/consideRatio), [@manics](https://github.com/manics))
- refactor: specify param names for Connection.search consistently [#268](https://github.com/jupyterhub/ldapauthenticator/pull/268) ([@consideRatio](https://github.com/consideRatio))
- refactor: reduce use of temporary variables [#264](https://github.com/jupyterhub/ldapauthenticator/pull/264) ([@consideRatio](https://github.com/consideRatio))
- Relocate example snippet from code to readme [#257](https://github.com/jupyterhub/ldapauthenticator/pull/257) ([@consideRatio](https://github.com/consideRatio))
- Require ldap3 2.9.1+ released 2021 (currently latest) as a lower bound [#256](https://github.com/jupyterhub/ldapauthenticator/pull/256) ([@consideRatio](https://github.com/consideRatio))
- Transition to async functions and remove tornado dependency [#255](https://github.com/jupyterhub/ldapauthenticator/pull/255) ([@consideRatio](https://github.com/consideRatio))
- tests: avoid reuse of authenticator fixture between tests and add docstring [#254](https://github.com/jupyterhub/ldapauthenticator/pull/254) ([@consideRatio](https://github.com/consideRatio))
- Fix incorrect log message (debug level) [#252](https://github.com/jupyterhub/ldapauthenticator/pull/252) ([@consideRatio](https://github.com/consideRatio))
- refactor: reduce use of temporary variables like msg for logging [#251](https://github.com/jupyterhub/ldapauthenticator/pull/251) ([@consideRatio](https://github.com/consideRatio))
- refactor: put validation logic in traitlets validation functions [#250](https://github.com/jupyterhub/ldapauthenticator/pull/250) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Update ldap testing server to the latest available version [#247](https://github.com/jupyterhub/ldapauthenticator/pull/247) ([@consideRatio](https://github.com/consideRatio))
- Require jupyterhub 4.1.6+ and Python 3.9+ [#245](https://github.com/jupyterhub/ldapauthenticator/pull/245) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Fix traitlets warnings when running tests [#169](https://github.com/jupyterhub/ldapauthenticator/pull/169) ([@kinow](https://github.com/kinow), [@minrk](https://github.com/minrk), [@manics](https://github.com/manics))

#### Documentation improvements

- Docs updates, and a few tweaks to the allow config [#286](https://github.com/jupyterhub/ldapauthenticator/pull/286) ([@manics](https://github.com/manics), [@minrk](https://github.com/minrk))
- docs: update a few config descriptions [#279](https://github.com/jupyterhub/ldapauthenticator/pull/279) ([@consideRatio](https://github.com/consideRatio))
- docs: fix readme example based on investigation by MakarovDi [#262](https://github.com/jupyterhub/ldapauthenticator/pull/262) ([@consideRatio](https://github.com/consideRatio))
- docs: add two docstrings and fix an example in another [#248](https://github.com/jupyterhub/ldapauthenticator/pull/248) ([@consideRatio](https://github.com/consideRatio))
- Update README.md with details on jupyterhub_config.py [#242](https://github.com/jupyterhub/ldapauthenticator/pull/242) ([@jdkruzr](https://github.com/jdkruzr), [@consideRatio](https://github.com/consideRatio))
- Update README.md [#228](https://github.com/jupyterhub/ldapauthenticator/pull/228) ([@ehooi](https://github.com/ehooi), [@yuvipanda](https://github.com/yuvipanda))
- Add study participation notice to readme [#197](https://github.com/jupyterhub/ldapauthenticator/pull/197) ([@sgibson91](https://github.com/sgibson91), [@yuvipanda](https://github.com/yuvipanda), [@manics](https://github.com/manics))

#### Continuous integration improvements

- ci: test jupyterhub 5 and python 3.12, refresh github workflows [#244](https://github.com/jupyterhub/ldapauthenticator/pull/244) ([@consideRatio](https://github.com/consideRatio))
- ci: fix testing ldap server port mapping for broken gate [#192](https://github.com/jupyterhub/ldapauthenticator/pull/192) ([@bloodeagle40234](https://github.com/bloodeagle40234), [@manics](https://github.com/manics))
- ci: Replace Travis with GitHub workflow [#188](https://github.com/jupyterhub/ldapauthenticator/pull/188) ([@manics](https://github.com/manics), [@consideRatio](https://github.com/consideRatio))

#### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/jupyterhub/ldapauthenticator/graphs/contributors?from=2020-08-28&to=2024-10-18&type=c))

@1kastner ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3A1kastner+updated%3A2020-08-28..2024-10-18&type=Issues)) | @Aethylred ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3AAethylred+updated%3A2020-08-28..2024-10-18&type=Issues)) | @bloodeagle40234 ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Abloodeagle40234+updated%3A2020-08-28..2024-10-18&type=Issues)) | @brindapabari ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Abrindapabari+updated%3A2020-08-28..2024-10-18&type=Issues)) | @consideRatio ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3AconsideRatio+updated%3A2020-08-28..2024-10-18&type=Issues)) | @Cronan ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3ACronan+updated%3A2020-08-28..2024-10-18&type=Issues)) | @dhirschfeld ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adhirschfeld+updated%3A2020-08-28..2024-10-18&type=Issues)) | @dmpe ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Admpe+updated%3A2020-08-28..2024-10-18&type=Issues)) | @edergillian ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aedergillian+updated%3A2020-08-28..2024-10-18&type=Issues)) | @ehooi ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aehooi+updated%3A2020-08-28..2024-10-18&type=Issues)) | @GlennHD ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3AGlennHD+updated%3A2020-08-28..2024-10-18&type=Issues)) | @healinyoon ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ahealinyoon+updated%3A2020-08-28..2024-10-18&type=Issues)) | @jdkruzr ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ajdkruzr+updated%3A2020-08-28..2024-10-18&type=Issues)) | @kinow ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Akinow+updated%3A2020-08-28..2024-10-18&type=Issues)) | @loic-vial ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aloic-vial+updated%3A2020-08-28..2024-10-18&type=Issues)) | @m-erhardt ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Am-erhardt+updated%3A2020-08-28..2024-10-18&type=Issues)) | @mananpreetsingh ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amananpreetsingh+updated%3A2020-08-28..2024-10-18&type=Issues)) | @manics ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amanics+updated%3A2020-08-28..2024-10-18&type=Issues)) | @mannevijayakrishna ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amannevijayakrishna+updated%3A2020-08-28..2024-10-18&type=Issues)) | @marcusianlevine ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amarcusianlevine+updated%3A2020-08-28..2024-10-18&type=Issues)) | @marty90 ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amarty90+updated%3A2020-08-28..2024-10-18&type=Issues)) | @minrk ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aminrk+updated%3A2020-08-28..2024-10-18&type=Issues)) | @mk-raven ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amk-raven+updated%3A2020-08-28..2024-10-18&type=Issues)) | @Nikolai-Hlubek ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3ANikolai-Hlubek+updated%3A2020-08-28..2024-10-18&type=Issues)) | @nylocx ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Anylocx+updated%3A2020-08-28..2024-10-18&type=Issues)) | @ordlucas ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aordlucas+updated%3A2020-08-28..2024-10-18&type=Issues)) | @Ownercz ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3AOwnercz+updated%3A2020-08-28..2024-10-18&type=Issues)) | @ragul-inv ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aragul-inv+updated%3A2020-08-28..2024-10-18&type=Issues)) | @reinierpost ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Areinierpost+updated%3A2020-08-28..2024-10-18&type=Issues)) | @sebastian-luna-valero ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Asebastian-luna-valero+updated%3A2020-08-28..2024-10-18&type=Issues)) | @sgibson91 ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Asgibson91+updated%3A2020-08-28..2024-10-18&type=Issues)) | @wiltonsr ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Awiltonsr+updated%3A2020-08-28..2024-10-18&type=Issues)) | @wsuzume ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Awsuzume+updated%3A2020-08-28..2024-10-18&type=Issues)) | @ygean ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aygean+updated%3A2020-08-28..2024-10-18&type=Issues)) | @yuvipanda ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ayuvipanda+updated%3A2020-08-28..2024-10-18&type=Issues))

## 1.3

### 1.3.2 - 2020-08-28

#### Fixes

- Exchanging ldap3 constants in if/else ([#175](https://github.com/jupyterhub/ldapauthenticator/pull/175)) ([@1kastner](https://github.com/1kastner))

### 1.3.1 - 2020-08-13

#### Fixes

- Pin ldap3 version to lower than 2.8 ([#172](https://github.com/jupyterhub/ldapauthenticator/pull/172)) ([@1kastner](https://github.com/1kastner))

### 1.3.0 - 2020-02-09

#### Fixes

- Avoid binding the connection twice [#142](https://github.com/jupyterhub/ldapauthenticator/pull/142) ([@m2hofi94](https://github.com/m2hofi94))
- Gracefully handle username lookups with list return values [#117](https://github.com/jupyterhub/ldapauthenticator/pull/117) ([@metrofun](https://github.com/metrofun))
- Misc cleanup + fixes [#95](https://github.com/jupyterhub/ldapauthenticator/pull/95) ([@dhirschfeld](https://github.com/dhirschfeld)) - _Empty DN templates are now ignored, `search_filter` and `allowed_groups` are no longer mutually exclusive._

#### Improvements

- Allow authentication with empty bind_dn_template when using lookup_dn [#106](https://github.com/jupyterhub/ldapauthenticator/pull/106) ([@behrmann](https://github.com/behrmann))
- Ignore username returned by `resolve_username` [#105](https://github.com/jupyterhub/ldapauthenticator/pull/105) ([@behrmann](https://github.com/behrmann)) - _`use_lookup_dn_username` configuration option added._
- Lookup additional LDAP user info [#103](https://github.com/jupyterhub/ldapauthenticator/pull/103) ([@manics](https://github.com/manics)) - _`user_info_attributes` is now saved in `auth_state` for a valid user._

#### Maintenance

- Fix CI linting failures and add testing of Py38 [#157](https://github.com/jupyterhub/ldapauthenticator/pull/157) ([@consideRatio](https://github.com/consideRatio))
- Add long description for pypi [#155](https://github.com/jupyterhub/ldapauthenticator/pull/155) ([@manics](https://github.com/manics))
- Add badges according to team-compass [#154](https://github.com/jupyterhub/ldapauthenticator/pull/154) ([@consideRatio](https://github.com/consideRatio))
- Travis deploy tags to PyPI [#153](https://github.com/jupyterhub/ldapauthenticator/pull/153) ([@manics](https://github.com/manics))
- Add bind_dn_template to Active Directory instructions [#147](https://github.com/jupyterhub/ldapauthenticator/pull/147) ([@irasnyd](https://github.com/irasnyd))
- Expand contributor's guide [#135](https://github.com/jupyterhub/ldapauthenticator/pull/135) ([@marcusianlevine](https://github.com/marcusianlevine))
- Add Travis CI setup and simple tests [#134](https://github.com/jupyterhub/ldapauthenticator/pull/134) ([@marcusianlevine](https://github.com/marcusianlevine))
- Update project url in setup.py [#92](https://github.com/jupyterhub/ldapauthenticator/pull/92) ([@dhirschfeld](https://github.com/dhirschfeld))
- Update README.md [#85](https://github.com/jupyterhub/ldapauthenticator/pull/85) ([@dhirschfeld](https://github.com/dhirschfeld))
- Bump version to 1.2.2 [#84](https://github.com/jupyterhub/ldapauthenticator/pull/84) ([@dhirschfeld](https://github.com/dhirschfeld))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/ldapauthenticator/graphs/contributors?from=2018-06-14&to=2020-01-31&type=c))

[@behrmann](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Abehrmann+updated%3A2018-06-14..2020-01-31&type=Issues) | [@betatim](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Abetatim+updated%3A2018-06-14..2020-01-31&type=Issues) | [@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3AconsideRatio+updated%3A2018-06-14..2020-01-31&type=Issues) | [@dhirschfeld](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adhirschfeld+updated%3A2018-06-14..2020-01-31&type=Issues) | [@irasnyd](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Airasnyd+updated%3A2018-06-14..2020-01-31&type=Issues) | [@m2hofi94](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Am2hofi94+updated%3A2018-06-14..2020-01-31&type=Issues) | [@manics](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amanics+updated%3A2018-06-14..2020-01-31&type=Issues) | [@marcusianlevine](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amarcusianlevine+updated%3A2018-06-14..2020-01-31&type=Issues) | [@meeseeksmachine](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ameeseeksmachine+updated%3A2018-06-14..2020-01-31&type=Issues) | [@metrofun](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ametrofun+updated%3A2018-06-14..2020-01-31&type=Issues) | [@ramkrishnan8994](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aramkrishnan8994+updated%3A2018-06-14..2020-01-31&type=Issues) | [@titansmc](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Atitansmc+updated%3A2018-06-14..2020-01-31&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ayuvipanda+updated%3A2018-06-14..2020-01-31&type=Issues)

## 1.2

### 1.2.2 - 2018-06-14

Minor patch release for incorrectly escaping commas in `resolved_username`

#### Fixes

- Fix comma escape in `resolved_username` [#83](https://github.com/jupyterhub/ldapauthenticator/pull/83) ([@dhirschfeld](https://github.com/dhirschfeld))

#### Improvements

- Add manifest to package license [#74](https://github.com/jupyterhub/ldapauthenticator/pull/74) ([@mariusvniekerk](https://github.com/mariusvniekerk)) - _Adds license file to the sdist_

## Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/ldapauthenticator/graphs/contributors?from=2018-06-08&to=2018-06-14&type=c))

[@dhirschfeld](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adhirschfeld+updated%3A2018-06-08..2018-06-14&type=Issues) | [@mariusvniekerk](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amariusvniekerk+updated%3A2018-06-08..2018-06-14&type=Issues)

### 1.2.1 - 2018-06-08

Minor patch release for bug in `resolved_username` regex.

#### Fixes

- Fix resolved_username regex [#75](https://github.com/jupyterhub/ldapauthenticator/pull/75) ([@dhirschfeld](https://github.com/dhirschfeld))

#### Improvements

- Improve packaging [#77](https://github.com/jupyterhub/ldapauthenticator/pull/77) ([@dhirschfeld](https://github.com/dhirschfeld)) - _Decoupled runtime dependencies from the build process_

#### Maintenance

- Minor cleanup of setup.py [#73](https://github.com/jupyterhub/ldapauthenticator/pull/73) ([@dhirschfeld](https://github.com/dhirschfeld))

#### Contributors to this release

[@dhirschfeld](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adhirschfeld+updated%3A2018-06-07..2018-06-08&type=Issues)

### 1.2.0 - 2018-06-07

#### Merged PRs

- Escape comma in resolved_username [#68](https://github.com/jupyterhub/ldapauthenticator/pull/68) ([@dhirschfeld](https://github.com/dhirschfeld))
- Fixed really bad error [#64](https://github.com/jupyterhub/ldapauthenticator/pull/64) ([@jcrubioa](https://github.com/jcrubioa))
- Don't force TLS bind if not using SSL. [#61](https://github.com/jupyterhub/ldapauthenticator/pull/61) ([@GrahamDumpleton](https://github.com/GrahamDumpleton))
- Catch exception thrown in getConnection [#56](https://github.com/jupyterhub/ldapauthenticator/pull/56) ([@dhirschfeld](https://github.com/dhirschfeld))
- Update LICENSE [#48](https://github.com/jupyterhub/ldapauthenticator/pull/48) ([@fm75](https://github.com/fm75))
- Switching to StartTLS instead of ssl [#46](https://github.com/jupyterhub/ldapauthenticator/pull/46) ([@toxadx](https://github.com/toxadx))
- Add yuvipanda's description of local user creation [#43](https://github.com/jupyterhub/ldapauthenticator/pull/43) ([@willingc](https://github.com/willingc))
- Update ldapauthenticator.py [#40](https://github.com/jupyterhub/ldapauthenticator/pull/40) ([@sauloal](https://github.com/sauloal))
- import union traitlet [#34](https://github.com/jupyterhub/ldapauthenticator/pull/34) ([@dirkcgrunwald](https://github.com/dirkcgrunwald))
- User CN name lookup with specific query [#32](https://github.com/jupyterhub/ldapauthenticator/pull/32) ([@mateuszboryn](https://github.com/mateuszboryn))
- Add better documentation for traitlets [#26](https://github.com/jupyterhub/ldapauthenticator/pull/26) ([@yuvipanda](https://github.com/yuvipanda))
- Extending ldapauthenticator to allow arbitrary LDAP search-filters [#24](https://github.com/jupyterhub/ldapauthenticator/pull/24) ([@nklever](https://github.com/nklever))
- Support for multiple bind templates [#23](https://github.com/jupyterhub/ldapauthenticator/pull/23) ([@kishorchintal](https://github.com/kishorchintal))

#### Contributors to this release

[@beenje](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Abeenje+updated%3A2016-11-21..2018-06-07&type=Issues) | [@deebuls](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adeebuls+updated%3A2016-11-21..2018-06-07&type=Issues) | [@dhirschfeld](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adhirschfeld+updated%3A2016-11-21..2018-06-07&type=Issues) | [@dirkcgrunwald](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Adirkcgrunwald+updated%3A2016-11-21..2018-06-07&type=Issues) | [@fm75](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Afm75+updated%3A2016-11-21..2018-06-07&type=Issues) | [@GrahamDumpleton](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3AGrahamDumpleton+updated%3A2016-11-21..2018-06-07&type=Issues) | [@jcrubioa](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ajcrubioa+updated%3A2016-11-21..2018-06-07&type=Issues) | [@kishorchintal](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Akishorchintal+updated%3A2016-11-21..2018-06-07&type=Issues) | [@mateuszboryn](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Amateuszboryn+updated%3A2016-11-21..2018-06-07&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aminrk+updated%3A2016-11-21..2018-06-07&type=Issues) | [@nklever](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Anklever+updated%3A2016-11-21..2018-06-07&type=Issues) | [@pratik705](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Apratik705+updated%3A2016-11-21..2018-06-07&type=Issues) | [@sauloal](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Asauloal+updated%3A2016-11-21..2018-06-07&type=Issues) | [@toxadx](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Atoxadx+updated%3A2016-11-21..2018-06-07&type=Issues) | [@willingc](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Awillingc+updated%3A2016-11-21..2018-06-07&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ayuvipanda+updated%3A2016-11-21..2018-06-07&type=Issues)

## 1.1

### 1.1.0 - 2016-11-21

#### Merged PRs

- More options for ldap group membership [#22](https://github.com/jupyterhub/ldapauthenticator/pull/22) ([@m0zes](https://github.com/m0zes))
- Add info on invalidating existing logins [#18](https://github.com/jupyterhub/ldapauthenticator/pull/18) ([@yuvipanda](https://github.com/yuvipanda))
- Add more verbose logging for login failures [#17](https://github.com/jupyterhub/ldapauthenticator/pull/17) ([@yuvipanda](https://github.com/yuvipanda))
- Clarify usage of 'c.' [#16](https://github.com/jupyterhub/ldapauthenticator/pull/16) ([@yuvipanda](https://github.com/yuvipanda))
- Add support for looking up the account DN post-bind [#12](https://github.com/jupyterhub/ldapauthenticator/pull/12) ([@skemper](https://github.com/skemper))

#### Contributors to this release

[@m0zes](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Am0zes+updated%3A2016-03-28..2016-11-21&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Aminrk+updated%3A2016-03-28..2016-11-21&type=Issues) | [@skemper](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Askemper+updated%3A2016-03-28..2016-11-21&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fldapauthenticator+involves%3Ayuvipanda+updated%3A2016-03-28..2016-11-21&type=Issues)

## 1.0

### 1.0.0 - 2016-03-28

Initial release.
