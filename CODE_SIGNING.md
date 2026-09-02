# Code Signing Policy

[← Back to README](README.md)

## Current status

HOTS Hosts is currently distributed as an open-source project, but the Windows release installer is **not currently signed with a trusted commercial code-signing certificate**.

The project previously applied to the SignPath Foundation program. The application was not approved at that time because the project did not yet meet the Foundation program's public visibility and adoption criteria.

The project may reapply in the future as its community adoption and external visibility grow.

## Release artifact

The primary Windows release artifact is:

- `HOTS_Hosts_setup.exe`

Release artifacts are published through the project's GitHub Releases page:

https://github.com/darsono6/HOTS/releases

## Build process

Release builds are produced through GitHub Actions.

The intended build pipeline:

1. builds the application from the public repository source;
2. compiles/packages the Python application for Windows;
3. creates the Windows installer with Inno Setup;
4. publishes the release artifact through GitHub Releases.

The project does not intentionally use locally built binaries as official release artifacts.

## Source transparency

The source code used to build HOTS Hosts is publicly available in this repository.

Users who do not want to run an unsigned pre-built executable can inspect the source and build the application themselves.

## Why Windows may show a SmartScreen warning

Because the current release does not have a trusted commercial code-signing certificate and the project has limited download reputation, Windows SmartScreen may display a warning such as:

> Windows protected your PC

This warning should not be treated as proof that a file is safe or unsafe.

Users should obtain release binaries only from the official GitHub Releases page and should verify the release version before running them.

## Future signing

If HOTS Hosts is accepted into a trusted open-source code-signing program or obtains another trusted signing certificate, this document will be updated with:

- the signing provider;
- the certificate identity;
- the official signing workflow;
- verification instructions;
- the date from which signed releases apply.

Until then, release binaries should be considered **unsigned**.

## Maintainer

HOTS Hosts is currently maintained by:

- GitHub: https://github.com/darsono6/HOTS
- Maintainer: Darsono (`@darsono6`)
