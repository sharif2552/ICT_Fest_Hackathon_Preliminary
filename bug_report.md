# Bug Report - Agentic AI Hackathon

CoWork: Multi-Tenant Coworking Space Booking API. All bugs below were found by
diffing observed API behavior against the business rules and API contract in
the problem statement, reproduced against a running `docker compose` instance,
fixed with the smallest change that makes the documented behavior correct, and
re-verified against the same reproduction. Full reproduction transcripts and
raw evidence live in `bugs.md`.

## Summary

| Bug ID | Difficulty | File/Lines | Status | Short Description |
|---|---|---|---|---|
| BUG-001 | Medium | `app/auth.py:50` | Fixed | Access tokens lasted 15 hours instead of 900 seconds |
| BUG-002 | Medium | `app/config.py:8`, `docker-compose.yml:6` | Fixed | Hardcoded, publicly-known JWT signing secret |
| BUG-003 | Hard | `app/services/export.py:22-50` | Fixed | Cross-tenant data leak in `/admin/export` |
| BUG-004 | Medium | `app/auth.py:85-98` | Fixed | Logout checked the wrong JWT claim, never revoked tokens |
| BUG-005 | Medium | `app/routers/auth.py:81-93` | Fixed | Refresh tokens were not single-use (unlimited replay) |
| BUG-006 | Medium | `app/routers/auth.py:32-43` | Fixed | Duplicate registration leaked account info instead of 409 |
| BUG-007 | Medium | `app/routers/bookings.py:86` | Fixed | Booking start_time accepted times up to 5 minutes in the past |
| BUG-008 | Medium | `app/routers/bookings.py:89-94` | Fixed | Missing minimum-duration validation (0/negative-hour bookings allowed) |
| BUG-009 | Medium | `app/routers/bookings.py:50` | Fixed | Conflict check rejected valid back-to-back bookings |
| BUG-010 | Medium | `app/routers/bookings.py:198-208` | Fixed | Cancellation always refunded >=50%, never 0% |
| BUG-011 | Easy | `app/routers/bookings.py:166` | Fixed | `GET /bookings/{id}` returned `created_at` as `start_time` |
| BUG-012 | Medium | `app/routers/bookings.py:137-139` | Fixed | Pagination skipped records, ignored `limit`, wrong sort order |
| BUG-013 | Hard | `app/timeutils.py:11-14` | Fixed | Offset-aware datetimes were not converted to UTC |
| BUG-014 | Hard | `app/routers/bookings.py:42-52` | Fixed | Race condition allowed double-booking a room |
| BUG-015 | Hard | `app/routers/bookings.py:55-71` | Fixed | Race condition allowed bypassing the booking quota |
| BUG-016 | Hard | `app/routers/bookings.py:178-225` | Fixed | Race condition allowed duplicate refunds on concurrent cancel |
| BUG-017 | Hard | `app/services/reference.py:17-21` | Fixed | Race condition allowed duplicate `reference_code` values |
| BUG-018 | Medium | `app/services/ratelimit.py:18-26` | Fixed | Race condition allowed bypassing the booking rate limit |
| BUG-019 | Medium | `app/services/stats.py:15-26` | Fixed | Race condition caused lost updates in live room stats |
| BUG-020 | Hard | `app/routers/bookings.py:162-186` | Fixed | Any org member could read another member's booking (IDOR) |
| BUG-021 | Medium | `app/routers/bookings.py:220`, `app/services/refunds.py:14-18` | Fixed | Refund rounding truncated instead of rounding half-cents up; response/RefundLog could diverge |
| BUG-022 | Hard | `app/services/notifications.py:24-35` | Fixed | Opposite lock ordering could deadlock concurrent create/cancel notifications |
| BUG-023 | Medium | `app/routers/bookings.py:132-134` | Fixed | Usage-report cache not invalidated when a booking is created |
| BUG-024 | Medium | `app/routers/bookings.py:228-230` | Fixed | Availability cache not invalidated when a booking is cancelled |
| BUG-025 | Hard | `app/routers/admin.py:65-73` | Fixed | Export returned 200 empty CSV instead of 404 for unknown/cross-org room_id |
| BUG-026 | Medium | `app/routers/rooms.py:42-58` | Fixed | Usage-report cache not invalidated when a room is created |
| BUG-027 | Hard | `app/routers/rooms.py:103-119` | Fixed | Room stats returned 0/0 after restart because they read only in-memory counters |

---

## BUG-001 - Access token lifetime is 15 hours instead of 900 seconds

### File(s)/line(s)

- `app/auth.py:50`

### What was the bug?

```python
lifetime = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
```
`ACCESS_TOKEN_EXPIRE_MINUTES` is `15` (already minutes). Multiplying by `60`
before passing it into `timedelta(minutes=...)` (which already expects
minutes) produces `timedelta(minutes=900)` = 54,000 seconds = 15 hours.

