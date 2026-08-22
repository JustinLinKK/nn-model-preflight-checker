# Candidate adapter API

The adapter named by the manifest is instantiated with no arguments inside each worker. Keep
construction deterministic and use the supplied context mapping:

- `manifest`: normalized manifest values.
- `scenario`: batch size, shape name/value, precision, and mode.
- `device`: `"cpu"` or `"meta"`.
- `fixture_root`: normalized fixture path or `null`.

`build_train_batch` and `build_validation_batch` receive the scenario and device separately.
They should exercise real transforms, tokenization, dataset access, and collation using tiny
fixture data. Avoid network downloads.

`training_step` must return one finite scalar PyTorch tensor connected to trainable model
parameters. Model/optimizer ownership stays with the adapter, so custom loss and batch layouts
need no checker-specific inference.

For branched models, define:

```python
def required_gradient_names(self, model):
    return {"encoder.weight", "classifier.weight"}
```

Without it, Model Preflight requires at least one trainable parameter to receive a gradient and
checks every produced gradient for finiteness.

`FunctionAdapter` is provided for integrations composed of top-level functions.

