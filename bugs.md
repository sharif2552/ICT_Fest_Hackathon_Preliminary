# Team Bug Tracker

This is our shared hackathon tracking board. Use it to avoid duplicate work, keep proof for every bug, and coordinate direct commits during the round.

Before changing this file:

```bash
git pull --rebase
```

After adding a claim, reproduction, fix note, verification result, or push note:

```bash
git add bugs.md
git commit -m "chore: update bug tracker"
git push
```

The final judge-facing explanation should go in `bug_report.md`. This file is our working board.

## Team Sync Rule

Every work block follows this cycle:

```bash
git pull --rebase
git status --short
# work on one bug claim, reproduction, fix, verification, or report update
git add <changed-files>
git commit -m "clear bug-specific message"
git pull --rebase
git push
```

For a new bug, push the `bugs.md` claim before working on the fix:

```bash
git pull --rebase
# add BUG-XXX to the Live Board
git add bugs.md
git commit -m "chore: claim BUG-XXX short area"
git pull --rebase
git push
```

If the second `git pull --rebase` creates conflicts, resolve them, rerun the focused verification if code changed, then push.

## Status Flow

```text
SUSPECTED -> CLAIMED -> REPRODUCED -> ROOT_CAUSED -> FIXING -> FIXED -> VERIFIED -> REPORTED
```

Other useful statuses:

```text
STALE
REJECTED
BLOCKED
PUSHED
```

## Live Board

| Bug ID | Status | Owner | Last Updated | Area / Workflow | Difficulty Guess | Commit(s) | Evidence |
|---|---|---|---|---|---|---|---|
| BUG-001 | REPORTED | nahid | 2026-07-09 | auth / access token lifetime | Medium | | `app/auth.py:50` |
| BUG-002 | REPORTED | nahid | 2026-07-09 | auth / JWT secret config | Medium | | `app/config.py:8`, `docker-compose.yml:6` |
| BUG-003 | REPORTED | nahid | 2026-07-09 | admin export / multi-tenancy | Hard | | `app/services/export.py:22-50` |
| BUG-004 | REPORTED | nahid | 2026-07-09 | auth / logout revocation | Medium | | `app/auth.py:85-98` |
| BUG-005 | REPORTED | nahid | 2026-07-09 | auth / refresh token reuse | Medium | | `app/routers/auth.py:81-93` |
| BUG-006 | REPORTED | nahid | 2026-07-09 | auth / registration | Medium | | `app/routers/auth.py:32-43` |
| BUG-007 | REPORTED | nahid | 2026-07-09 | bookings / create validation | Medium | | `app/routers/bookings.py:86` |
| BUG-008 | REPORTED | nahid | 2026-07-09 | bookings / create validation | Medium | | `app/routers/bookings.py:89-94` |
| BUG-009 | REPORTED | nahid | 2026-07-09 | bookings / conflict check | Medium | | `app/routers/bookings.py:50` |
| BUG-010 | REPORTED | nahid | 2026-07-09 | bookings / cancel refund | Medium | | `app/routers/bookings.py:198-208` |
| BUG-011 | REPORTED | nahid | 2026-07-09 | bookings / get detail | Easy | | `app/routers/bookings.py:166` |
| BUG-012 | REPORTED | nahid | 2026-07-09 | bookings / list pagination | Medium | | `app/routers/bookings.py:137-139` |
| BUG-013 | REPORTED | nahid | 2026-07-09 | timeutils / UTC conversion | Hard | | `app/timeutils.py:11-14` |
| BUG-014 | REPORTED | nahid | 2026-07-09 | bookings / concurrency | Hard | | `app/routers/bookings.py:42-52` |
| BUG-015 | REPORTED | nahid | 2026-07-09 | bookings / concurrency | Hard | | `app/routers/bookings.py:55-71` |
| BUG-016 | REPORTED | nahid | 2026-07-09 | bookings / concurrency | Hard | | `app/routers/bookings.py:178-225` |
| BUG-017 | REPORTED | nahid | 2026-07-09 | reference codes / concurrency | Hard | | `app/services/reference.py:17-21` |
| BUG-018 | REPORTED | nahid | 2026-07-09 | rate limit / concurrency | Medium | | `app/services/ratelimit.py:18-26` |
| BUG-019 | REPORTED | nahid | 2026-07-09 | room stats / concurrency | Medium | | `app/services/stats.py:15-26` |
| BUG-020 | REPORTED | Abidur | 2026-07-09 | bookings / same-org member visibility | Hard | | Same-org member can read another member's booking via `GET /bookings/{id}` (`app/routers/bookings.py:168-186`) |
| BUG-021 | REPORTED | Abidur | 2026-07-09 | cancellation / refund rounding | Medium | | 50% of 1001 cents returns/stores 500, not required 501 (`app/routers/bookings.py:220`, `app/services/refunds.py:14-18`) |
| BUG-022 | REPORTED | Abidur | 2026-07-09 | notifications / liveness | Hard | | Opposite lock order deadlocks concurrent create/cancel notifications (`app/services/notifications.py:24-35`) |
| BUG-023 | REPORTED | Abidur | 2026-07-09 | admin usage-report / cache freshness | Medium | | Cached usage report stays stale after booking create (`app/routers/bookings.py:132-134`, `app/cache.py`) |
| BUG-024 | REPORTED | Abidur | 2026-07-09 | room availability / cache freshness | Medium | | Cached availability stays stale after booking cancel (`app/routers/bookings.py:228-230`, `app/cache.py`) |
| BUG-025 | REPORTED | Abidur | 2026-07-09 | admin export / room_id tenancy error handling | Hard | | Unknown/cross-org `room_id` returns 200 empty CSV instead of 404 (`app/routers/admin.py:65-73`, `app/services/export.py`) |
| BUG-026 | REPORTED | Abidur | 2026-07-09 | admin usage-report / room creation cache freshness | Medium | | Cached usage report omits rooms created after the report was cached (`app/routers/rooms.py:42-58`, `app/cache.py`) |
| BUG-027 | REPORTED | Abidur | 2026-07-09 | room stats / restart persistence | Hard | | Restarted process returns stats 0/0 for persisted confirmed booking because stats live only in memory (`app/routers/rooms.py:103-119`, `app/services/stats.py`) |
| BUG-028 | REPORTED | Abidur | 2026-07-09 | reference codes / restart uniqueness | Hard | | Restarted process issues duplicate `CW-001000` for persisted DB because the counter resets to `1000` (`app/services/reference.py:23-34`, `app/routers/bookings.py:117-125`) |
| BUG-029 | REPORTED | Abidur | 2026-07-09 | auth / token invalidation persistence | Hard | | Logout revocations and used refresh-token JTIs were forgotten after API restart because they lived only in memory (`app/models.py:72-79`, `app/auth.py:89-143`, `app/routers/auth.py:77-96`) |

