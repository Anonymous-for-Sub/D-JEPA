# Anonymous review release

This repository and its static website are maintained as a separate anonymous release.

- Website: https://anonymous-for-sub.github.io/D-JEPA/
- Code: https://github.com/Anonymous-for-Sub/D-JEPA
- Model checkpoints and decision-supervision data will be released after acceptance.
- Resource buttons display the release notice instead of opening a model or dataset account.
- The site has no author block, institutional attribution, paper button, or lab link.

## Maintenance

Apply scientific, implementation and presentation changes here deliberately. Do not mirror another checkout wholesale: that can restore author metadata, resource links or unrelated history. Preserve anonymous commit identity and avoid identifying machine paths in public logs.

Before pushing, run:

```bash
python3 scripts/check_anonymous_release.py
python3 scripts/check_site.py
node --test tests/explainer*.test.mjs
```

The static website is published from `docs/` through the Pages workflow. Its repository setting must use GitHub Actions as the Pages source. Asset URLs are relative and support the `/D-JEPA/` subpath.

The download utility accepts explicit `--model-repo` and `--dataset-repo` values once resources are available. During review, commands requiring unreleased data/checkpoints are documented workflows, not automatic downloads. Local method, toy-example and CPU tests remain available.
