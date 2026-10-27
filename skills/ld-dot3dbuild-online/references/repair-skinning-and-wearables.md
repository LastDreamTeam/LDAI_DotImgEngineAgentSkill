# Targeted skinning and wearable repair

## Diagnose the moving surface before changing the rig

- Compare rest pose, a controlled single-bone rotation, and the actual retargeted action. Distinguish joint placement, source animation translation/scale, retargeting/rest-pose mismatch, topology bridges, and incorrect weights; a wide-looking shoulder alone does not identify the cause.
- Locate the designed body joint under the clothing, not the outer shoulder sleeve or padding. When the pivot is too lateral, move it toward the anatomical/design joint only by the amount supported by front/profile inspection. Reconcile affected rest transforms, children, skinning and animation; do not merely drag a pose control or apply a universal inward offset.
- Inspect both shoulders independently. Symmetric names or a mirrored edit do not prove symmetric topology or deformation.
- For underarm/chest webbing, inspect actual connected geometry and per-vertex influences. Remove an unintended topology bridge or misplaced arm influence locally. Do not freeze all sleeve/chest vertices to the torso: this can fix the chest while leaving the sleeve behind and letting the arm emerge through it.
- Retest coupled regions after every repair: torso, sleeve, upper arm and cuff in arm-up, forward reach, bend and twist poses. Include frames between extremes, not only neutral and the highest reach.
- For side-skirt lift during crouching, isolate side panels from the front panel that may need to follow a raised thigh. Reduce unintended thigh influence locally and redistribute to suitable pelvis/skirt controls. Do not freeze the whole garment in world space or promise cloth collision from weight changes alone.

## Fit wearables to the actual body and reference

- Use the supplied body asset rather than a similar mascot or a proxy as final acceptance. For a handless character, design wearable/mounted props instead of assuming a hand grip.
- Read the user's sketch as coverage and shape guidance. Mark top/bottom edges, overlap with other accessories, knot/fastener location and tail lengths. Do not invent a rule to avoid an existing accessory when the sketch explicitly wraps around or over it.
- For an ellipsoid torso scarf, deform the full band around front, sides and back with appropriate thickness and clearance. Uniformly scaling or translating a horizontal ring does not produce a fitted wrap. Keep mouth/face readability and inspect the knot and tails separately.
- For glasses, size the lens frame independently of the temples. Rebuild supports to start laterally and bend along the body's surface when appropriate; scaling the whole assembly can leave oversize or horn-like supports.
- Use evaluated world-space body/accessory surfaces when guiding offsets with BVH or nearest-surface queries. Treat signed nearest normals cautiously on open or layered meshes. Check the entire support, including the middle, from front, side, top and back; a successful query is not proof of clearance or a good silhouette.
- Choose clearance from asset scale, thickness and intended motion, not a borrowed millimeter or percentage constant. Static fitting is not proof of extreme-pose, cloth-physics or runtime collision safety.

## Protect seams and materials during deformation

- Inspect whether a generated mesh duplicates geometric vertices along UV seams. Smoothing independently split vertices can pull coincident seam positions apart and expose black cracks.
- When those positions represent one continuous surface, weld only the verified geometric duplicates before smoothing, preserving face-corner/loop UVs and intended hard edges. Do not merge UV islands or weld intentional layered surfaces indiscriminately. Confirm compatibility with existing shape keys, weights and topology-dependent data before topology changes.
- Inspect UV stretch after large deformations. Reproject the affected band or patch with consistent texel density when necessary; preserve unaffected tails/details and material assignments. If texture sharpness softens, disclose the remaining difference rather than claiming exact restoration.

## Preserve the character while changing a prop

Record unaffected base mesh geometry, transforms, skeleton hierarchy/rest transforms,
weights, shape keys (including blink), materials/UVs, and action ranges before editing.
Keep other approved props invariant. Compare decoded scene data within a documented
precision, not just whole-file hashes that change on save. Use before/after fixed views
and fresh export/import checks to supplement these invariants. Parent a rigid prop to
the appropriate existing bone without re-skinning the entire character unnecessarily.

When changing rigid bone parenting, preserve the intended world placement and check
parent-inverse and local transforms explicitly; do not carry over unmeasured display-root
scale. If a permanently hidden object's world matrix appears stale, compare its stored
local transforms, parent inverse and evaluated visible state before treating it as a
real transform regression. Do not silently repair a dependency-graph cache symptom.