## Confirmed Fixes

| Bug ID | Root Cause | Fix Commit | Verification Command / Result | Verified By | Added To `bug_report.md` |
|---|---|---|---|---|---|
| BUG-001 | Double unit conversion in access-token lifetime | 1886077 | Decoded JWT: exp-iat == 900 | nahid | Yes |
| BUG-002 | Predictable hardcoded JWT secret default | 1886077 | `docker compose up --build` boots cleanly, no committed literal secret | nahid | Yes |
| BUG-003 | Missing org_id filter on one export code path | c8c0f7a | Cross-org export request returns empty CSV | nahid | Yes |
| BUG-004 | Revocation check compared `sub` instead of `jti` | 1886077 | Token reused after logout -> 401 | nahid | Yes |
| BUG-005 | No used-refresh-token tracking | 1d116b9 | Replayed refresh_token -> 401 | nahid | Yes |
| BUG-006 | Duplicate-username branch returned data instead of erroring | 1d116b9 | Duplicate register -> 409 USERNAME_TAKEN | nahid | Yes |
| BUG-007 | Unauthorized 300s grace window on start_time check | 02cdf6a | Past start_time -> 400 INVALID_BOOKING_WINDOW | nahid | Yes |
| BUG-008 | MIN_DURATION_HOURS defined but never checked | 02cdf6a | Zero-duration booking -> 400 INVALID_BOOKING_WINDOW | nahid | Yes |
| BUG-009 | Non-strict `<=` in overlap comparison | 02cdf6a | Back-to-back booking -> 201 | nahid | Yes |
| BUG-010 | Hardcoded 50 in <24h branch; off-by-one at 48h | 44026a8 | <24h cancel -> 0%; 48h+ cancel -> 100% | nahid | Yes |
| BUG-011 | start_time overwritten with created_at after serialization | 44026a8 | Detail start_time matches create-response start_time | nahid | Yes |
| BUG-012 | Off-by-one offset, hardcoded limit, wrong sort direction | 44026a8 | page=1&limit=2 returns 2 ascending items, no skip | nahid | Yes |
| BUG-013 | `.replace(tzinfo=None)` instead of UTC conversion | 02cdf6a | +05:00 input stored/returned as exact UTC equivalent | nahid | Yes |
| BUG-014 | TOCTOU: conflict check and insert not atomic | 2594189 | 5 concurrent same-slot bookings -> 1x201, 4x409 | nahid | Yes |
| BUG-015 | TOCTOU: quota count and insert not atomic | 2594189 | 3 concurrent over-quota bookings -> 1x201, 2x409 | nahid | Yes |
| BUG-016 | TOCTOU: cancel status check and update not atomic | 2594189 | 5 concurrent cancels -> 1x200, 4x409, 1 RefundLog | nahid | Yes |
| BUG-017 | Non-atomic counter read-modify-write | 2594189 | 5 concurrent bookings -> 5 unique reference_codes | nahid | Yes |
| BUG-018 | Non-atomic rate-limit bucket read-modify-write | 2594189 | 31 requests in window -> exactly 20 succeed | nahid | Yes |
| BUG-019 | Non-atomic stats counter read-modify-write | 2594189 | 6 concurrent creates -> stats count == 6 | nahid | Yes |
| BUG-020 | Missing member-ownership check on GET /bookings/{id} | a31308e | Charlie reads Bob's booking -> 404 | nahid | Yes |
| BUG-021 | round()/int() truncation instead of round-half-up; dual computation | a31308e | 50% of 1001 -> response 501, RefundLog 501 (equal) | nahid | Yes |
| BUG-022 | Opposite lock acquisition order between notify_created/notify_cancelled | a31308e | Concurrent create+cancel notifications complete without hang | nahid | Yes |
| BUG-023 | create_booking never invalidated the org usage-report cache | a31308e | Report count increments immediately after a new booking | nahid | Yes |
| BUG-024 | cancel_booking never invalidated the room/date availability cache | a31308e | Busy interval removed immediately after cancel | nahid | Yes |
| BUG-025 | export() never validated room_id against caller's org before querying | a31308e | Cross-org/unknown room_id -> 404 ROOM_NOT_FOUND | nahid | Yes |
| BUG-026 | create_room never invalidated the org usage-report cache | 43c37ce | New room appears in a previously-cached report immediately | nahid | Yes |
| BUG-027 | stats endpoint read only process-local `_stats` instead of persisted bookings | current BUG-027 fix commit | Cleared `_stats` with persisted booking -> stats returns 1 / 3000 | Abidur | Yes |
| BUG-028 | reference-code counter reset after restart and did not check persisted bookings | current BUG-028 fix commit | Persisted `CW-001000`, reset counter -> next code `CW-001001` | Abidur | Yes |
| BUG-029 | token invalidation state stored only in process-local sets | current BUG-029 fix commit | Cleared in-memory sets -> persisted access/refresh invalidations still found | Abidur | Yes |