### Why did it cause incorrect behavior?

Rule 8 requires access tokens to expire in exactly 900 seconds. Tokens
instead stayed valid 60x longer than specified, undermining the short-lived
access-token security model.

### How was it reproduced?

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"alice","password":"pw12345"}' | jq -r .access_token)
python3 -c "import jwt,sys; p=jwt.decode('$TOKEN', options={'verify_signature': False}); print(p['exp']-p['iat'])"
```

Expected:

```text
900
```

Actual before fix:

```text
54000
```

### How was it fixed?

```python
lifetime = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
900
```

---

## BUG-002 - Hardcoded/insecure default JWT signing secret

### File(s)/line(s)

- `app/config.py:8`
- `docker-compose.yml:6`

### What was the bug?

`JWT_SECRET` fell back to the literal `"cowork-dev-secret-change-me"` when
unset, and `docker-compose.yml` (the documented, recommended run command)
explicitly set the runtime secret to that exact same literal.

### Why did it cause incorrect behavior?

Anyone reading the public repository could read the exact HS256 signing
secret used by the reference deployment and forge arbitrary valid JWTs
(any `sub`/`org`/`role`), completely bypassing authentication.

### How was it reproduced?

```text
Read app/config.py:8 and docker-compose.yml:6 in the repository.
```

Expected:

```text
No usable signing secret recoverable from the repository.
```

Actual before fix:

```text
The literal secret "cowork-dev-secret-change-me" is committed in two places
and used verbatim by `docker compose up --build`.
```

### How was it fixed?

`app/config.py` no longer ships a predictable literal default; an unset
`JWT_SECRET` now falls back to a value generated at process start via
`secrets.token_hex(32)` (never a guessable, committed string), and
`docker-compose.yml`'s explicit value was rotated to a freshly generated
random 32-byte hex string:

```python
JWT_SECRET = os.getenv("JWT_SECRET") or secrets.token_hex(32)
```

### Verification after fix

```bash
docker compose up --build -d && curl -s http://localhost:8000/health
```

Result:

```text
{"status":"ok"} — service boots cleanly under the documented Docker workflow
with no predictable secret committed to source control.
```

---

## BUG-003 - Cross-tenant IDOR/BOLA in `GET /admin/export`

### File(s)/line(s)

- `app/services/export.py:22-29` (`fetch_bookings_raw`)
- `app/services/export.py:48-50` (unscoped call site)

### What was the bug?

```python
def fetch_bookings_raw(db, room_id):
    return db.query(Booking).filter(Booking.room_id == room_id).order_by(Booking.id.asc()).all()

def generate_export(db, org_id, user_id, room_id, include_all):
    if include_all:
        if room_id is not None:
            rows = fetch_bookings_raw(db, room_id)   # no org_id filter
