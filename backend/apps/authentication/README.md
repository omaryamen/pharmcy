# apps/authentication — Identity & Access

Production authentication and identity module for PharmaCloud ERP. Replaces the
stock SimpleJWT views with a service layer that owns the full login lifecycle:
JWT session ledger, email/phone verification, password policies, brute-force
lockout, per-endpoint rate limiting and a security audit trail.

## Scope

| Concern | Where it lives |
| --- | --- |
| Session ledger (JWT refresh tracking) | `models/session.py` + `services/auth.py` |
| Verification / one-time codes | `models/token.py` + `services/verification.py` |
| Password reuse prevention | `models/password.py` + `services/password.py` |
| Security audit trail | `models/event.py` + `services/security.py` |
| Registration | `services/registration.py` |
| Brute-force protection | `throttles.py` + account lockout in `services/auth.py` |
| Emails / SMS | `notifications.py`, `tasks.py` (Celery) |

## Design highlights

- **Ledger as source of truth.** Every login opens a `LoginSession` row keyed by
  the refresh token's `jti`. Refresh slides that row to the rotated token;
  logout, password change and reset revoke it and blacklist the token
  (defence-in-depth via SimpleJWT's blacklist app). A revoked session can never
  refresh, even before its JWT expires.
- **No email enumeration.** Unknown emails and wrong passwords return the same
  `invalid_credentials` error, and the login path runs a constant-time dummy
  hash check so response timing does not leak account existence. Password-reset
  request always returns the same message.
- **Lockout that survives errors.** Failed-login counters and `login_failed`
  events are written *outside* the success-path transaction, so they persist
  even though the request returns 401/423 (see `services/auth.py`).
- **Codes are never stored in plaintext.** Verification codes are SHA-256
  digests compared with `secrets.compare_digest`; they are single-use, expire,
  and are rate-limited per token.
- **One usable code per user + kind.** Requesting a new code consumes all
  previous ones, so a leaked old code cannot be replayed.
- **Everything is audited.** `SecurityEvent` records logins, lockouts, password
  changes, verifications, session revocations and profile updates, including
  IP + user agent.

## Running tests

```bash
cd backend
.venv\Scripts\python.exe -m pytest tests -q
```

Auth coverage: `tests/test_auth_api.py`, `tests/test_verification.py`,
`tests/test_password.py`, `tests/test_sessions.py`, `tests/test_throttling.py`,
`tests/test_auth_models.py`, plus the shared helpers in `tests/helpers.py`.

## Configuration

All policy knobs are env-driven — see `docs/AUTH_CONFIG.md` for the full
reference and `config/settings/base.py` for defaults.

## Endpoints

See `docs/AUTH_API.md` for the request/response contracts and error codes.
Routes are mounted under `/api/v1/auth/*` in `api/urls.py`.
