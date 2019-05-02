# directory-forms-api

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![gitflow-image]][gitflow]
[![calver-image]][calver]

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

## Development

    $ git clone https://github.com/uktrade/directory-forms-api
    $ cd directory-forms-api
    $ virtualenv .venv -p python3.6
    $ source .venv/bin/activate
    $ pip install -r requirements_test.txt

### Configuration

Secrets such as API keys and environment specific configurations are placed in `conf/.env` - a file that is not added to version control. You will need to create that file locally in order for the project to run.

Here is an example `conf/.env` with placeholder values to get you going:

```
EMAIL_HOST=debug
EMAIL_HOST_PASSWORD=debug
EMAIL_HOST_USER=debug
EMAIL_USE_TLS=debug
ZENDESK_EMAIL=debug
ZENDESK_SUBDOMAIN=debug
ZENDESK_TOKEN=debug
ZENDESK_CUSTOM_FIELD_ID=debug
GOV_NOTIFY_API_KEY=debug
ZENDESK_SUBDOMAIN_EUEXIT=debug
ZENDESK_TOKEN_EUEXIT=debug
ZENDESK_EMAIL_EUEXIT=debug
ZENDESK_CUSTOM_FIELD_ID_EUEXIT=debug
```

## Running

### Setup development environment

    $ make debug

### Run debug webserver

    $ make debug_webserver

### Run debug tests

    $ make debug_test



[code-climate-image]: https://codeclimate.com/github/uktrade/directory-forms-api/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-forms-api

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-forms-api/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-forms-api/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-forms-api/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-forms-api

[gitflow-image]: https://img.shields.io/badge/Branching%20strategy-gitflow-5FBB1C.svg
[gitflow]: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow

[calver-image]: https://img.shields.io/badge/Versioning%20strategy-CalVer-5FBB1C.svg
[calver]: https://calver.org
