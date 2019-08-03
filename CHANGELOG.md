# Changelog

## Pre release

### Implemented enhancements
- TT-1604 - Send Letter Gov Notify
- TT-1670 Allow-Govnotify send letters test mode set env GOV_NOTIFY_LETTER_API_KEY to test key to allow PDF viewing in Dev. In Prod set to live key
- TT-1692 - SSO integration   (setup ENVS STAFF_SSO_AUTHBROKER_URL/AUTHBROKER_CLIENT_ID/AUTHBROKER_CLIENT_SECRET, ENFORCE_STAFF_SSO_ON) 
- TT-1692 - enhanced to give user grant staff status using grant_staff_status managment command

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
