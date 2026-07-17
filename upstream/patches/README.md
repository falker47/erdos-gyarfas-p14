# Upstream Patches

No patch exists in the bootstrap baseline.

The preserved source under `third_party/erdos-gyarfas/` must remain exact. If
a later task needs a compatibility workaround or semantic correction, it must:

1. preserve the original behavior and source;
2. record a minimal regression outside the snapshot;
3. place a reviewable patch or replacement here or in project-owned source;
4. compare original and changed behavior on a documented bounded domain; and
5. state whether the change is portability-only or semantic.

Nothing in this directory promotes upstream behavior to a certified result.
