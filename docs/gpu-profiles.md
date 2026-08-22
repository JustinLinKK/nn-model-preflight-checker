# GPU profiles

Profiles are YAML documents validated by `profiles/schema.json`. Version 1 records vendor, name,
architecture, compute capability, VRAM bytes, native training dtypes, and an explicit unsupported
feature list.

Bundled profiles:

- `nvidia/v100_16gb`
- `nvidia/v100_32gb`
- `nvidia/a10_24gb`
- `nvidia/a100_40gb`

Profile checks are capability filters, not CUDA execution. CUDA-only packages, custom extensions,
streams, distributed execution, and architecture-specific kernels still require the target-GPU
canary.

