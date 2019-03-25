# directory-forms-api

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]

**Export Directory forms API service**

A service with a write-only API for submitting schemaless JSON documents that represent a form submission, and then perform an action such as creating zendesk tickets, sending emails, etc.

---

### See also:
| [directory-ui-buyer](https://github.com/uktrade/directory-ui-buyer) | [directory-ui-supplier](https://github.com/uktrade/directory-ui-supplier) | [directory-ui-export-readiness](https://github.com/uktrade/directory-ui-export-readiness) |
| --- | --- | --- | --- |
| **[directory-sso](https://github.com/uktrade/directory-sso)** | **[directory-sso-proxy](https://github.com/uktrade/directory-sso-proxy)** | **[directory-sso-profile](https://github.com/uktrade/directory-sso-profile)** |  |

For more information on installation please check the [Developers Onboarding Checklist](https://uktrade.atlassian.net/wiki/spaces/ED/pages/32243946/Developers+onboarding+checklist)

## Requirements

[Python 3.6](https://www.python.org/downloads/release/python-366/)
[Redis](https://redis.io/)
[Postgres](https://www.postgresql.org/)

## Local installation

    $ git clone https://github.com/uktrade/directory-forms-api
    $ cd directory-forms-api
    $ make

## Integrations
Set the following values in your `conf/.env` file to use third-party services:

### Zendesk

`ZENDESK_EMAIL`
`ZENDESK_SUBDOMAIN`
`ZENDESK_TOKEN`

### Email

`EMAIL_HOST`
`EMAIL_HOST_PASSWORD`
`EMAIL_HOST_USER`
`EMAIL_PORT`
`EMAIL_USE_TLS`

## Development

### Setup development environment

    $ make debug

### Run debug webserver

    $ make debug_webserver

### Run debug tests

    $ make debug_test

## SSO
To make sso work locally add the following to your machine's `/etc/hosts`:

| IP Adress | URL                  |
| --------  | -------------------- |
| 127.0.0.1 | buyer.trade.great    |
| 127.0.0.1 | supplier.trade.great |
| 127.0.0.1 | sso.trade.great      |
| 127.0.0.1 | api.trade.great      |
| 127.0.0.1 | profile.trade.great  |
| 127.0.0.1 | exred.trade.great    |

Then log into `directory-sso` via `sso.trade.great:8004`

Note in production, the `directory-sso` session cookie is shared with all subdomains that are on the same parent domain as `directory-sso`. However in development we cannot share cookies between subdomains using `localhost` - that would be like trying to set a cookie for `.com`, which is not supported by any RFC.

Therefore to make cookie sharing work in development we need the apps to be running on subdomains. Some stipulations:
 - `directory-ui-supplier` and `directory-sso` must both be running on sibling subdomains (with same parent domain)
 - `directory-sso` must be told to target cookies at the parent domain.



[code-climate-image]: https://codeclimate.com/github/uktrade/directory-forms-api/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-forms-api

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-forms-api/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-forms-api/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-forms-api/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-forms-api
