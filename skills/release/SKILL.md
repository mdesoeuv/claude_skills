---
name: release
description: Cut a versioned release — semantic version bump, CHANGELOG from conventional commits, git tag, GitHub release notes, and artifact publishing. Use when the user says "release", "tag a version", "bump the version", "write release notes", or "update the changelog".
argument-hint: "[major|minor|patch|<version>]"
metadata:
  tier: recommended
---

# Release

A release is a promise about compatibility. The version number is the only part of that promise most consumers will read.

## Decide the version

From the commits since the last tag (`git log $(git describe --tags --abbrev=0)..HEAD --oneline`):

- `BREAKING CHANGE` footer or `!` after the type → **major**
- any `feat` → **minor**
- only `fix`/`perf`/`refactor`/`docs`/`chore` → **patch**

Pre-1.0 projects treat breaking changes as minor. If the project uses a tool (`semantic-release`, `release-please`, `changesets`, `cargo release`, `npm version`), use that tool instead of hand-rolling; the point of conventions is automation.

## Steps

1. Confirm the working tree is clean and on the release branch; the CI on the last commit is green.
2. Bump the version in every place it lives (`package.json`, `pyproject.toml`, `Chart.yaml`, `version.tf` locals, Helm `appVersion`). Grep for the old version to be sure.
3. Update `CHANGELOG.md` (Keep a Changelog format) by moving `Unreleased` into a dated section:

```markdown
## [1.4.0] - 2026-10-17
### Added
- OIDC login for the admin console (#412)
### Fixed
- Handle S3 buckets with no tags in the inventory job (#418)
### Changed
- Bump aws provider to 5.60
```

Group by Added / Changed / Deprecated / Removed / Fixed / Security. Write for consumers: what they can do now, what they must change. Drop internal-only chores.

4. Commit: `chore(release): v1.4.0`.
5. Tag annotated: `git tag -a v1.4.0 -m "v1.4.0"` and push the tag only when the user asks.
6. Publish: `gh release create v1.4.0 --notes-file <section extracted from CHANGELOG>` and attach artifacts if the project ships them. Let CI build and push images/packages from the tag; do not build release artifacts on a laptop.
7. Verify the published artifact (image tag exists in ECR, package visible in the registry) and report.

## Infra-specific

- Terraform modules: tag the module repo; consumers pin `?ref=v1.4.0`. Breaking variable renames are major.
- Helm charts: `version` is the chart's semver; `appVersion` is the app's. Bump both as appropriate.
- Lambda/containers: the deployable is the image digest; the tag is a label. Record the digest in the release notes.

## When $ARGUMENTS is given

Use it as the bump type or exact version; still sanity-check it against the commit history and flag a mismatch.