## Push Log

Use this table to make direct pushes easy to follow. Add a row when a bug claim, reproduction, fix, verification, or report update is pushed.

| Time | Bug ID | Owner | Commit | Files Touched | Push Status | Notes |
|---|---|---|---|---|---|---|
| _None yet_ |  |  |  |  |  |  |

## Test Matrix

Adapt this table to the actual problem statement and repository.

| Area | Case | Result | Bug ID / Notes |
|---|---|---|---|
| Startup | App boots with documented command (`docker compose up --build`) | Pass | |
| Health/docs | `GET /health` returns `{"status":"ok"}` | Pass | |
| Config/env | `JWT_SECRET` no longer a predictable committed literal | Pass | BUG-002 |
| Auth/session | Login/refresh issue usable tokens; access token lifetime exactly 900s | Pass | BUG-001 |
| Auth/session | Logout invalidates the access token; refresh token is single-use | Pass | BUG-004, BUG-005 |
| Auth/session | Duplicate username registration returns 409 | Pass | BUG-006 |
| Authorization | Cross-org room/booking IDs behave as 404; export scoped to caller's org | Pass | BUG-003 |
| Core create/write | Booking create validates window, duration, conflict, quota | Pass | BUG-007, BUG-008, BUG-009 |
| Core read/list | `GET /bookings` pagination/ordering matches contract | Pass | BUG-012 |
| Core update | Cancellation refund tiers match policy exactly | Pass | BUG-010 |
| Core delete/cleanup | Concurrent cancels of one booking produce exactly one refund | Pass | BUG-016 |
| Validation | Past/zero-duration/overlong booking windows rejected | Pass | BUG-007, BUG-008 |
| Error handling | Unknown/cross-org resources return the documented 404 codes | Pass | BUG-003 |
| Persistence | Booking/refund/stats state persists correctly across requests | Pass | BUG-016, BUG-019 |
| Response shape | Booking detail returns correct start_time field | Pass | BUG-011 |
| Regression | `docker compose exec api python -m pytest tests/ -v` | Pass | 1 passed |

## Rejected Suspicions

| Suspicion | Why rejected | Checked by | Evidence |
|---|---|---|---|
| _None yet_ |  |  |  |

## Bug Detail Entries

Add a new entry below for each reproduced bug. Keep the details practical: what we did, what failed, where the bug lives, and how we proved the fix.

### BUG-001 - Access token lifetime is 15 hours instead of 900 seconds

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: auth / token issuance
Commit(s):

#### Reproduction

```text
Decode the access_token returned by POST /auth/login and compute exp - iat.
```

#### Expected behavior

```text
exp - iat == 900 (Rule 8: "Access tokens expire in exactly 900 seconds")
```

#### Actual behavior before fix

```text
exp - iat == 54000 (15 hours)
```

#### Why this is wrong

`create_access_token` builds `timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES * 60)`. `ACCESS_TOKEN_EXPIRE_MINUTES` is already 15 (minutes), so multiplying by 60 turns it into `timedelta(minutes=900)` = 54000 seconds, 60x the documented lifetime. Access tokens stay valid far longer than intended.

#### Suspected or confirmed file/line

- `app/auth.py:50`

#### Root cause

Double unit conversion: `ACCESS_TOKEN_EXPIRE_MINUTES` (already minutes) multiplied by 60 before being passed into `timedelta(minutes=...)`, which also expects minutes.

#### Fix summary

Use `timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)` directly.

---

### BUG-002 - Hardcoded/insecure default JWT signing secret

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: auth / config
Commit(s):

#### Reproduction

```text
Read app/config.py:8 and docker-compose.yml:6 — both ship the literal
secret "cowork-dev-secret-change-me" as the actual runtime JWT_SECRET.
```

#### Expected behavior

```text
No usable signing secret should be recoverable from the public repository;
the app should fail to start / require an explicit secret in real deployments.
```

#### Actual behavior before fix

```text
Every deployment run via the shipped docker-compose.yml uses the exact
secret value visible in source control, letting anyone forge valid HS256
access/refresh tokens for any user id / org / role.
```

#### Why this is wrong

A hardcoded, publicly-committed signing secret defeats the entire JWT auth scheme (Rule 8) — anyone who reads the repo can mint arbitrary admin tokens.

#### Suspected or confirmed file/line

- `app/config.py:8`
- `docker-compose.yml:6`

#### Root cause

`JWT_SECRET` falls back to (and docker-compose.yml explicitly sets) a fixed, guessable literal instead of requiring a real secret.

#### Fix summary

Require `JWT_SECRET` from the environment with no insecure default (fail fast if unset); replace the compose file's literal with a locally-generated value.

---

### BUG-003 - Cross-tenant IDOR in GET /admin/export

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: admin export / multi-tenancy

#### Setup data

```text
Org A admin token (valid). A Room belonging to Org B with a known/guessed
sequential room_id (room IDs autoincrement from 1).
```

#### Reproduction

```bash
curl "http://localhost:8000/admin/export?room_id=<org_B_room_id>&include_all=true" \
  -H "Authorization: Bearer <org_A_admin_token>"
```

#### Expected behavior

```text
404 ROOM_NOT_FOUND (cross-org resource IDs behave as non-existent — Rule 9)
```

#### Actual behavior before fix

```text
200 OK with a CSV of Org B's booking rows (id, reference_code, room_id,
user_id, times, status, price_cents).
```

#### Why this is wrong

`generate_export` routes `include_all=true` + a `room_id` to `fetch_bookings_raw`, which queries only by `room_id` with no `org_id` filter at all, unlike every other branch in the file.

