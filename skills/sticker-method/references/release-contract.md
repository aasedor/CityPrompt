# Sticker Method release contract

## Contents

1. Required inputs
2. Machine gates
3. Visual gates
4. Evidence package
5. Fail-closed publisher
6. Batch promotion

## 1. Required inputs

A release publisher must lock:

- exact reference paths, hashes, dimensions, and variant identity;
- binding architecture and tier contract;
- geometry hash and mesh count;
- builder and focused-test hashes or committed identities;
- intrinsic asset provenance hash;
- compiler, signature profile, registry, carrier package, and contract hashes;
- formal manifest, validation, preflight, renders, and comparison-board hashes.

## 2. Machine gates

Require all of the following:

- deterministic geometry, asset, compiler, and publisher output;
- globally unique mesh names;
- closed/outward construction where applicable;
- exact-one ownership of every visible polygon;
- zero missing and multiply owned faces;
- zero fallback/default/clay material;
- registered assets only;
- roof roles at or above their declared roof datum;
- plan materials only on intended plan/upward faces;
- valid glass profile and pane/card/backing containment;
- metric UV scale and no nonuniform sticker scaling;
- fixed-kit and whole-module invariants for every tier;
- validation and production preflight status `pass`.

Performance warnings may remain nonblocking only when visual reviewers explicitly accept them and the package records them.

## 3. Visual gates

Require the nine formal cameras and an independent architectural review. The release score record must include all five component values, exact total or mean, and hard-stop count.

Release only when:

- fixed landmark canonical score is at least 95.00; or
- every modular tier is at least 95.00 and the exact unrounded tier mean is strictly greater than 95.00;
- hard-stop count is zero;
- Sticker/material review finds no coverage or registration stop.

## 4. Evidence package

Promote a compact review directory containing:

- six or more representative formal renders;
- comparison boards covering exact front, oblique/detail, roof, rear/interior, and tier scale where applicable;
- `machine-evidence.json`;
- copied validation and production-preflight reports;
- `visual-approval.json`;
- `release-evidence-scaffold.json` or equivalent final approval record.

Do not promote raw experiments, all intermediate renders, assembled GLBs, caches, or temporary diagnostics into the review package.

## 5. Fail-closed publisher

The publisher must refuse to write approved output when:

- any locked hash differs;
- a required formal view is absent;
- validation/preflight fails;
- exact-one coverage fails;
- a score is absent or below the threshold;
- a hard stop remains;
- an approved tier does not match its contract;
- a fixed identity count changes;
- the output ledger would modify another building's approval.

Run the publisher twice and compare every output byte. Record the final board and evidence hashes.

## 6. Batch promotion

Promote only the current order after its release package passes. Assert all earlier entries are unchanged. The ledger should record:

- order, archetype id, variant id;
- representation;
- `approved_95_plus` status;
- exact scores and hard stops;
- identity locks;
- approved tier dimensions;
- LEGO/fixed-landmark rule;
- review path.

Run `scripts/audit_release.py --repo <repo-root>` before committing. The audit is a release guard, not a replacement for formal review.
