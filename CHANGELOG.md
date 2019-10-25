# Changelog

## Pre release

### Implemented enhancements
- No ticket - Improve label of client model fields in django admin
- No ticket - update gov-notify sumbission type in testapi
- TT-1922 - activity-stream-integration
- TT-1975 - implement rate-limiting

### Fixed bugs:
- No ticket - Upgrade django to 1.11.23 to fix vulnerability
- No ticket - turn off staff sso enforcement on local dev
- No Ticker - fix-ip-restrictor

## [2019.08.12](https://github.com/uktrade/directory-forms-api/releases/tag/2019.08.12)
[Full Changelog](https://github.com/uktrade/directory-forms-api/compare/2019.07.09...2019.08.12)

### Implemented enhancements
- TT-1604 - Send Letter Gov Notify
- TT-1670 Allow-Govnotify send letters test mode set env GOV_NOTIFY_LETTER_API_KEY to test key to allow PDF viewing in Dev. In Prod set to live key
- TT-1692 - SSO integration   (setup ENVS STAFF_SSO_AUTHBROKER_URL/AUTHBROKER_CLIENT_ID/AUTHBROKER_CLIENT_SECRET, ENFORCE_STAFF_SSO_ON) 
- TT-1692 - enhanced to give user grant staff status using grant_staff_status managment command
- TT-1700 - Middleware admin status permission check
- TT-1735 - Forms & Directory-API SSO display message for 1st time users

## [2019.07.09](https://github.com/uktrade/directory-forms-api/releases/tag/2019.07.09)
[Full Changelog](https://github.com/uktrade/directory-forms-api/compare/2019.05.02...2019.07.09)

### Implemented enhancements
- TT-1591 - Expose ingress url to zendesk
- TT-1160 - Add auto retry to celery tasks
- No ticket - replace directory components IP whitelister

### Fixed bugs:
-  No ticket - Upgrade vulnerable django version to django 1.11.22
-  No ticket - Upgrade vulnerable django rest framework version

## [2019.05.02](https://github.com/uktrade/directory-forms-api/releases/tag/2019.05.02)
[Full Changelog](https://github.com/uktrade/directory-forms-api/compare/2019.01.28_1...2019.05.02)

### Fixed bugs:
- Upgraded urllib3 to fix [vulnerability](https://nvd.nist.gov/vuln/detail/CVE-2019-11324)
