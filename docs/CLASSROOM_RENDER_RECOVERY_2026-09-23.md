# Classroom render fidelity and recovery

## Concept fidelity checkpoint

The default same-camera AI finish now uses the existing `balanced` policy,
labelled **Concept finish**. Its prompt preserves building count, placement,
footprint, height and roof massing, street routes and junctions, pedestrian
access, and park programme. Materials, foliage, lighting and small details can
improve. **Strict detail** remains available in Source checks, alongside
Expressive interpretation. All results still require comparison with the source.

No gate threshold was changed. This corrects the mismatch between the classroom
ideation target and a default requiring exact facade openings. It is not evidence
that previous failed images now pass, or that every gate failure was a false
positive. The old Currie outputs do not retain the full control-image bundle,
so an exact offline replay is not possible. Future attempts need the immutable
source, controls, settings, provider original and diagnostics retained together.

Validation: 36 focused frontend tests passed; TypeScript check passed. No image
provider was called. The funded close/wide comparison and independent visual
review remain open.

## Recovery work still required

Persist attempts before dispatch; bind an idempotency key to exact request bytes;
bound the queue; reserve credits atomically; keep unknown provider costs against
the cap while refunding the student once; retain results before gallery work;
recover after reload without dispatching another paid request. Hosted worker,
storage and failure tests remain separate from local unit evidence.
