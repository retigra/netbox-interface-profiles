# Compatibility

This document tracks the minimum and maximum supported NetBox versions for each
release of Interface Profiles.

| Plugin Version | Minimum NetBox Version | Maximum NetBox Version | Python |
| -------------- | ---------------------- | ---------------------- | ------ |
| 0.1.x          | 4.7.0                  | 4.7.99                 | 3.12+  |

## Upgrading

When upgrading NetBox or this plugin:

1. Review the [changelog](CHANGELOG.md) and the
   [NetBox release notes](https://netboxlabs.com/docs/netbox/release-notes/) for
   breaking changes
2. Test the upgrade in a development environment
3. Back up your database before upgrading production
4. Run database migrations: `python manage.py migrate`
5. Collect static files: `python manage.py collectstatic --no-input`
6. Restart NetBox and its worker

See the
[compatibility documentation](https://wouterdebruijn.github.io/netbox-interface-profiles/latest/reference/compatibility/)
for details.
