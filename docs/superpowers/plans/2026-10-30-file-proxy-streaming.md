# File proxy streaming regression plan

**Scope:** A finite follow-up to the overnight student stress test. Preserve
authentication, project authorization, file tickets, MIME / download headers
and existing cache policy. Change only file delivery and its regression tests.

**Evidence:** Ten concurrent 29.4 MB downloads returned exact original bytes.
One client health measurement reached 1.45 seconds during the burst. That
client shares an event loop, so the measurement alone does not establish server
latency. Source inspection independently shows synchronous S3 reads and full
object buffering inside an asynchronous endpoint.

## Verification sequence

1. Reproduce event-loop blocking with bounded fake storage and an independent
   heartbeat; do not exhaust memory or contact paid providers.
2. Deliver bounded chunks with blocking storage operations off the event loop.
   Close storage bodies on completion, failures and disconnects. Preserve all
   existing authorization checks before storage access.
3. Verify exact bytes, metadata / HEAD behavior, private/public caching,
   sanitized filenames, storage errors and cancellation. Review database and
   storage-client lifetime when delivering a long response.
4. Run focused file/security tests, lint and formatting; obtain independent
   review. Run the full backend suite after the final source correction.
5. Repeat the finite local transfer trial with an independent health probe.
   Keep output byte integrity and latency measurements separate.
6. Commit the verified unit, build a matching review artifact, and update the
   existing draft handoff PR without changing deployment or catalogue approval.

The previous source checkpoint remains available at `bb593c68f`. No paid image
or video generation, live deployment or additional catalogue activation is part
of this follow-up. Confidential runtime credentials remain outside the repository.

## Verified checkpoint

- Independent review found no unresolved Critical or Important findings. Related
  file/security checks passed 92 cases; the reviewer independently ran 15 lifecycle cases.
- Full backend passed 3,148 tests with three skips using a fresh migrated test
  database. Ruff, Black and the existing mypy boundary passed.
- Both retained imported originals still match their hashes after the API restart;
  anonymous requests are rejected and all saved routes/buildings remain present.
- The independent local health probe improved from a 1,359 ms peak to 218 ms
  during ten concurrent original downloads. Total transfer time increased from
  2.328 to 4.157 seconds; no general internet throughput claim is implied.
- Final hosted artifact and current-head CI results belong in the delivery
  receipts and existing review PR. Publication approval remains a separate gate.
