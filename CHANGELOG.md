# Changelog

## Pre release

### Implemented enhancements

- No ticket - Improve filtering on Submission. Inline Submissions in Sender admin.

### Fixed bugs
- TT-2254 - Cleaned up obseolete settings
- TT-2261-non-recipient-email-fix

### Fixed bugs

## [2020.01.14](https://github.com/uktrade/directory-forms-api/releases/tag/2020.01.14)
[Full Changelog](https://github.com/uktrade/directory-forms-api/compare/2019.11.21_2...2020.01.14)

### Implemented enhancements
- TT-2199 - add testapi endpoint to delete submissions created by automated tests
- TT-2204 - add testapi endpoint to delete senders created by automated tests
- No ticket - Improve form url filter
- TT-2229 -add recipient email
- TT-2248 - Facilitate .internal domain communication

### Fixed bugs:
- TT-2228 - Use sender email address provded by meta.sender
- No ticket - Upgrade waitress to fix security vulnerability
- TT-2245 - error django download
- TT-2251 - zendesk-recipient-email

## [2019.11.21](https://github.com/uktrade/directory-forms-api/releases/tag/2019.11.21_2)
[Full Changelog](https://github.com/uktrade/directory-forms-api/compare/2019.22.10...2019.11.21_2)

### Implemented enhancements
- TT2100 fix type name error for activitystream
- No Ticket - configure redis for default cache 

## [2019.22.10](https://github.com/uktrade/directory-forms-api/releases/tag/2019.22.10)
[Full Changelog](https://github.com/uktrade/directory-forms-api/compare/2019.08.12...2019.22.10)

### Implemented enhancements
- No ticket - Improve label of client model fields in django admin
- No ticket - update gov-notify sumbission type in testapi
- TT-1922 - activity-stream-integration
- TT-1975 - implement rate-limiting
- TT-2043 - upgrade notify client
- TT-2062 - strip tags from email

### Fixed bugs:
- No ticket - Upgrade django to 1.11.23 to fix vulnerability
- No ticket - turn off staff sso enforcement on local dev
- No Ticker - fix-ip-restrictor
- TT-2066 - change activity stream Schema

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
