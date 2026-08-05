# Authentication API Reference

Base URL: `/api/v1`

All JSON responses are wrapped in the platform envelope:

```json
{
  "success": true,
  "status_code": 200,
  "message": "Success",
  "data": { ... },
  "errors": [],
  "meta": { "request_id": "...", "timestamp": "...", "version": "v1" }
}
```

Errors use `data: null` and a non-empty `errors` array, each item shaped
`{"code", "field", "message"}`. **Clients should branch on `code`**, never on the
human-readable message.

---

## Registration

### `POST /auth/register/`

Anonymous. Creates an account. When `AUTH_VERIFY_EMAIL_REQUIRED` is on (default),
the account starts as `pending_verification`, `is_active=false`, and a 6-digit
code is emailed.

Request:

```json
{
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "phone": "+967123456789",
  "password": "StrongPass!123"
}
```

`last_name` and `phone` are optional.

| Status | Code | Notes |
| --- | --- | --- |
| 201 | — | `data.verification_sent: true/false` |
| 409 | `email_taken` | email (case-insensitive) already registered |
| 422 | `weak_password` | fails Django password validators |
| 429 | `throttled` | per-IP registration throttle |

---

## Sessions (JWT)

### `POST /auth/token/` — login

Anonymous. Exchanges credentials for access + refresh tokens.

Request:

```json
{
  "email": "user@example.com",
  "password": "…",
  "remember_me": false
}
```

`remember_me` (optional) extends the refresh lifetime
(`AUTH_REMEMBER_ME_LIFETIME_DAYS` instead of `AUTH_SESSION_LIFETIME_DAYS`).

| Status | Code | Notes |
| --- | --- | --- |
| 200 | — | `data.access`, `data.refresh`, `data.user`, `data.session_id`, `data.expires_at` |
| 401 | `invalid_credentials` | wrong password *or* unknown email (identical) |
| 403 | `email_not_verified` | account exists but email unverified |
| 403 | `account_inactive` | status `inactive` |
| 423 | `account_locked` | locked after repeated failures (lockout email also sent) |
| 429 | `throttled` | per-email / per-IP login throttle |

### `POST /auth/token/refresh/` — rotate refresh token

Anonymous. Rotates the refresh token (the old one is blacklisted) and returns a
fresh pair.

| Status | Code | Notes |
| --- | --- | --- |
| 200 | — | `data.access`, `data.refresh`, `data.session_id` |
| 401 | `token_revoked` | token blacklisted / session revoked |
| 401 | `invalid_token` | malformed, expired or unknown token |

### `POST /auth/token/verify/` — validate access token

Anonymous. Returns 200 when the access token is valid and unexpired.

| Status | Code |
| --- | --- |
| 200 | — |
| 401 | `invalid_token` |

### `POST /auth/logout/` — revoke a refresh token

Anonymous and idempotent. Revokes the session and blacklists the token.

Request: `{ "refresh": "…" }` → 200 always (even for garbage/unknown tokens).

---

## Profile

### `GET /auth/me/` and `GET /auth/profile/`

Authenticated. Returns the current `User` resource.

### `PATCH /auth/profile/`

Authenticated. Updates editable preferences only
(`first_name`, `last_name`, `phone`, `language`, `timezone`, `avatar`).
`email`/`status` are never writable here. Records a `profile_updated` event.

| Status | Code | Notes |
| --- | --- | --- |
| 200 | — | updated `User` resource |
| 400 | `validation_error` (`field: timezone`) | unknown IANA timezone |

---

## Email / phone verification

### `POST /auth/email/verify/request/`

Anonymous. `email` is optional for authenticated callers.

| Status | Code | Notes |
| --- | --- | --- |
| 200 | — | `data.sent: true` (code emailed) or `false` (unknown email) |
| 409 | `email_already_verified` | already verified |
| 429 | `throttled` | per-email throttle |

### `POST /auth/email/verify/confirm/`

Anonymous. `email` optional for authenticated callers.

Request: `{ "email": "…", "code": "123456" }`

| Status | Code | Notes |
| --- | --- | --- |
| 200 | — | `data.email_verified: true`; account moved to `active` |
| 400 | `invalid_verification_code` | wrong/expired code (or unknown email) |
| 422 | `invalid_verification_code_format` | not 6 digits |
| 429 | `too_many_verification_attempts` | attempt budget exhausted — request a new code |

### `POST /auth/phone/verify/request/`

Authenticated. Requires the user to have a `phone`.

| Status | Code |
| --- | --- |
| 200 | — `data.sent: true` |
| 422 | `phone_required` |

### `POST /auth/phone/verify/confirm/`

Authenticated. Request: `{ "code": "123456" }` → 200 `data.phone_verified: true`.

---

## Passwords

### `POST /auth/password/reset/request/`

Anonymous. **Same response whether or not the email exists** (anti-enumeration).
Request: `{ "email": "…" }` → 200 always.

### `POST /auth/password/reset/confirm/`

Anonymous. Request:

```json
{ "email": "…", "code": "123456", "new_password": "FreshPass!456" }
```

| Status | Code | Notes |
| --- | --- | --- |
| 200 | — | password changed; all sessions revoked; locked account is unlocked |
| 400 | `invalid_verification_code` | bad/expired code (or unknown email) |
| 422 | `password_reuse` / `weak_password` | policy violations |

### `POST /auth/password/change/`

Authenticated. Request:

```json
{ "current_password": "…", "new_password": "FreshPass!456" }
```

| Status | Code | Notes |
| --- | --- | --- |
| 200 | — | changed; **all** sessions (incl. current) revoked |
| 400 | `incorrect_current_password` | `field: current_password` |
| 422 | `password_reuse` | new password in recent history (`field: new_password`) |
| 422 | `weak_password` | fails validators |

---

## Sessions & audit trail

### `GET /auth/sessions/`

Authenticated. Active (and only active) login sessions for the current user.

### `POST /auth/sessions/<uuid:pk>/revoke/`

Authenticated. Revokes one of the user's own sessions.

| Status | Code |
| --- | --- |
| 200 | — revoked session resource |
| 404 | `not_found` | unknown id or another user's session |

### `POST /auth/sessions/revoke-all/`

Authenticated. Signs the user out everywhere → 200 `data.revoked: <count>`.

### `GET /auth/security/events/`

Authenticated. The current user's recent security events (most recent first,
max 100). Event types: `registered`, `login_success`, `login_failed`,
`login_locked`, `logout`, `token_refreshed`, `email_verified`,
`phone_verified`, `password_changed`, `password_reset_confirmed`,
`session_revoked`, `account_locked`, `account_unlocked`, `profile_updated`, …

---

## Error codes (summary)

| Code | HTTP | Meaning |
| --- | --- | --- |
| `invalid_credentials` | 401 | wrong password or unknown email |
| `email_not_verified` | 403 | must verify email before login |
| `account_inactive` | 403 | account deactivated |
| `account_locked` | 423 | locked after repeated failures |
| `email_taken` | 409 | registration duplicate |
| `email_already_verified` | 409 | resend on verified email |
| `invalid_verification_code` | 400 | wrong/expired code |
| `invalid_verification_code_format` | 422 | not N digits |
| `too_many_verification_attempts` | 429 | OTP attempt budget spent |
| `incorrect_current_password` | 400 | wrong current password |
| `password_reuse` | 422 | recent password reused |
| `weak_password` | 422 | password policy failure |
| `invalid_token` | 401 | malformed/expired token |
| `token_revoked` | 401 | token blacklisted / session revoked |
| `throttled` | 429 | rate limit exceeded |
