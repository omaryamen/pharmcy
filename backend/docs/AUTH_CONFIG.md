# Authentication Configuration Reference

All settings live in `config/settings/base.py` and are env-driven (defaults
shown). Override via `.env` / container environment. Test values are overridden
in `config/settings/testing.py`.

## Policy

| Setting | Default | Env var | Description |
| --- | --- | --- | --- |
| `AUTH_MAX_LOGIN_ATTEMPTS` | `5` | `AUTH_MAX_LOGIN_ATTEMPTS` | Consecutive failed logins before the account locks (`423`). |
| `AUTH_VERIFY_EMAIL_REQUIRED` | `True` | `AUTH_VERIFY_EMAIL_REQUIRED` | New registrations must verify email before first login. |
| `AUTH_VERIFICATION_CODE_LENGTH` | `6` | `AUTH_VERIFICATION_CODE_LENGTH` | Digit length of email/phone/reset OTPs. |
| `AUTH_VERIFICATION_CODE_LIFETIME_MINUTES` | `10` | `AUTH_VERIFICATION_CODE_LIFETIME_MINUTES` | OTP validity window. |
| `AUTH_VERIFICATION_MAX_ATTEMPTS` | `5` | `AUTH_VERIFICATION_MAX_ATTEMPTS` | Wrong-code budget per token before `429`. |
| `AUTH_PASSWORD_HISTORY_SIZE` | `5` | `AUTH_PASSWORD_HISTORY_SIZE` | Recent hashes compared on every password change/reset. |
| `AUTH_SESSION_LIFETIME_DAYS` | `30` | `AUTH_SESSION_LIFETIME_DAYS` | Refresh-token lifetime for a normal login. |
| `AUTH_REMEMBER_ME_LIFETIME_DAYS` | `90` | `AUTH_REMEMBER_ME_LIFETIME_DAYS` | Refresh-token lifetime for `remember_me=true`. |
| `AUTH_MAX_ACTIVE_SESSIONS` | `10` | `AUTH_MAX_ACTIVE_SESSIONS` | Concurrent sessions per user; the oldest is revoked past this cap. |
| `AUTH_SMS_BACKEND` | `""` | `AUTH_SMS_BACKEND` | Dotted import of `send_sms(phone, message)` for phone codes. Unset → code logged (dev only). |
| `AUTH_THROTTLE_WINDOW_SECONDS` | `300` | `AUTH_THROTTLE_WINDOW_SECONDS` | TTL for the Redis brute-force counters. |

## Rate limits

Configured in `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`. Defaults:

| Scope | Production | Testing |
| --- | --- | --- |
| `auth_login_email` | `10/min` | `100/min` |
| `auth_login_ip` | `30/min` | `300/min` |
| `auth_password_reset_email` | `5/hour` | `60/hour` |
| `auth_register_ip` | `5/min` | `60/min` |

The generic `anon` / `user` rates from `DEFAULT_THROTTLE_CLASSES` still apply.
Throttles use the Redis-backed default cache in production (locmem in tests).

## JWT (SimpleJWT)

`SIMPLE_JWT` is configured so refresh tokens rotate and are blacklisted:

- `ACCESS_TOKEN_LIFETIME`: `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` (default 60)
- `REFRESH_TOKEN_LIFETIME`: `JWT_REFRESH_TOKEN_LIFETIME_DAYS` (default 7) — the
  effective lifetime for logins is `AUTH_SESSION_LIFETIME_DAYS` /
  `AUTH_REMEMBER_ME_LIFETIME_DAYS`, which the service sets explicitly on every
  issued refresh token.
- `ROTATE_REFRESH_TOKENS: True`, `BLACKLIST_AFTER_ROTATION: True`
- `USER_ID_CLAIM: user_id`, `JTI_CLAIM: jti`

`rest_framework_simplejwt.token_blacklist` must stay in `INSTALLED_APPS`.

## Emails

`DEFAULT_FROM_EMAIL` is the sender for verification / reset / lockout emails.
Delivered via the Celery tasks in `apps/authentication/tasks.py`; in production
configure the standard `EMAIL_*` variables (SMTP/Amazon SES/SendGrid, etc.).

## Example `.env` overrides

```dotenv
AUTH_MAX_LOGIN_ATTEMPTS=5
AUTH_VERIFY_EMAIL_REQUIRED=true
AUTH_VERIFICATION_CODE_LENGTH=6
AUTH_VERIFICATION_CODE_LIFETIME_MINUTES=10
AUTH_VERIFICATION_MAX_ATTEMPTS=5
AUTH_PASSWORD_HISTORY_SIZE=5
AUTH_SESSION_LIFETIME_DAYS=30
AUTH_REMEMBER_ME_LIFETIME_DAYS=90
AUTH_MAX_ACTIVE_SESSIONS=10
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```