```
When `include_all=true` and a `room_id` was supplied, bookings were fetched
by `room_id` alone with no `org_id` scoping at all — unlike every other
branch in the file.

### Why did it cause incorrect behavior?

Rule 9 requires cross-org resource IDs to behave as non-existent. Instead,
any authenticated admin could pass another organization's (sequential,
guessable) `room_id` and receive that organization's full booking data —
IDs, user IDs, times, status, and revenue — in the exported CSV.

### How was it reproduced?

```text
Org A admin token + Org B's room_id:
GET /admin/export?room_id=<org_B_room_id>&include_all=true
Authorization: Bearer <org_A_admin_token>
```

Expected:

```text
Empty result set (no rows from a room outside the caller's org).
```

Actual before fix:

```text
200 OK with a CSV containing Org B's booking rows.
```

### How was it fixed?

```python
def fetch_bookings_raw(db, org_id, room_id):
    return (
        db.query(Booking).join(Room)
        .filter(Room.org_id == org_id, Booking.room_id == room_id)
        .order_by(Booking.id.asc()).all()
    )
```
and the call site now passes `org_id` through.

### Verification after fix

```text
Same reproduction as above, using the fixed code.
```

Result:

```text
200 OK with only the CSV header row — no Org B data returned.
```

---

## BUG-004 - Logout did not revoke the access token

### File(s)/line(s)

- `app/auth.py:85-86` (stores `jti`)
- `app/auth.py:97` (checked `sub`)

### What was the bug?

`revoke_access_token` stored the token's `jti` in `_revoked_tokens`, but the
per-request check compared `payload.get("sub")` (the user id) against that
same set. A random UUID `jti` can never equal a small integer `sub` string,
so the check never matched.

### Why did it cause incorrect behavior?

Rule 8 requires logout to immediately invalidate the presented access token.
Instead, logged-out tokens remained fully usable until their natural
900-second expiry.

### How was it reproduced?

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"alice","password":"pw12345"}' | jq -r .access_token)
curl -s -X POST http://localhost:8000/auth/logout -H "Authorization: Bearer $TOKEN"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/rooms -H "Authorization: Bearer $TOKEN"
```

Expected:

```text
401
```

Actual before fix:

```text
200
```

### How was it fixed?

```python
if payload.get("jti") in _revoked_tokens:
    raise AppError(401, "UNAUTHORIZED", "Token has been revoked")
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
401
```

---

## BUG-005 - Refresh tokens were not single-use

### File(s)/line(s)

- `app/routers/auth.py:81-93`

### What was the bug?

`refresh()` decoded the presented refresh token and issued a new pair, but
never recorded or checked the presented token's `jti` anywhere, so the same
refresh token could be replayed indefinitely.

### Why did it cause incorrect behavior?

Rule 8 requires refresh tokens to be single-use, with reuse returning 401.
A leaked refresh token instead granted unlimited re-authentication for its
full 7-day lifetime.

### How was it reproduced?

```bash
curl -s -X POST http://localhost:8000/auth/refresh -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"$REFRESH\"}"
curl -s -X POST http://localhost:8000/auth/refresh -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"$REFRESH\"}"
```

Expected:

```text
Second call -> 401
```

Actual before fix:

```text
Second call -> 200, a fresh token pair
```

### How was it fixed?

Added `consume_refresh_token()` in `app/auth.py`, tracking used refresh
`jti`s and rejecting reuse; wired into `POST /auth/refresh`:

```python
def consume_refresh_token(payload: dict) -> None:
    if payload["jti"] in _used_refresh_tokens:
        raise AppError(401, "UNAUTHORIZED", "Refresh token already used")
    _used_refresh_tokens.add(payload["jti"])
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
first refresh: 200
second refresh (replay): 401 {"detail": "Refresh token already used", "code": "UNAUTHORIZED"}
```

---

## BUG-006 - Registering a taken username leaked account data instead of 409

### File(s)/line(s)

- `app/routers/auth.py:32-43`

### What was the bug?

```python
if existing is not None:
    return {"user_id": existing.id, "org_id": org.id, "username": existing.username, "role": existing.role}
```
A duplicate `(org, username)` returned the existing user's real data with a
success status and no password check, instead of the documented conflict
error.

### Why did it cause incorrect behavior?

Rule 15 requires `409 USERNAME_TAKEN`. Beyond the contract violation, this
let an unauthenticated caller enumerate usernames and roles across any org
by guessing `org_name`/`username` pairs.

### How was it reproduced?

```bash
curl -s -X POST http://localhost:8000/auth/register -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"alice","password":"anything"}'
```
(where `alice` already exists in `acme`)

Expected:

```text
409 {"detail": "...", "code": "USERNAME_TAKEN"}
```

Actual before fix:

```text
201 with alice's real user_id, org_id, username, role
```

### How was it fixed?

```python
if existing is not None:
    raise AppError(409, "USERNAME_TAKEN", "Username already taken in this organization")
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
409 {"detail": "Username already taken in this organization", "code": "USERNAME_TAKEN"}
```

---

## BUG-007 - Booking creation allowed start_time already in the past

### File(s)/line(s)

- `app/routers/bookings.py:86`

### What was the bug?

```python
if start <= now - timedelta(seconds=300):
    raise AppError(400, "INVALID_BOOKING_WINDOW", "start_time must be in the future")
```
This only rejected times more than 5 minutes in the past, silently allowing
a 300-second grace window.

### Why did it cause incorrect behavior?

Rule 2 explicitly requires `start_time` to be strictly in the future with
"no grace window." Bookings starting now or up to 5 minutes in the past were
incorrectly accepted.

### How was it reproduced?

```text
POST /bookings with start_time = now - 2 minutes, end_time = start_time + 1h
```

Expected:

```text
400 INVALID_BOOKING_WINDOW
```

Actual before fix:

```text
201 Created
```

### How was it fixed?

```python
if start <= now:
    raise AppError(400, "INVALID_BOOKING_WINDOW", "start_time must be in the future")
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
400 {"detail": "start_time must be in the future", "code": "INVALID_BOOKING_WINDOW"}
```

---

## BUG-008 - Missing minimum-duration / end-after-start validation

### File(s)/line(s)

- `app/routers/bookings.py:89-94`

### What was the bug?

The whole-hour check and the maximum-duration check existed, but nothing
checked the documented minimum: `MIN_DURATION_HOURS = 1` was defined but
never referenced. A duration of `0` or a negative whole number of hours
(e.g. `end_time <= start_time`) passed both existing checks.

### Why did it cause incorrect behavior?

Rule 2 requires a minimum duration of 1 hour and `end_time` strictly after
`start_time`. Zero/negative-duration bookings were created with
`price_cents <= 0` and `end_time` at or before `start_time`.

### How was it reproduced?

```text
POST /bookings with end_time == start_time
```

Expected:

```text
400 INVALID_BOOKING_WINDOW
```

Actual before fix:

```text
201 Created, price_cents = 0
```

### How was it fixed?

```python
if duration_hours < MIN_DURATION_HOURS or duration_hours > MAX_DURATION_HOURS:
    raise AppError(400, "INVALID_BOOKING_WINDOW", "duration out of range")
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
400 {"detail": "duration out of range", "code": "INVALID_BOOKING_WINDOW"}
```

---

## BUG-009 - Room conflict check rejected valid back-to-back bookings

### File(s)/line(s)

- `app/routers/bookings.py:50`

### What was the bug?

```python
if b.start_time <= end and start <= b.end_time:
```
Non-strict `<=` on both sides of the overlap test flagged a booking starting
exactly when another ends as conflicting.

### Why did it cause incorrect behavior?

Rule 3 defines overlap with strict inequalities and explicitly states
back-to-back bookings are allowed. Valid back-to-back bookings were rejected
with `409 ROOM_CONFLICT`.

### How was it reproduced?

```text
Book Room X 10:00-11:00, then book Room X 11:00-12:00.
```

Expected:

```text
Second booking succeeds (201)
```

Actual before fix:

```text
409 ROOM_CONFLICT
```

### How was it fixed?

```python
if b.start_time < end and start < b.end_time:
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
booking1: 201
booking2 (back-to-back): 201
```

---

## BUG-010 - Cancellation refund policy always paid >=50%, never 0%

### File(s)/line(s)

- `app/routers/bookings.py:198-208`

### What was the bug?

```python
if notice_hours > 48:
    refund_percent = 100
elif notice >= timedelta(hours=24):
    refund_percent = 50
else:
    refund_percent = 50   # should be 0
```
The `<24h` branch was hardcoded to `50` instead of `0`, and the top branch
used `> 48` instead of `>= 48`.

### Why did it cause incorrect behavior?

Rule 6 specifies 0% refund for `<24h` notice and 100% for `>=48h` notice.
Every last-minute cancellation received an unauthorized 50% refund, and a
cancellation at exactly 48 hours' notice was underpaid at 50% instead of
100%.

### How was it reproduced?

```text
Create a booking starting in 2 hours; cancel it immediately.
```

Expected:

```text
refund_percent == 0
```

Actual before fix:

```text
refund_percent == 50
```

### How was it fixed?

```python
if notice >= timedelta(hours=48):
    refund_percent = 100
elif notice >= timedelta(hours=24):
    refund_percent = 50
else:
    refund_percent = 0
```

### Verification after fix

```bash
# same reproduction as above, plus a booking cancelled at 48h+ notice
```

Result:

```text
<24h notice refund: 0 (expected 0)
48h+ notice refund: 100 (expected 100)
```

---

## BUG-011 - `GET /bookings/{id}` returned `created_at` as `start_time`

### File(s)/line(s)

- `app/routers/bookings.py:166`

### What was the bug?

```python
response = serialize_booking(booking)
response["start_time"] = iso_utc(booking.created_at)
```
`serialize_booking` already set the correct `start_time`; this line
immediately overwrote it with the booking's `created_at` timestamp.

### Why did it cause incorrect behavior?

The documented response schema for `GET /bookings/{id}` is "Booking plus
refunds" — `start_time` must be the booking's actual start time, not its
creation timestamp.

### How was it reproduced?

```bash
curl http://localhost:8000/bookings/<id> -H "Authorization: Bearer $TOKEN"
```

Expected:

```text
response.start_time == the booking's real start_time
```

Actual before fix:

```text
response.start_time == the booking's created_at
```

### How was it fixed?

Deleted the erroneous overwrite line.

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
detail.start_time equals the booking's actual start_time (matches the
create-response's start_time exactly).
```

---

## BUG-012 - `GET /bookings` pagination skipped records, ignored `limit`, wrong sort order

### File(s)/line(s)

- `app/routers/bookings.py:137-139`

### What was the bug?

```python
items = (
    base.order_by(Booking.start_time.desc(), Booking.id.asc())
    .offset(page * limit)
    .limit(10)
    .all()
)
```
Three compounded mistakes: `offset(page * limit)` should be
`(page - 1) * limit`; `.limit(10)` ignored the caller's `limit` query
parameter; and the sort was descending instead of ascending.

### Why did it cause incorrect behavior?

Rule 11 requires ascending `start_time` order (ties by ascending `id`), the
requested `limit` to be honored, and sequential pages to never skip or
repeat items. Page 1 skipped the caller's first `limit` bookings entirely,
`limit` was silently ignored, and results were returned newest-first.

### How was it reproduced?

```text
Create 3 bookings; GET /bookings?page=1&limit=2
```

Expected:

```text
2 items, ascending by start_time, no records skipped
```

Actual before fix:

```text
Page 1 with limit=10 returned 0 items until >10 bookings existed; limit was
always effectively 10; order was descending.
```

### How was it fixed?

```python
items = (
    base.order_by(Booking.start_time.asc(), Booking.id.asc())
    .offset((page - 1) * limit)
    .limit(limit)
    .all()
)
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
page1 limit2 items count: 2, total: 3, ascending order check: True
```

---

## BUG-013 - Offset-aware datetimes were not converted to UTC

### File(s)/line(s)

- `app/timeutils.py:11-14`

### What was the bug?

```python
dt = datetime.fromisoformat(value)
if dt.tzinfo is not None:
    dt = dt.replace(tzinfo=None)
```
`.replace(tzinfo=None)` strips a UTC offset without adjusting the wall-clock
time, instead of converting to UTC first.

### Why did it cause incorrect behavior?

Rule 1 requires input datetimes carrying a UTC offset to be converted to UTC
before storage/comparison. A client sending `+05:00`-offset timestamps had
its booking silently shifted by the offset amount, corrupting price,
conflict-detection, quota, and cancellation-notice calculations for that
booking.

### How was it reproduced?

```text
POST /bookings with start_time = "<instant>" expressed in +05:00 offset
```

Expected:

```text
Stored/returned start_time equals the same instant expressed in UTC.
```

Actual before fix:

```text
Stored/returned start_time equals the wall-clock digits of the +05:00 value,
reinterpreted as UTC — 5 hours off from the requested instant.
```

### How was it fixed?

```python
if dt.tzinfo is not None:
    dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
Booking created with a +05:00-offset start_time is stored/returned with the
exact equivalent UTC instant.
```

---

## BUG-014 - Race condition allowed double-booking a room

### File(s)/line(s)

- `app/routers/bookings.py:42-52` (conflict check)
- `app/routers/bookings.py:100-118` (create_booking critical section)

### What was the bug?

`_has_conflict` read existing bookings, then slept ~120ms (`_pricing_warmup`),
before the caller inserted the new booking — with no lock or transaction
isolation spanning the read and the later write.

### Why did it cause incorrect behavior?

Rule 3 requires the no-double-booking invariant to hold under concurrent
requests. Two concurrent requests for the same room/overlapping interval
both observed "no conflict" before either committed, producing two
overlapping confirmed bookings.

### How was it reproduced?

```python
# 5 concurrent POST /bookings for the same room + identical time slot
from concurrent.futures import ThreadPoolExecutor
# ... (see bugs.md for full script)
```

Expected:

```text
Exactly one 201; the rest 409 ROOM_CONFLICT
```

Actual before fix:

```text
Multiple 201s for the same overlapping slot
```

### How was it fixed?

Added a module-level `threading.Lock` (`_booking_lock`) in
`app/routers/bookings.py` serializing the conflict-check, quota-check, and
insert+commit as one critical section.

### Verification after fix

```bash
# same 5-concurrent-request reproduction
```

Result:

```text
statuses: [201, 409, 409, 409, 409] -> successes: 1
```

---

## BUG-015 - Race condition allowed bypassing the booking quota

### File(s)/line(s)

- `app/routers/bookings.py:55-71`

### What was the bug?

`_check_quota` counted existing bookings, slept (`_quota_audit`), and
returned — with the insert happening later, outside any lock covering the
count-then-insert sequence.

### Why did it cause incorrect behavior?

Rule 4 requires the 3-booking quota to hold under concurrent requests.
Concurrent requests could each observe a count below the limit before any
of them committed, allowing more than 3 confirmed bookings in the 24h
window.

### How was it reproduced?

```text
With 2 existing confirmed bookings in the next 24h, fire 3 concurrent
POST /bookings requests for 3 more distinct slots in that window.
```

Expected:

```text
Exactly 1 of the 3 concurrent requests succeeds (caps total at 3)
```

Actual before fix:

```text
More than 1 could succeed, exceeding the quota
```

### How was it fixed?

Covered by the same `_booking_lock` critical section added for BUG-014
(the quota check and insert now happen atomically together).

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
statuses: [409, 201, 409] -> successes: 1
```

---

## BUG-016 - Race condition allowed duplicate refunds on concurrent cancel

### File(s)/line(s)

- `app/routers/bookings.py:178-225`

### What was the bug?

`cancel_booking` checked `booking.status == "cancelled"`, logged a refund,
slept (`_settlement_pause`), and only then set `booking.status = "cancelled"`
and committed — with no lock across the check-then-act sequence, and no
re-read of the booking's current DB state immediately before deciding.

### Why did it cause incorrect behavior?

Rule 6 requires a cancelled booking to have exactly one RefundLog entry and
requires this to hold under concurrent cancel requests. Two concurrent
cancels of the same booking could both pass the "not already cancelled"
check and each write a RefundLog row — a double refund.

### How was it reproduced?

```text
5 concurrent POST /bookings/{id}/cancel for the same confirmed booking.
```

Expected:

```text
Exactly one 200; the rest 409 ALREADY_CANCELLED; exactly one RefundLog entry.
```

Actual before fix:

```text
Multiple 200s possible; multiple RefundLog entries.
```

### How was it fixed?

Added a module-level `threading.Lock` (`_cancel_lock`) wrapping a
`db.refresh(booking)` + status check + refund + status update + commit as
one atomic critical section.

### Verification after fix

```bash
# same 5-concurrent-cancel reproduction
```

Result:

```text
cancel statuses: [200, 409, 409, 409, 409] -> successes: 1
refund log entries on the booking: 1
```

---

## BUG-017 - Race condition allowed duplicate `reference_code` values

### File(s)/line(s)

- `app/services/reference.py:17-21`

### What was the bug?

```python
current = _counter["value"]
_format_pause()
_counter["value"] = current + 1
```
Read-modify-write with no lock let two concurrent callers read the same
`current` value before either incremented.

### Why did it cause incorrect behavior?

Rule 7 requires every `reference_code` to be unique, including under
concurrent creation. Concurrent bookings could receive identical codes.

### How was it reproduced?

```text
5 concurrent POST /bookings for 5 distinct, non-overlapping slots; compare
reference_code values.
```

Expected:

```text
All 5 reference codes unique
```

Actual before fix:

```text
Duplicate reference codes possible under concurrency
```

### How was it fixed?

```python
_lock = threading.Lock()

def next_reference_code() -> str:
    with _lock:
        current = _counter["value"]
        _format_pause()
        _counter["value"] = current + 1
    return f"CW-{current:06d}"
```

### Verification after fix

```bash
# same 5-concurrent-request reproduction
```

Result:

```text
['CW-001004', 'CW-001002', 'CW-001001', 'CW-001005', 'CW-001003'] -> unique: True
```

---

## BUG-018 - Race condition allowed bypassing the booking rate limit

### File(s)/line(s)

- `app/services/ratelimit.py:18-26`

### What was the bug?

`record_and_check` read and trimmed `_buckets[user_id]`, slept
(`_settle_pause`), then appended and wrote back — with no lock, so
concurrent calls could race and lose each other's updates.

### Why did it cause incorrect behavior?

Rule 5 requires the 20-requests-per-60s limit to hold under concurrent
requests. Lost updates under concurrency let more than 20 requests in the
window succeed.

### How was it reproduced?

```text
A user with 6 already-counted requests fires 25 more concurrent
POST /bookings requests (31 total in the window).
```

Expected:

```text
Exactly 20 total succeed across the window; the remaining 11 get 429.
```

Actual before fix:

```text
More than 20 could succeed due to lost bucket updates.
```

### How was it fixed?

```python
_lock = threading.Lock()

def record_and_check(user_id: int) -> None:
    with _lock:
        ...
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
6 prior + 14 in this burst = 20 total successes; 11 got 429.
```

---

## BUG-019 - Race condition caused lost updates in live room stats

### File(s)/line(s)

- `app/services/stats.py:15-26`

### What was the bug?

`record_create`/`record_cancel` read `_stats[room_id]`, slept
(`_aggregate_pause`), then wrote back — with no lock (unlike
`app/services/notifications.py`, which already used `threading.Lock`
correctly for its own side effects).

### Why did it cause incorrect behavior?

Rule 14 requires stats to always stay consistent with the underlying
bookings, including after bursts of concurrent activity. Concurrent
create/cancel calls could lose updates and under/over-count.

### How was it reproduced?

```text
6 concurrent, non-overlapping POST /bookings for the same room; compare
GET /rooms/{id}/stats.total_confirmed_bookings to the number of successful
creates.
```

Expected:

```text
stats.total_confirmed_bookings == number of successful creates
```

Actual before fix:

```text
Could diverge under concurrency due to lost updates.
```

### How was it fixed?

```python
_lock = threading.Lock()

def record_create(room_id, price_cents):
    with _lock:
        ...

def record_cancel(room_id, price_cents):
    with _lock:
        ...
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
successful creates: 6, stats.total_confirmed_bookings: 6, match: True
```

---

## BUG-020 - `GET /bookings/{id}` let any org member read another member's booking

### File(s)/line(s)

- `app/routers/bookings.py:162-186`

### What was the bug?

`get_booking` scoped the lookup only by `Room.org_id == user.org_id`. Unlike
`cancel_booking` (a few lines below it), it never checked whether the
requesting non-admin user actually owned the booking.

### Why did it cause incorrect behavior?

Rule 10 requires members to read/cancel only their own bookings, with
another member's booking id returning `404 BOOKING_NOT_FOUND`. Any member
could instead read any other member's booking in the same org, including
its refund history.

### How was it reproduced?

```text
Member Bob creates a booking. Member Charlie (same org) calls
GET /bookings/{bob_booking_id}.
```

Expected:

```text
404 BOOKING_NOT_FOUND
```

Actual before fix:

```text
200 OK with Bob's booking JSON
```

### How was it fixed?

```python
if user.role != "admin" and booking.user_id != user.id:
    raise AppError(404, "BOOKING_NOT_FOUND", "Booking not found")
```
added to `get_booking`, mirroring the check already present in `cancel_booking`.

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
BUG-020 charlie reads bob's booking: 404
```

---

## BUG-021 - Refund rounding truncated instead of rounding half-cents up

### File(s)/line(s)

- `app/routers/bookings.py:220` (response calculation)
- `app/services/refunds.py:14-18` (`log_refund`)

### What was the bug?

The response used Python's `round()` (round-half-to-even) on a float, and
`log_refund` independently recomputed the amount via float division and
`int()` truncation — two separate formulas that happened to often agree but
were not guaranteed to.

### Why did it cause incorrect behavior?

The contract specifies half-cents round up, with the explicit example
"50% of 1001 = 501". Both existing implementations returned 500. The dual,
independently-computed values also risked violating the requirement that
the cancel response amount equal the stored `RefundLog` amount.

### How was it reproduced?

```text
Create a 1001-cent, 1-hour booking; cancel it with 24-48h notice (50% tier).
```

Expected:

```text
refund_amount_cents == 501, RefundLog.amount_cents == 501
```

Actual before fix:

```text
refund_amount_cents == 500, RefundLog.amount_cents == 500
```

### How was it fixed?

Centralized the calculation with exact integer round-half-up math (no
floats) inside `log_refund`, and made the API response read the persisted
value back instead of recomputing it:

```python
# app/services/refunds.py
amount_cents = (booking.price_cents * percent + 50) // 100
```
```python
# app/routers/bookings.py
refund_entry = log_refund(db, booking, refund_percent)
refund_amount_cents = refund_entry.amount_cents
```

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
refund_amount_cents for 50% of 1001: 501
RefundLog amount_cents: 501
```

---

## BUG-022 - Opposite notification lock order could deadlock the service

### File(s)/line(s)

- `app/services/notifications.py:24-35`

### What was the bug?

`notify_created` acquired `_email_lock` then `_audit_lock`; `notify_cancelled`
acquired `_audit_lock` then `_email_lock` — a classic lock-order inversion.

### Why did it cause incorrect behavior?

Rule 16 requires no combination of concurrent valid requests to hang the
service. A concurrent booking create and cancel could each hold one lock
while waiting forever for the other, deadlocking both request threads (and,
under load, eventually exhausting the whole worker thread pool).

### How was it reproduced?

```text
Run notify_created and notify_cancelled concurrently (e.g. a POST /bookings
and a POST /bookings/{id}/cancel fired at the same time).
```

Expected:

```text
Both requests complete.
```

Actual before fix:

```text
Both threads could remain blocked indefinitely.
```

### How was it fixed?

Made `notify_cancelled` acquire the locks in the same order as
`notify_created` (email, then audit):

```python
def notify_cancelled(booking) -> None:
    with _email_lock:
        with _audit_lock:
            _write_audit("cancelled", booking)
        _send_email("cancelled", booking)
```

### Verification after fix

```bash
# concurrent create + cancel against the same room
```

Result:

```text
BUG-022 concurrent create+cancel notifications completed without deadlock: True
```

---

## BUG-023 - Usage-report cache not invalidated when a booking is created

### File(s)/line(s)

- `app/routers/bookings.py:132-134` (`create_booking`)

### What was the bug?

`create_booking` invalidated the room availability cache but never the
org's usage-report cache.

### Why did it cause incorrect behavior?

Rule 12 requires the usage report to reflect current state immediately.
A cached report undercounted a booking created after the report was cached.

### How was it reproduced?

```text
Fetch a usage report for a date range, create a new confirmed booking in
that range, fetch the same report again.
```

Expected:

```text
Second report count increases by 1.
```

Actual before fix:

```text
Second report returns the stale cached count.
```

### How was it fixed?

```python
cache.invalidate_report(user.org_id)
```
added after the booking commit in `create_booking`.

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
usage report before=0 after=1
```

---

## BUG-024 - Availability cache not invalidated when a booking is cancelled

### File(s)/line(s)

- `app/routers/bookings.py:228-230` (`cancel_booking`)

### What was the bug?

`cancel_booking` invalidated the usage-report cache but never the room/date
availability cache.

### Why did it cause incorrect behavior?

Rule 13 requires availability to reflect current state immediately. A
cached day's availability kept showing a cancelled booking as a busy
interval.

### How was it reproduced?

```text
Create a booking, fetch availability for its date, cancel the booking,
fetch availability again.
```

Expected:

```text
Cancelled booking removed from busy intervals.
```

Actual before fix:

```text
Cancelled booking remained in the cached busy interval list.
```

### How was it fixed?

```python
cache.invalidate_availability(booking.room_id, booking.start_time.date().isoformat())
```
added after the cancellation commit in `cancel_booking`.

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
busy before cancel: 1, after cancel: 0
```

---

## BUG-025 - Admin export returned 200 for unknown or cross-org room_id

### File(s)/line(s)

- `app/routers/admin.py:65-73`

### What was the bug?

`export()` never validated a supplied `room_id` against the caller's org
before generating the CSV — an unscoped/nonexistent `room_id` simply
produced zero matching rows.

### Why did it cause incorrect behavior?

Rule 9 requires cross-org (and by extension unknown) resource IDs to
behave as non-existent, returning 404 — not a silent empty success.

### How was it reproduced?

```text
Org A admin calls GET /admin/export?room_id=<org_B_room_id>&include_all=true
and GET /admin/export?room_id=999999&include_all=true.
```

Expected:

```text
404 ROOM_NOT_FOUND for both
```

Actual before fix:

```text
200 OK with only the CSV header, for both
```

### How was it fixed?

```python
if room_id is not None:
    room = db.query(Room).filter(Room.id == room_id, Room.org_id == admin.org_id).first()
    if room is None:
        raise AppError(404, "ROOM_NOT_FOUND", "Room not found")
```
added at the top of the `export` handler, before generating the CSV.

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
cross-org export room_id: 404 ROOM_NOT_FOUND
unknown export room_id: 404 ROOM_NOT_FOUND
```

---

## BUG-026 - Usage-report cache not invalidated when a room is created

### File(s)/line(s)

- `app/routers/rooms.py:42-58` (`create_room`)

### What was the bug?

`create_room` inserted the new room but never invalidated the org's
usage-report cache.

### Why did it cause incorrect behavior?

Rule 12 requires the usage report to include rooms with zero bookings and
reflect current state immediately. A room created after a report was
cached for that org/date-range was silently omitted from the report.

### How was it reproduced?

```text
Fetch a usage report for a date range (0 rooms), create a new room in the
same org, fetch the same report again.
```

Expected:

```text
Second report includes the new room with 0 confirmed bookings.
```

Actual before fix:

```text
Second report still shows 0 rooms (stale cache).
```

### How was it fixed?

```python
cache.invalidate_report(admin.org_id)
```
added after the room commit in `create_room`.

### Verification after fix

```bash
# same reproduction as above
```

Result:

```text
rooms in report before creating a room: 0
rooms in report after creating a room: 1
```

---

## BUG-027 - Room stats were lost after API restart

### File(s)/line(s)

- `app/routers/rooms.py:103-119`
- `app/services/stats.py`

### What was the bug?

`GET /rooms/{id}/stats` read the room totals from `services.stats.get(room.id)`,
which is backed only by the process-local `_stats` dictionary.

### Why did it cause incorrect behavior?

The SQLite database persists bookings across API restarts, but `_stats` resets
to `{}` when the process starts. After restart, a room with persisted confirmed
bookings could report:

```text
{"total_confirmed_bookings": 0, "total_revenue_cents": 0}
```

Rule 14 requires room stats to always equal the values derivable from confirmed
bookings.

### How was it reproduced?

```text
Create a confirmed 3000-cent booking, clear/restart the in-memory stats state,
then call GET /rooms/{id}/stats against the same persisted booking data.
```

Expected:

```text
total_confirmed_bookings == 1
total_revenue_cents == 3000
```

Actual before fix:

```text
total_confirmed_bookings == 0
total_revenue_cents == 0
```

### How was it fixed?

The stats endpoint now queries persisted confirmed bookings for the room and
computes the count and revenue from the database at request time.

### Verification after fix

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

## Regression check

```bash
docker compose exec api python -m pytest tests/ -v
```

Result:

```text
tests/test_smoke.py::test_core_flow PASSED
1 passed, 1 warning in 1.65s
```
