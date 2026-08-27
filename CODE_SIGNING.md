# Code Signing Policy

This project signs and distributes its Windows release artifacts.

## What is signed

- The Windows installer package (`HOTS_Hosts_setup.exe`), built with Inno Setup
  and published on the [GitHub Releases](https://github.com/darsono6/HOTS/releases)
  page for each tagged version.

## Signing provider

We are applying to the [SignPath Foundation](https://signpath.org) for free
code signing of open source projects.

Planned statement (once approved, as required by the program):
"Free code signing provided by [SignPath.io](https://signpath.io), certificate
by [SignPath Foundation](https://signpath.org)"

Status: pending approval.

## Build and signing process

- All release artifacts are built exclusively via GitHub Actions
  (`.github/workflows/build-release.yml`), triggered by pushing a version tag
  (e.g. `v2.1`).
- The build compiles the Python source with [Nuitka](https://nuitka.net/) in
  standalone mode, then packages the result with
  [Inno Setup](https://jrsoftware.org/isinfo.php).
- Only artifacts built by this CI pipeline, directly from this public
  repository's source code, are ever submitted for signing. No locally built
  binaries are signed.
- The private signing key is held and managed by SignPath (HSM-backed). This
  project does not have access to, or store, the private key.

## Team roles

Single-maintainer project:

- Author / sole committer: [@darsono6](https://github.com/darsono6)
