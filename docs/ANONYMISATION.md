# Anonymisation Checklist for Double-Blind Submission

*Inteligencia Artificial* (IBERAMIA) uses double-blind review with a
minimum of two anonymous reviewers. This document records every location
where author identity is exposed in the working repository, the
transformation applied in the anonymous review bundle, and the release
procedure after acceptance.

> [!IMPORTANT]
> **Never submit the GitHub URL as the manuscript's repository link.**
> Use an anonymous-review link (e.g. `anonymous.4open.science` or a Zenodo
> anonymous-review deposit) generated from `make anon-bundle`. The public
> repository and permanent DOI are released only after acceptance.

---

## 1. Known Deanonymising Locations

| Location | What is exposed | Transformation in anon bundle |
|---|---|---|
| `CITATION.cff` lines 6–8 | Author name, given name, affiliation | Replaced by `ANONYMISED` |
| `CITATION.cff` line 9 | GitHub repository URL | Replaced by `ANONYMISED` |
| `CITATION.cff` lines 29–32 | `preferred-citation` author name + affiliation | Replaced by `ANONYMISED` |
| `README.md` CI badge | Points to `github.com/Ariful-Furqon/RiceKG-Expert-System` | Badge line removed |
| `analysis/verify_citations.py` line 49 | Crossref `User-Agent` contains `ariful.furqon@unej.ac.id` | Replaced by `ricekg-review@anonymous.invalid` |
| Git commit history | Author name and email in every commit | Squashed to a single anonymous commit |
| `pyproject.toml` line 13 | `authors` name and email | Replaced by `ANONYMISED` |
| `README.md` BibTeX block | Citation key `furqon2026ricekg` and `author = {Furqon, ...}` | Key and author replaced |
| `results/baselines.json` | Previously embedded an absolute path carrying username and institution | Writer now stores repo-relative paths |
| `.gitattributes` | Comment named the cloud-sync provider | Reworded |

If new files are added that contain any of the following strings, they must
be added to this table before the next submission:

The authoritative list is `deny_list` in `analysis/anon_rules.json`. It is
enforced automatically, so this table is documentation rather than the control.
A new file containing an author name, institution, place name, institutional
email, GitHub path, or absolute filesystem path will fail the build.

---

## 2. Building the bundle

```bash
python analysis/build_anon_bundle.py        # or: make anon-bundle
```

Pure Python — neither `make` nor `rsync` is required, so this runs on Windows
Git Bash as well as CI. The bundle is written to `anon_bundle/ricekg-review/`
(excluded from git via `.gitignore`). The working repository is never modified;
`tests/test_anon_bundle.py::test_working_tree_is_untouched` asserts this.

Steps:

1. Collect the tracked files via `git ls-files`, which honours `.gitignore`
   and never sees `.git/`, `.venv/`, `scratch/`, or the task briefs.
2. Copy them, skipping the entries in `exclude_from_bundle`
   (`analysis/anon_rules.json`, `analysis/build_anon_bundle.py`, and this
   document) — the anonymisation tooling necessarily contains the identifiers
   it exists to remove, so it must not travel with the bundle.
3. Apply the substitution rules to every text file.
4. `git init` and commit once as `Anonymous <review@anonymous.invalid>` with
   the message `Initial submission`, so the authored history does not ship.
5. **Verify**: scan every file in the finished bundle, and every path, against
   the deny list. Any hit deletes the bundle and exits non-zero.

### Why step 5 is the important one

Substitution rules only remove the leaks somebody thought of. Before the
deny-list scan existed, seven identifiers survived a bundle build that looked
successful, including `pyproject.toml` untouched in full (its extension was
missing from the file filter) and an absolute path inside
`results/baselines.json` that carried both username and institution.

A bundle that cannot be verified is not produced. If the scan fires, add a rule
to `analysis/anon_rules.json` and rebuild — never ship past a warning.

### Editing the rules

`analysis/anon_rules.json` holds three lists:

- `substitutions` — ordered pairs; **order matters**. Longer, more specific
  patterns first; the bare-surname catch-all last. (`Furqon, Muhammad Ariful`
  must precede `Muhammad Ariful`, or the surname is left stranded — this was a
  real defect, and `test_substitution_order_removes_bare_surname` guards it.)
- `deny_list` — terms the finished bundle must not contain anywhere.
- `text_extensions` / `text_filenames` — which files get substituted. **Add new
  text formats here**; anything absent is copied byte-for-byte and will only be
  caught by the deny-list scan.

The bundle can then be uploaded to:
- [anonymous.4open.science](https://anonymous.4open.science/) (GitHub-based anonymous hosting)
- [Zenodo sandbox](https://sandbox.zenodo.org/) with the "restricted" access type
  and an anonymous-review link

> [!CAUTION]
> Do not publish the bundle to the public GitHub repository or any
> publicly indexed URL before acceptance. The anonymous review host must
> support access-controlled or token-gated sharing.

---

## 3. Release Procedure After Acceptance

1. **Do not alter the accepted version's content.** Create a new git tag
   `v1.0-accepted` on `main`.
2. Deposit the working (non-anonymised) repository to Zenodo via the
   GitHub integration. This generates a permanent DOI.
3. Update `CITATION.cff` with the Zenodo DOI and the journal DOI once
   both are assigned.
4. The manuscript's supplementary material or data-availability statement
   should cite the Zenodo DOI, not the GitHub URL, as the permanent
   identifier.
5. Delete or archive the `anon_bundle/` directory.

---

## 4. Pre-submission audit

The deny-list scan in the builder is the audit; it runs on every build and in
CI. To run it alone against an existing bundle:

```bash
python -c "import sys; sys.path.insert(0,'analysis'); import build_anon_bundle as b; from pathlib import Path; v=b.verify(Path('anon_bundle/ricekg-review'), b.load_rules()); print('
'.join(v) or 'clean')"
```

If a match appears, add a substitution rule to `analysis/anon_rules.json` and
rebuild. Do not edit the bundle by hand — the next build would overwrite it and
the leak would return.
