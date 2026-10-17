# Shared water candidate v4

An empty `.gdignore` isolates this entire candidate directory from editor import. The current game does not load it. Removal of that file requires a bounded integration decision and engine validation.

This disconnected candidate prepares a common D4 water cache and owner-local bank caches. It does not register an autoload, edit a scene, or alter game rendering.

The source has been reconstructed after loss of the previous working files. It has not been compiled or rerun in Godot. Previous numerical results are historical observations, not validation of these bytes.

`PINS_SHA = "PLACEHOLDER"` deliberately rejects every preparation request. Original source-based responsibility masks, owner contracts and verified input pins must be rebuilt before isolated testing. A missing mask or any readiness status other than `MASK_READY_FOR_ISOLATED_PROBE` must also reject loading. Do not bypass these gates to enable the candidate.

The spatial modes are an unchanged binary negative control and a D4 3×3 inset. The inset suppresses water only near supported unresolved/protected samples; original owner support remains a separate drawing constraint. No smoothing or new shoreline is inferred. All original owner rectangles, ordering, world phases and unresolved cross-family ports must be preserved by the consumer.

Preparation uses atomic staging, actual RenderingServer update completion, a required external validator, and same-ticket deadline checks before/after validation and before publication. The production clock remains `Time.get_ticks_msec()` with the original strict `> 10000` millisecond timeout.

A future isolated probe must reproduce constant controls, lifecycle/deadline negative controls, all three original contexts and both world phases, and same-camera D2 color/weight comparisons. Technical checks do not certify artwork seams, padding, early generated banks, mask hard edges or shoreline geometry. Root visual review remains required before any integration.