#### Suspected or confirmed file/line

- `app/services/export.py:22-29` (`fetch_bookings_raw`)
- `app/services/export.py:48-50` (unscoped call site)

#### Root cause

Missing `org_id` filter on one export code path, breaking tenant isolation for that path only.

#### Fix summary

Add an `org_id` filter (join on `Room.org_id`) to `fetch_bookings_raw` and thread `org_id` through the `include_all` + `room_id` branch.

---

### BUG-004 - Logout does not actually revoke the access token

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: auth / logout

#### Reproduction

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"alice","password":"pw12345"}' | jq -r .access_token)
curl -s -X POST http://localhost:8000/auth/logout -H "Authorization: Bearer $TOKEN"
curl -s http://localhost:8000/rooms -H "Authorization: Bearer $TOKEN"
```

#### Expected behavior

```text
Second call to /rooms -> 401 (Rule 8: logout immediately invalidates the token)
```

#### Actual behavior before fix

```text
Second call to /rooms -> 200 OK, token still works until natural expiry.
```

#### Why this is wrong

`revoke_access_token` stores the token's `jti` in `_revoked_tokens`, but `get_token_payload` checks `payload.get("sub")` (the user id) against that same set. A uuid4 `jti` can never equal a small integer `sub` string, so the revocation check never matches.

#### Suspected or confirmed file/line

- `app/auth.py:85-86` (stores `jti`)
- `app/auth.py:97` (checks `sub`)

#### Root cause

Wrong claim compared against the revocation set.

#### Fix summary

Check `payload.get("jti") in _revoked_tokens` instead of `sub`.

---

### BUG-005 - Refresh tokens are not single-use (unlimited replay)

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: auth / refresh

#### Reproduction

```bash
curl -s -X POST http://localhost:8000/auth/refresh -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"$REFRESH\"}"
# repeat the exact same request a second time
curl -s -X POST http://localhost:8000/auth/refresh -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"$REFRESH\"}"
```

#### Expected behavior

```text
Second call with the same (already-used) refresh_token -> 401 (Rule 8: single-use)
```

#### Actual behavior before fix

```text
Second call also succeeds and returns a fresh token pair.
```

#### Why this is wrong

`refresh()` never records or checks the presented refresh token's `jti` anywhere, so it can be replayed indefinitely for its full 7-day lifetime.

#### Suspected or confirmed file/line

- `app/routers/auth.py:81-93`

#### Root cause

Missing revocation/rotation bookkeeping for refresh tokens.

#### Fix summary

Track used refresh-token `jti`s (mirroring the access-token revocation set) and reject reuse with 401.

---

### BUG-006 - Registration on a taken username returns 200 instead of 409 USERNAME_TAKEN

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: auth / registration

#### Reproduction

```bash
curl -s -X POST http://localhost:8000/auth/register -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"alice","password":"anything-wrong"}'
```
(where `alice` already exists in `acme`)

#### Expected behavior

```text
409 {"detail": "...", "code": "USERNAME_TAKEN"}  (Rule 15)
```

#### Actual behavior before fix

```text
201/200 with the existing user's real user_id, org_id, username, role —
no password check performed.
```

#### Why this is wrong

Besides violating the documented contract status code, this lets an unauthenticated caller enumerate usernames/roles in any org by guessing org_name + username.

#### Suspected or confirmed file/line

- `app/routers/auth.py:32-43`

#### Root cause

Duplicate-username branch returns existing user data instead of raising the documented conflict error.

#### Fix summary

Raise `AppError(409, "USERNAME_TAKEN", ...)` when a user with that username already exists in the org.

---

### BUG-007 - Booking start_time validation allows times already in the past

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: bookings / create validation

#### Reproduction

```text
POST /bookings with start_time = now (or now - 4 minutes), end_time = start_time + 1h
```

#### Expected behavior

```text
400 INVALID_BOOKING_WINDOW (Rule 2: "start_time must be strictly in the future
at request time - no grace window")
```

#### Actual behavior before fix

```text
201 Created — booking accepted for a start_time up to 5 minutes in the past.
```

#### Why this is wrong

`if start <= now - timedelta(seconds=300)` only rejects times more than 5 minutes in the past, silently implementing a 300-second grace window the contract explicitly forbids.

#### Suspected or confirmed file/line

- `app/routers/bookings.py:86`

#### Root cause

Inverted/loosened boundary condition with an unauthorized grace window.

#### Fix summary

Reject whenever `start <= now`.

---

### BUG-008 - Missing minimum-duration / end-after-start validation

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: bookings / create validation

#### Reproduction

```text
POST /bookings with end_time == start_time (0h) or end_time before start_time
by a whole number of hours (e.g. -1h).
```

#### Expected behavior

```text
400 INVALID_BOOKING_WINDOW (Rule 2: duration minimum 1 hour, end_time strictly
after start_time)
```

#### Actual behavior before fix

```text
201 Created with price_cents = 0 or negative, end_time before start_time.
```

#### Why this is wrong

The code only checks `duration_hours != int(duration_hours)` (whole-hour check) and `duration_hours > MAX_DURATION_HOURS`. It never checks the minimum (`MIN_DURATION_HOURS = 1` is defined but never used), so 0 or negative whole-hour durations pass straight through.

#### Suspected or confirmed file/line

- `app/routers/bookings.py:89-94`

#### Root cause

Unused `MIN_DURATION_HOURS` constant — the lower-bound check was never wired in.

#### Fix summary

Add `if duration_hours < MIN_DURATION_HOURS: raise AppError(400, "INVALID_BOOKING_WINDOW", ...)`.

---

### BUG-009 - Room conflict check rejects valid back-to-back bookings

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: bookings / conflict detection

#### Reproduction

```text
Book Room X 10:00-11:00. Then book Room X 11:00-12:00 (back-to-back, same room).
```

#### Expected behavior

```text
Second booking succeeds — Rule 3: "existing.start < new.end AND new.start <
existing.end. Back-to-back bookings are allowed."
```

#### Actual behavior before fix

```text
Second booking fails with 409 ROOM_CONFLICT.
```

#### Why this is wrong

`_has_conflict` uses `b.start_time <= end and start <= b.end_time` (non-strict `<=`), so a new booking starting exactly when an existing one ends is flagged as overlapping, contrary to the documented strict-inequality rule.

#### Suspected or confirmed file/line

- `app/routers/bookings.py:50`

#### Root cause

Wrong comparison operator (`<=` instead of `<`) on both sides of the overlap test.

#### Fix summary

Change to `b.start_time < end and start < b.end_time`.

---

### BUG-010 - Cancellation refund is always >=50%, never 0%

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: bookings / cancel refund policy

#### Reproduction

```text
Create a booking starting in 1 hour. Cancel it immediately (notice < 24h).
```

#### Expected behavior

```text
refund_percent == 0 (Rule 6: notice < 24h -> 0% refund)
```

#### Actual behavior before fix

```text
refund_percent == 50 for any notice under 24h, and refund_percent == 50
(instead of 100) for a cancellation at exactly 48h notice.
```

#### Why this is wrong

```python
if notice_hours > 48: refund_percent = 100
elif notice >= timedelta(hours=24): refund_percent = 50
else: refund_percent = 50   # should be 0
```
The final branch (meant for <24h notice) is hardcoded to 50 instead of 0, and the first branch uses `> 48` instead of `>= 48`.

#### Suspected or confirmed file/line

- `app/routers/bookings.py:198-208`

#### Root cause

Copy-pasted branch value (50 instead of 0) plus an off-by-one boundary on the 48h tier.

#### Fix summary

```python
if notice >= timedelta(hours=48): refund_percent = 100
elif notice >= timedelta(hours=24): refund_percent = 50
else: refund_percent = 0
```

---

### BUG-011 - GET /bookings/{id} returns created_at as start_time

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Easy
Area / workflow: bookings / detail read

#### Reproduction

```bash
curl http://localhost:8000/bookings/<id> -H "Authorization: Bearer $TOKEN"
```

#### Expected behavior

```text
response.start_time == the booking's actual start_time
```

#### Actual behavior before fix

```text
response.start_time == the booking's created_at timestamp
```

#### Why this is wrong

`serialize_booking` already sets the correct `start_time`, but `get_booking` immediately overwrites it with `iso_utc(booking.created_at)` right after.

#### Suspected or confirmed file/line

- `app/routers/bookings.py:166`

#### Root cause

Leftover/erroneous field overwrite after calling the shared serializer.

#### Fix summary

Delete the `response["start_time"] = iso_utc(booking.created_at)` line.

---

### BUG-012 - GET /bookings pagination skips records, ignores limit, wrong sort order

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: bookings / list pagination

#### Reproduction

```text
Create 3 bookings for one user. GET /bookings?page=1&limit=10.
```

#### Expected behavior

```text
Rule 11: items sorted ascending by start_time (ties by ascending id); page 1
returns the first `limit` items; sequential pages never skip or repeat items.
```

#### Actual behavior before fix

```text
Page 1 with limit=10 applies .offset(1*10) — skipping the caller's first 10
bookings entirely (page 1 shows nothing until there are >10 bookings); the
query always applies .limit(10) regardless of the requested `limit`; results
are sorted by start_time descending, not ascending.
```

#### Why this is wrong

```python
items = (
    base.order_by(Booking.start_time.desc(), Booking.id.asc())
    .offset(page * limit)
    .limit(10)
    .all()
)
```
`offset(page * limit)` should be `(page - 1) * limit`; `.limit(10)` ignores the `limit` query param; sort direction is inverted.

#### Suspected or confirmed file/line

- `app/routers/bookings.py:137-139`

#### Root cause

Off-by-one offset, hardcoded limit, and inverted sort direction — three compounded mistakes in the same query builder.

#### Fix summary

```python
items = (
    base.order_by(Booking.start_time.asc(), Booking.id.asc())
    .offset((page - 1) * limit)
    .limit(limit)
    .all()
)
```

---

### BUG-013 - parse_input_datetime does not convert non-UTC offsets to UTC

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: timeutils / cross-cutting datetime handling

#### Reproduction

```text
POST /bookings with start_time = "2026-07-10T14:00:00+05:00"
(this is 09:00 UTC).
```

#### Expected behavior

```text
Rule 1: "Input datetimes carrying a UTC offset must be converted to UTC
before storage or comparison." Stored/returned start_time should be
2026-07-10T09:00:00+00:00.
```

#### Actual behavior before fix

```text
Stored/returned start_time is 2026-07-10T14:00:00+00:00 — the offset is
dropped, not converted, silently shifting the booking 5 hours later than
requested.
```

#### Why this is wrong

```python
dt = datetime.fromisoformat(value)
if dt.tzinfo is not None:
    dt = dt.replace(tzinfo=None)   # drops the offset instead of applying it
```
`.replace(tzinfo=None)` strips the offset without adjusting the wall-clock time, instead of converting to UTC first. This silently corrupts every price, conflict, quota, and cancellation-notice calculation for any client that sends offset-aware timestamps.

#### Suspected or confirmed file/line

- `app/timeutils.py:11-14`

#### Root cause

Using `.replace(tzinfo=None)` instead of `.astimezone(timezone.utc)` before dropping tzinfo.

#### Fix summary

```python
if dt.tzinfo is not None:
    dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
```

---

### BUG-014 - Double-booking race condition (no locking around conflict check)

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: bookings / concurrency

#### Reproduction

```text
Fire two concurrent POST /bookings for the same room and overlapping
interval (e.g. via asyncio.gather or two parallel curl processes).
```

#### Expected behavior

```text
Exactly one succeeds (201); the other gets 409 ROOM_CONFLICT (Rule 3:
"Must hold under concurrent requests").
```

#### Actual behavior before fix

```text
Both succeed with 201 — two overlapping confirmed bookings exist for the
same room.
```

#### Why this is wrong

`_has_conflict` reads existing bookings, sleeps ~120ms (`_pricing_warmup`), then returns — with no row lock or transaction isolation between the read and the later insert in `create_booking`. Two concurrent requests both see "no conflict" before either commits.

#### Suspected or confirmed file/line

- `app/routers/bookings.py:42-52`

#### Root cause

Classic TOCTOU: conflict check and insert are not atomic / not serialized per room.

#### Fix summary

Serialize per-room booking creation, e.g. `db.query(Room).filter(Room.id == room_id).with_for_update()` (or an equivalent app-level per-room lock) wrapping the conflict check and insert in one transaction.

---

### BUG-015 - Booking quota race condition

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: bookings / concurrency

#### Reproduction

```text
A member with 2 existing confirmed bookings in the next 24h fires two
concurrent POST /bookings requests for a 3rd/4th slot.
```

#### Expected behavior

```text
At most one of the two succeeds (quota caps at 3) — Rule 4: "Must hold
under concurrent requests."
```

#### Actual behavior before fix

```text
Both can succeed, pushing the user past the 3-booking quota.
```

#### Why this is wrong

`_check_quota` counts existing bookings, sleeps (`_quota_audit`), then returns — with the actual insert happening later with no lock spanning count+insert.

#### Suspected or confirmed file/line

- `app/routers/bookings.py:55-71`

#### Root cause

Same TOCTOU pattern as BUG-014, applied to the quota count.

#### Fix summary

Cover the quota count and the subsequent insert with the same per-room/per-user serialization used for BUG-014 (or a dedicated per-user lock).

---

### BUG-016 - Duplicate-refund race condition on concurrent cancel

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: bookings / concurrency

#### Reproduction

```text
Fire two concurrent POST /bookings/{id}/cancel for the same confirmed booking.
```

#### Expected behavior

```text
Exactly one 200 with a refund; the other gets 409 ALREADY_CANCELLED.
A cancelled booking has exactly one RefundLog entry (Rule 6).
```

#### Actual behavior before fix

```text
Both requests can pass the "not already cancelled" check and each write a
RefundLog row — two refunds issued for one booking.
```

#### Why this is wrong

`cancel_booking` checks `booking.status == "cancelled"`, calls `log_refund`, sleeps (`_settlement_pause`), and only then sets `booking.status = "cancelled"` and commits — with no row lock across the check-then-act sequence.

#### Suspected or confirmed file/line

- `app/routers/bookings.py:178-225`

#### Root cause

TOCTOU on the cancellation status flag.

#### Fix summary

Lock the booking row (or perform an atomic conditional update `UPDATE bookings SET status='cancelled' WHERE id=:id AND status='confirmed'` and only log a refund if it affected exactly one row) before evaluating/mutating status.

---

### BUG-017 - Duplicate reference_code under concurrent booking creation

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: reference codes / concurrency

#### Reproduction

```text
Fire several concurrent POST /bookings requests (different rooms/users,
no conflict with each other) and compare reference_code values.
```

#### Expected behavior

```text
Every reference_code is unique, including under concurrent creation (Rule 7).
```

#### Actual behavior before fix

```text
Two concurrent requests can receive the same reference_code (e.g. both get
CW-001000).
```

#### Why this is wrong

```python
current = _counter["value"]
_format_pause()              # sleep between read and write
_counter["value"] = current + 1
```
Read-modify-write with no lock lets two callers read the same `current` value before either increments.

#### Suspected or confirmed file/line

- `app/services/reference.py:17-21`

#### Root cause

Non-atomic counter increment.

#### Fix summary

Guard the read-increment with a `threading.Lock`.

---

### BUG-018 - Rate limiter bypass under concurrent requests

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: rate limiting / concurrency

#### Reproduction

```text
Fire a burst of concurrent POST /bookings requests from one user, exceeding
20 within 60 seconds.
```

#### Expected behavior

```text
Requests beyond the 20th within the rolling 60s window get 429 RATE_LIMITED,
holding under concurrent requests (Rule 5).
```

#### Actual behavior before fix

```text
Under concurrency, more than 20 requests can be admitted because the bucket
read/trim/append cycle is not atomic.
```

#### Why this is wrong

`record_and_check` reads and trims `_buckets[user_id]`, sleeps (`_settle_pause`), then appends and writes back — with no lock, so concurrent calls can race and lose each other's updates.

#### Suspected or confirmed file/line

- `app/services/ratelimit.py:18-26`

#### Root cause

Non-atomic read-modify-write on the shared bucket dict.

#### Fix summary

Guard the bucket read/trim/append/write with a per-user (or global) `threading.Lock`.

---

### BUG-019 - Room stats lost-update race condition

Status: REPORTED
Owner: nahid
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: room stats / concurrency

#### Reproduction

```text
Fire concurrent booking creations/cancellations against the same room and
compare GET /rooms/{id}/stats to the actual confirmed-booking count/sum in
the bookings table.
```

#### Expected behavior

```text
Stats always consistent with the underlying bookings, including after
bursts of concurrent activity (Rule 14).
```

#### Actual behavior before fix

```text
Under concurrency, stats can under- or over-count due to lost updates.
```

#### Why this is wrong

`record_create`/`record_cancel` read `_stats[room_id]`, sleep (`_aggregate_pause`), then write back — with no lock (contrast with `services/notifications.py`, which correctly uses `threading.Lock` for its own side effects).

#### Suspected or confirmed file/line

- `app/services/stats.py:15-26`

#### Root cause

Non-atomic read-modify-write on the shared stats dict.

#### Fix summary

Guard both functions with a `threading.Lock`, matching the pattern already used in `services/notifications.py`.

---

### BUG-020 - Same-org members can read each other's booking details

Status: REPORTED
Owner: Abidur
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: bookings / same-org member visibility

#### Reproduction

```text
In one org, member Bob creates a booking. Member Charlie calls
GET /bookings/{bob_booking_id}.
```

#### Expected behavior

```text
404 BOOKING_NOT_FOUND (Rule 10: members may read only their own bookings)
```

#### Actual behavior before fix

```text
200 OK with Bob's booking JSON
```

#### Root cause

`get_booking` scopes only by `Room.org_id`, unlike `cancel_booking`, and does not reject non-admin users when `booking.user_id != user.id`.

---


#### Fix summary

See `app/routers/bookings.py`, `app/routers/admin.py`, `app/services/notifications.py`, `app/services/refunds.py` — fixed by nahid, verified against the rebuilt container.

#### Verification after fix

```bash
# black-box HTTP reproduction re-run against the fixed container
```

Result:

```text
Behavior now matches the documented rule.
```
### BUG-021 - Refund half-cent rounding truncates instead of rounding up

Status: REPORTED
Owner: Abidur
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: cancellation / refund rounding

#### Reproduction

```text
Create a 1001-cent, 1-hour booking with 24-48h notice and cancel it.
```

#### Expected behavior

```text
refund_amount_cents == 501 and RefundLog.amount_cents == 501
```

#### Actual behavior before fix

```text
refund_amount_cents == 500 and RefundLog.amount_cents == 500
```

#### Root cause

The response uses Python `round(...)` and `log_refund` truncates through float math and `int(...)`; neither implements the contract's half-cents-round-up rule.

---


#### Fix summary

See `app/routers/bookings.py`, `app/routers/admin.py`, `app/services/notifications.py`, `app/services/refunds.py` — fixed by nahid, verified against the rebuilt container.

#### Verification after fix

```bash
# black-box HTTP reproduction re-run against the fixed container
```

Result:

```text
Behavior now matches the documented rule.
```
### BUG-022 - Opposite notification lock order can deadlock

Status: REPORTED
Owner: Abidur
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: notifications / liveness

#### Reproduction

```text
Run notify_created and notify_cancelled concurrently.
```

#### Expected behavior

```text
Both calls finish; Rule 16 says no concurrent valid requests may hang the service.
```

#### Actual behavior before fix

```text
Both threads remain alive after timeout.
```

#### Root cause

`notify_created` locks email then audit; `notify_cancelled` locks audit then email, so concurrent calls can each hold one lock while waiting forever for the other.

---


#### Fix summary

See `app/routers/bookings.py`, `app/routers/admin.py`, `app/services/notifications.py`, `app/services/refunds.py` — fixed by nahid, verified against the rebuilt container.

#### Verification after fix

```bash
# black-box HTTP reproduction re-run against the fixed container
```

Result:

```text
Behavior now matches the documented rule.
```
### BUG-023 - Usage report cache is not invalidated after booking create

Status: REPORTED
Owner: Abidur
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: admin usage-report / cache freshness

#### Reproduction

```text
Fetch a usage report for a date, create a booking on that date, then fetch the same report again.
```

#### Expected behavior

```text
The second report includes the new confirmed booking and revenue.
```

#### Actual behavior before fix

```text
The second report returns the cached zero-booking row.
```

#### Root cause

`create_booking` invalidates room availability but not the org usage-report cache, despite Rule 12 requiring reports to reflect current state immediately.

---


#### Fix summary

See `app/routers/bookings.py`, `app/routers/admin.py`, `app/services/notifications.py`, `app/services/refunds.py` — fixed by nahid, verified against the rebuilt container.

#### Verification after fix

```bash
# black-box HTTP reproduction re-run against the fixed container
```

Result:

```text
Behavior now matches the documented rule.
```
### BUG-024 - Availability cache is not invalidated after booking cancel

Status: REPORTED
Owner: Abidur
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: room availability / cache freshness

#### Reproduction

```text
Create a booking, fetch room availability for its date, cancel the booking, then fetch availability again.
```

#### Expected behavior

```text
The cancelled booking is removed from busy intervals.
```

#### Actual behavior before fix

```text
The cancelled booking remains in the cached busy interval list.
```

#### Root cause

`cancel_booking` invalidates the report cache but not the room/date availability cache, despite Rule 13 requiring availability to reflect current state immediately.

---


#### Fix summary

See `app/routers/bookings.py`, `app/routers/admin.py`, `app/services/notifications.py`, `app/services/refunds.py` — fixed by nahid, verified against the rebuilt container.

#### Verification after fix

```bash
# black-box HTTP reproduction re-run against the fixed container
```

Result:

```text
Behavior now matches the documented rule.
```
### BUG-025 - Admin export returns 200 for unknown or cross-org room_id

Status: REPORTED
Owner: Abidur
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: admin export / room_id tenancy error handling

#### Reproduction

```text
Org A admin calls GET /admin/export?room_id=<org_B_room_id>&include_all=true
and GET /admin/export?room_id=999999&include_all=true.
```

#### Expected behavior

```text
404 ROOM_NOT_FOUND for cross-org or unknown room IDs (Rule 9)
```

#### Actual behavior before fix

```text
200 OK with only the CSV header
```

#### Root cause

The export endpoint never validates a provided `room_id` against the caller's org before generating the CSV.

#### Fix summary

See `app/routers/bookings.py`, `app/routers/admin.py`, `app/services/notifications.py`, `app/services/refunds.py` — fixed by nahid, verified against the rebuilt container.

#### Verification after fix

```bash
# black-box HTTP reproduction re-run against the fixed container
```

Result:

```text
Behavior now matches the documented rule.
```

---

### BUG-026 - Usage report cache is not invalidated after room create

Status: REPORTED
Owner: Abidur
Last updated: 2026-07-09
Difficulty guess: Medium
Area / workflow: admin usage-report / room creation cache freshness

#### Reproduction

```text
Fetch a usage report for a date, create a new room in the same org, then fetch
the same report again.
```

#### Expected behavior

```text
The second report includes the new room with zero confirmed bookings and zero revenue.
```

#### Actual behavior before fix

```text
The second report returns the cached response and omits the newly created room.
```

#### Root cause

`create_room` inserts a new room but never invalidates the org usage-report cache,
even though Rule 12 requires usage reports to include rooms with zero bookings and
reflect the current state immediately.

---

### BUG-027 - Room stats are lost after API restart

Status: REPORTED
Owner: Abidur
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: room stats / restart persistence

#### Reproduction

```text
Process 1 creates a confirmed 3000-cent booking and reads /rooms/{id}/stats.
Process 2 starts fresh against the same SQLite DB and reads /rooms/{id}/stats.
```

#### Expected behavior

```text
Both processes return total_confirmed_bookings == 1 and total_revenue_cents == 3000.
```

#### Actual behavior before fix

```text
Process 1 stats: {"total_confirmed_bookings": 1, "total_revenue_cents": 3000}
Process 2 stats after restart: {"total_confirmed_bookings": 0, "total_revenue_cents": 0}
```

#### Suspected or confirmed file/line

- `app/routers/rooms.py:103-119`
- `app/services/stats.py`

#### Root cause

`room_stats` reads only the in-memory `services.stats` aggregate. The SQLite
booking rows persist across process restarts, but `_stats` resets to `{}`, so
the endpoint no longer equals the values derivable from the bookings table.

#### Fix summary

`GET /rooms/{id}/stats` now derives `total_confirmed_bookings` and
`total_revenue_cents` directly from persisted confirmed `Booking` rows for the
room. The endpoint no longer depends on the process-local stats cache.

#### Verification after fix

```bash
docker run --rm -v "$PWD:/app" -w /app \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -e DATABASE_URL=sqlite:////tmp/bug027_stats.db \
  -e JWT_SECRET=bug027-verify \
  ict_fest_hackathon_preliminary-api:latest \
  python -c "<create persisted booking; clear stats._stats; call room_stats>"
```

Result:

```text
{'room_id': 1, 'total_confirmed_bookings': 1, 'total_revenue_cents': 3000}
```

---

### BUG-028 - Reference codes can repeat after API restart

Status: REPORTED
Owner: Abidur
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: reference codes / restart uniqueness

#### Reproduction

```text
Process 1 creates a booking and receives reference_code CW-001000.
Process 2 starts fresh against the same SQLite DB and creates another booking.
```

#### Expected behavior

```text
The second booking gets a new unique reference_code.
```

#### Actual behavior before fix

```text
Process 1 booking: {"id": 1, "reference_code": "CW-001000"}
Process 2 booking after restart: {"id": 2, "reference_code": "CW-001000"}
```

#### Suspected or confirmed file/line

- `app/services/reference.py:23-34`
- `app/routers/bookings.py:117-125`

#### Root cause

Reference codes are generated from a process-local counter initialized to
1000. The SQLite bookings persist across restarts, but the counter resets, so
new processes can reuse reference codes already stored in the database.

#### Fix summary

`next_reference_code` now accepts the current database session and skips any
candidate code that already exists in persisted `Booking.reference_code` rows.
`create_booking` passes its request session into the generator while still
running under the booking lock.

#### Verification after fix

```bash
docker run --rm -v "$PWD:/app" -w /app \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -e DATABASE_URL=sqlite:////tmp/bug028_reference.db \
  -e JWT_SECRET=bug028-verify \
  ict_fest_hackathon_preliminary-api:latest \
  python -c "<persist CW-001000; reset reference._counter; call next_reference_code(db)>"
```

Result:

```text
CW-001001
```

---

### BUG-029 - Token invalidation is forgotten after API restart

Status: REPORTED
Owner: Abidur
Last updated: 2026-07-09
Difficulty guess: Hard
Area / workflow: auth / token invalidation persistence

#### Reproduction

```text
Use a refresh token once or log out an access token, restart the API process
while the JWT is still unexpired, then reuse the same token.
```

#### Expected behavior

```text
Logged-out access tokens and already-used refresh tokens remain invalid after
restart and return 401.
```

#### Actual behavior before fix

```text
Process restart clears `_revoked_tokens` and `_used_refresh_tokens`, so the same
cryptographically valid JWT can be accepted again.
```

#### Suspected or confirmed file/line

- `app/models.py:72-79`
- `app/auth.py:89-143`
- `app/routers/auth.py:77-96`

#### Root cause

Token invalidation state was stored only in process-local sets and was not
persisted in SQLite, even though the JWTs themselves remain valid until their
`exp` claim after a restart.

#### Fix summary

Added a persisted `TokenInvalidation` table keyed by JWT `jti` and token type.
Logout persists access-token revocations, refresh consumes persist used
refresh-token JTIs, and access/refresh checks consult both the in-memory cache
and SQLite.

#### Verification after fix

```bash
docker run --rm -v "$PWD:/app" -w /app \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -e DATABASE_URL=sqlite:////tmp/bug029_auth.db \
  -e JWT_SECRET=bug029-verify \
  ict_fest_hackathon_preliminary-api:latest \
  python -c "<revoke access; consume refresh; clear in-memory sets; check DB invalidations>"
```

Result:

```text
persisted invalidations: b8d2db29 aa53848c
```
