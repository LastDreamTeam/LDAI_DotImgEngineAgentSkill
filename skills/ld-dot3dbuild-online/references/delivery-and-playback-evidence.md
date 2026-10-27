# Delivery and playback evidence

## Verify the input and preserved invariants

- Resolve assets through known delivery manifests, connected storage and project metadata before asking the user to locate work already delivered. Follow existing access permissions; a repository LFS pointer is not the binary model.
- Test file headers, expected size and a fresh open/import rather than trusting the extension. Preserve an unreadable or truncated source without silently overwriting it. A valid GLB may permit a new editable Blender scene, but does not restore every original modifier, control or authoring setting from a missing/unreadable BLEND.
- Keep byte integrity checks separate from scene equivalence checks. SHA-256 can verify an uploaded/downloaded copy; it cannot show that two differently serialized scenes have identical rigs. Compare semantic geometry, weights, shape keys, transforms, actions, material/UV data and declared unaffected objects separately.
- After local prop repairs, verify unchanged body geometry, skeleton, weights, blink/other shape keys, other props and action/visibility schedule as applicable. Recheck intentional topology edits by appearance and behavior instead of requiring their hashes to stay unchanged.

## Separate source, optimization and recording copies

Maintain a complete-material editable master, separately named reduced-texture/runtime
candidate, requested exports and a recording-only scene if needed. Never replace the
master with a viewport workaround. If transparency, expensive effects or overlays are
changed for capture, disclose exactly what the recording omits and keep full-material
stills/exports available. Do not use those omissions to conceal a known model defect.

## Capture the evidence the user actually requested

- Distinguish real application GUI recording, offline rendered turntable and a slideshow of sampled angles. Do not label one as another or call synthesized interpolation a real recording.
- For try-on review, show the prop on the actual character, not only floating by itself. Frame front, profile, back and top/oblique views so fit and clearance remain visible; isolate each selected prop or clearly label combinations.
- Record the final saved revision and inspect the actual output video: opening, middle, ending, every prop interval, clipping, texture loading, missing frames and unintended visibility changes. A recording command's successful exit does not prove usable footage.
- Preserve the raw capture when practical. If speeding up, report source duration, delivered duration and approximate playback multiplier. Frame-rate metadata alone does not prove unique visual frames or real-time animation speed. Inspect sampled decoded frames and avoid claiming smooth motion from repeated images.
- Keep quality claims bounded: a quick textured viewport is not a final PBR render; a static rotation is not a deformation test; Blender playback is not Unity/VRChat runtime validation.

## Persist before declaring saved

1. Store editable source, construction/repair scripts where applicable, textures, exports, and final evidence in the authorized durable destination. Keep a clear latest entry and historical revisions; do not overwrite the only accepted source.
2. Record revision, file names, byte sizes, SHA-256, storage IDs/links and tested deliverables in a small delivery manifest. Never include credentials or temporary signed URLs as durable access links.
3. Verify destination metadata and, for critical editable sources/archives, download and compare hashes. Fresh-open the persisted/retrieved model; run archive integrity checks and verify texture dependencies.
4. Respect actual transfer limits. Prefer usable per-asset packages over a single oversized archive. If split archives are necessary, retain all volumes, document a compatible extractor, and test reconstruction. An extractor incompatibility alone is not proof of corrupt data.
5. Report upload completion only after confirmed success. Keep local save, uploaded object, verified retrievable copy and user-delivered attachment as distinct states. Preserve successfully uploaded parts after a partial failure rather than repeating the entire operation blindly.

A temporary workspace can disappear. On resume, verify durable copies and task state
before claiming progress. An exact backup recovery, a reconstruction from earlier
source, and a visually similar replacement are different outcomes; label them honestly.
