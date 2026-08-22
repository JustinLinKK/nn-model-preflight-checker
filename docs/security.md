# Security model

Candidate Python is untrusted. The controller does not import it. Local workers provide
process-level containment and cleanup, but a subprocess is not a security boundary against
hostile native code.

Production execution must use an external sandbox/container runtime with:

- a non-root user;
- no GPU devices;
- no network;
- a read-only root filesystem and candidate mount;
- a dedicated bounded writable temporary filesystem;
- dropped Linux capabilities and no-new-privileges;
- memory, CPU, PID, wall-time, and log-size enforcement.

The included CPU image runs as non-root. The `docker run` flags in the README supply the
runtime-only network, mount, capability, and filesystem controls.

