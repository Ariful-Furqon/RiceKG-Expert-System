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
| `docs/ETHICS.md` lines 5–7 | Institution name (Universitas Jember), ethics committee name | Replaced by `[Institution name withheld for review]` |
| Git commit history | Author name and email in every commit | Squashed to a single anonymous commit |

If new files are added that contain any of the following strings, they must
be added to this table before the next submission:

- `Furqon` / `Ariful` / `ariful`
- `Universitas Jember` / `UNEJ` / `unej`
- `github.com/Ariful-Furqon`
- Any institutional email address

---

## 2. `make anon-bundle` — What It Does

Running `make anon-bundle` produces a subdirectory `anon_bundle/` in the
repository root (excluded from git via `.gitignore`). It does **not**
modify the working repository.

Steps performed by the Makefile target:

1. Copy the entire working tree to `anon_bundle/ricekg-review/`, excluding
   `.git/`, `anon_bundle/`, and any file listed in `.gitignore`.
2. Apply text replacements (see Section 1) to every affected file.
3. Run `git init` in `anon_bundle/ricekg-review/`, add all files, and
   create a single commit authored as `Anonymous Reviewer <review@anonymous.invalid>`
   with a neutral commit message `Initial submission`.
4. Print the path to the bundle directory and remind the user to upload it
   to an anonymous review host.

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

## 4. Grep Commands for Pre-Submission Audit

Run these from the repository root to catch any newly added deanonymising
text before generating the bundle:

```bash
# Author name variants
grep -rI --include="*.py" --include="*.md" --include="*.cff" --include="*.yml" \
  -e "Furqon" -e "Ariful" -e "ariful" .

# Institution name
grep -rI --include="*.py" --include="*.md" --include="*.cff" --include="*.yml" \
  -e "Universitas Jember" -e "UNEJ" -e "unej.ac.id" .

# GitHub URL
grep -rI --include="*.py" --include="*.md" --include="*.cff" --include="*.yml" \
  -e "Ariful-Furqon" .
```

If any match appears in a file not already listed in Section 1, add it to
the table before running `make anon-bundle`.
