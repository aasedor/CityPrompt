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
