# CHANGELOG

<!-- version list -->

## v1.0.0 (2025-09-08)

### Bug Fixes

- Add missing build dependencies to GitHub workflows
  ([#22](https://github.com/UCSC-IDTAP/Python-API/pull/22),
  [`4e2effd`](https://github.com/UCSC-IDTAP/Python-API/commit/4e2effd2a23432f9cfbea5879226a71d62872a40))

- Add README.md version tracking to semantic-release config
  ([#22](https://github.com/UCSC-IDTAP/Python-API/pull/22),
  [`4e2effd`](https://github.com/UCSC-IDTAP/Python-API/commit/4e2effd2a23432f9cfbea5879226a71d62872a40))

- Grant pull-request write permission for PR comments
  ([#22](https://github.com/UCSC-IDTAP/Python-API/pull/22),
  [`4e2effd`](https://github.com/UCSC-IDTAP/Python-API/commit/4e2effd2a23432f9cfbea5879226a71d62872a40))

- Make PR comment step non-critical in workflow
  ([#22](https://github.com/UCSC-IDTAP/Python-API/pull/22),
  [`4e2effd`](https://github.com/UCSC-IDTAP/Python-API/commit/4e2effd2a23432f9cfbea5879226a71d62872a40))

- Mark all remaining integration test functions
  ([#22](https://github.com/UCSC-IDTAP/Python-API/pull/22),
  [`4e2effd`](https://github.com/UCSC-IDTAP/Python-API/commit/4e2effd2a23432f9cfbea5879226a71d62872a40))

- Mark all SwaraClient() auth tests as integration
  ([#22](https://github.com/UCSC-IDTAP/Python-API/pull/22),
  [`4e2effd`](https://github.com/UCSC-IDTAP/Python-API/commit/4e2effd2a23432f9cfbea5879226a71d62872a40))

- Mark test_large_query_performance as integration test
  ([#22](https://github.com/UCSC-IDTAP/Python-API/pull/22),
  [`4e2effd`](https://github.com/UCSC-IDTAP/Python-API/commit/4e2effd2a23432f9cfbea5879226a71d62872a40))

- Skip integration tests in CI to avoid authentication issues
  ([#22](https://github.com/UCSC-IDTAP/Python-API/pull/22),
  [`4e2effd`](https://github.com/UCSC-IDTAP/Python-API/commit/4e2effd2a23432f9cfbea5879226a71d62872a40))

### Features

- Implement all three workflow improvements from review
  ([#22](https://github.com/UCSC-IDTAP/Python-API/pull/22),
  [`4e2effd`](https://github.com/UCSC-IDTAP/Python-API/commit/4e2effd2a23432f9cfbea5879226a71d62872a40))

- Implement automated version bumping and PyPI publishing
  ([#22](https://github.com/UCSC-IDTAP/Python-API/pull/22),
  [`4e2effd`](https://github.com/UCSC-IDTAP/Python-API/commit/4e2effd2a23432f9cfbea5879226a71d62872a40))


## v0.1.14 (2025-09-08)


## v0.1.13 (2025-09-08)


## v0.1.10 (2025-08-14)

### Bug Fixes

- Resolve discontinuous jumps in Trajectory ID 6 (yoyo) compute method
  ([#9](https://github.com/UCSC-IDTAP/Python-API/pull/9),
  [`9ee079f`](https://github.com/UCSC-IDTAP/Python-API/commit/9ee079f4696a182187f9d79ad74c046f9e270cb7))


## v0.1.9 (2025-08-14)


## v0.1.8 (2025-08-12)


## v0.1.7 (2025-08-11)


## v0.1.6 (2025-08-07)

### Bug Fixes

- Resolve client test failure by mocking waiver check endpoint
  ([`6201187`](https://github.com/UCSC-IDTAP/Python-API/commit/6201187be6148f7e66decc6b83c9c46e01b3edf1))

- Resolve critical packaging configuration bugs
  ([`76fadec`](https://github.com/UCSC-IDTAP/Python-API/commit/76fadeccba001eb5cd9117f08e334bc12d2da07b))

- Resolve failing unit tests
  ([`82c1a0b`](https://github.com/UCSC-IDTAP/Python-API/commit/82c1a0bf77b23b2c0cb6f51f2d5f0af1aef1ff07))

- Resolve validation conflicts with existing tests
  ([`fa36a44`](https://github.com/UCSC-IDTAP/Python-API/commit/fa36a4413d3a74a00d647a2a0f31acedd0384c34))

### Chores

- Bump version to 0.1.6 for PyPI release
  ([`87b4adb`](https://github.com/UCSC-IDTAP/Python-API/commit/87b4adb04905003ce9ef6cc5fa688848caa47732))

- Remove Python cache files from git tracking
  ([`45260b9`](https://github.com/UCSC-IDTAP/Python-API/commit/45260b9e818b5679053356e8ba77abb59fe130bc))

### Documentation

- Add comprehensive PyPI publishing guide to CLAUDE.md
  ([`2474dde`](https://github.com/UCSC-IDTAP/Python-API/commit/2474dde49a7dc3cff143259a2b7cd52457e26759))

- Update documentation for package rename from idtap-api to idtap
  ([`b98a77a`](https://github.com/UCSC-IDTAP/Python-API/commit/b98a77a0af4d4b593123d841661a9244ce6c6749))

### Features

- Add comprehensive parameter validation to all data model classes
  ([`bbcbe67`](https://github.com/UCSC-IDTAP/Python-API/commit/bbcbe679207afa5309b5e6280aeac9b7f30317f6))

- Add comprehensive parameter validation to Raga constructor
  ([`e24343c`](https://github.com/UCSC-IDTAP/Python-API/commit/e24343c65588f8a3eb0082f2a1402e150c01e06b))

- Add get_raga_rules method to retrieve pitch rules for specific ragas
  ([`67e36d7`](https://github.com/UCSC-IDTAP/Python-API/commit/67e36d7fe2b7af74088de19602cf564914d0c62f))

### Refactoring

- Rename package from idtap-api to idtap for cleaner imports
  ([`113109b`](https://github.com/UCSC-IDTAP/Python-API/commit/113109be0bb0ff63203866c1332ef4b7d5ac02f7))

- Replace tempo magic numbers with named constants
  ([`5e0cb3e`](https://github.com/UCSC-IDTAP/Python-API/commit/5e0cb3eeaaece76eac725024ed3637735fbb5584))

- Standardize frequency validation and key handling
  ([`598450f`](https://github.com/UCSC-IDTAP/Python-API/commit/598450f2bc35420646b629b695189ca7a70854a6))

### Testing

- Add manual test for add_trajectory functionality
  ([`03b0cd4`](https://github.com/UCSC-IDTAP/Python-API/commit/03b0cd41539eefcca956c463b03ff337a04ffc7e))


## v0.1.4 (2025-07-31)

- Initial Release
