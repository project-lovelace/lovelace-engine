# Changelog

## [v3.2.0](https://github.com/project-lovelace/lovelace-engine/tree/v3.2.0) (2021-04-11)

[Full Changelog](https://github.com/project-lovelace/lovelace-engine/compare/v3.1.0...v3.2.0)

**Fixed bugs:**

- Fix issue where python processes run forever [\#23](https://github.com/project-lovelace/lovelace-engine/issues/23)

**Merged pull requests:**

- Bump urllib3 from 1.26.3 to 1.26.4 [\#80](https://github.com/project-lovelace/lovelace-engine/pull/80) ([dependabot[bot]](https://github.com/apps/dependabot))
- Modify code runner Dockerfile to support ARM architecture [\#79](https://github.com/project-lovelace/lovelace-engine/pull/79) ([benallan](https://github.com/benallan))
- No need to filter solutions in tests anymore [\#78](https://github.com/project-lovelace/lovelace-engine/pull/78) ([ali-ramadhan](https://github.com/ali-ramadhan))

## [v3.1.0](https://github.com/project-lovelace/lovelace-engine/tree/v3.1.0) (2021-03-27)

[Full Changelog](https://github.com/project-lovelace/lovelace-engine/compare/v3.0.0...v3.1.0)

**Merged pull requests:**

- Run CI tests with Python 3.9 [\#77](https://github.com/project-lovelace/lovelace-engine/pull/77) ([ali-ramadhan](https://github.com/ali-ramadhan))

## [v3.0.0](https://github.com/project-lovelace/lovelace-engine/tree/v3.0.0) (2021-03-24)

[Full Changelog](https://github.com/project-lovelace/lovelace-engine/compare/v2.0...v3.0.0)

**Fixed bugs:**

- Engine stalls when submitted code returns None. [\#19](https://github.com/project-lovelace/lovelace-engine/issues/19)

**Closed issues:**

- Switch from running code in LXC to Docker? [\#59](https://github.com/project-lovelace/lovelace-engine/issues/59)
- Build script for lovelace-image [\#57](https://github.com/project-lovelace/lovelace-engine/issues/57)
- Multiple gunicorn workers [\#52](https://github.com/project-lovelace/lovelace-engine/issues/52)
- Turn into a real Python package? [\#51](https://github.com/project-lovelace/lovelace-engine/issues/51)
- Tiny optimization: lxc file pull all output pickles at once [\#47](https://github.com/project-lovelace/lovelace-engine/issues/47)
- Dynamic resources must all have different names [\#44](https://github.com/project-lovelace/lovelace-engine/issues/44)
- Document setting up lovelace-engine as a systemd service [\#38](https://github.com/project-lovelace/lovelace-engine/issues/38)
- Document symbolic links used [\#32](https://github.com/project-lovelace/lovelace-engine/issues/32)
- Improve Julia runner performance [\#24](https://github.com/project-lovelace/lovelace-engine/issues/24)
- Add support for C and C++ [\#20](https://github.com/project-lovelace/lovelace-engine/issues/20)
- Engine must run users’ programs in parallel [\#12](https://github.com/project-lovelace/lovelace-engine/issues/12)

**Merged pull requests:**

- Bump urllib3 from 1.26.2 to 1.26.3 [\#76](https://github.com/project-lovelace/lovelace-engine/pull/76) ([dependabot[bot]](https://github.com/apps/dependabot))
- Verify solutions from the engine [\#75](https://github.com/project-lovelace/lovelace-engine/pull/75) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Include input and user/expected output in test case details [\#74](https://github.com/project-lovelace/lovelace-engine/pull/74) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Delete Makefile [\#73](https://github.com/project-lovelace/lovelace-engine/pull/73) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Upgrade code runner to use Julia 1.5.3 [\#71](https://github.com/project-lovelace/lovelace-engine/pull/71) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Remove DockerHub badge [\#70](https://github.com/project-lovelace/lovelace-engine/pull/70) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Use secrets to deal with private solutions repo [\#69](https://github.com/project-lovelace/lovelace-engine/pull/69) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Nuke all remnants of LXC/LXD! [\#68](https://github.com/project-lovelace/lovelace-engine/pull/68) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Switch to GitHub Actions CI [\#67](https://github.com/project-lovelace/lovelace-engine/pull/67) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Cleanup [\#66](https://github.com/project-lovelace/lovelace-engine/pull/66) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Add Travis and Docker Hub badges [\#65](https://github.com/project-lovelace/lovelace-engine/pull/65) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Use docker containers instead of lxc/lxd [\#64](https://github.com/project-lovelace/lovelace-engine/pull/64) ([benallan](https://github.com/benallan))
- Refactor engine tests to use pytest [\#63](https://github.com/project-lovelace/lovelace-engine/pull/63) ([benallan](https://github.com/benallan))
- Faster julia runner [\#62](https://github.com/project-lovelace/lovelace-engine/pull/62) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Add test case to verify\_user\_solution call [\#60](https://github.com/project-lovelace/lovelace-engine/pull/60) ([benallan](https://github.com/benallan))
- Bash script to build lovelace lxc image from scratch [\#58](https://github.com/project-lovelace/lovelace-engine/pull/58) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Dockerizing the engine [\#54](https://github.com/project-lovelace/lovelace-engine/pull/54) ([ali-ramadhan](https://github.com/ali-ramadhan))
- C support [\#53](https://github.com/project-lovelace/lovelace-engine/pull/53) ([ali-ramadhan](https://github.com/ali-ramadhan))

## [v2.0](https://github.com/project-lovelace/lovelace-engine/tree/v2.0) (2019-07-22)

[Full Changelog](https://github.com/project-lovelace/lovelace-engine/compare/v1.1...v2.0)

**Fixed bugs:**

- I think engine forgets to delete dynamic resources [\#36](https://github.com/project-lovelace/lovelace-engine/issues/36)

**Closed issues:**

- Merge the different runners? [\#46](https://github.com/project-lovelace/lovelace-engine/issues/46)
- `make test` should glob for \*.py files [\#34](https://github.com/project-lovelace/lovelace-engine/issues/34)
- Do not disable existing loggers when using logging.ini to configure a logger [\#42](https://github.com/project-lovelace/lovelace-engine/issues/42)
- Performance benchmarking [\#28](https://github.com/project-lovelace/lovelace-engine/issues/28)
- Execute test cases in batches [\#25](https://github.com/project-lovelace/lovelace-engine/issues/25)
- Engine should store temporary files in /tmp [\#22](https://github.com/project-lovelace/lovelace-engine/issues/22)

**Merged pull requests:**

- Actually do something if user returns None [\#49](https://github.com/project-lovelace/lovelace-engine/pull/49) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Merge runners into a single CodeRunner [\#48](https://github.com/project-lovelace/lovelace-engine/pull/48) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Faster engine that executes test cases all at once [\#45](https://github.com/project-lovelace/lovelace-engine/pull/45) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Show user an error when no code is provided [\#43](https://github.com/project-lovelace/lovelace-engine/pull/43) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Cleanup on\_post and simple\_lxd [\#41](https://github.com/project-lovelace/lovelace-engine/pull/41) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Better errors [\#39](https://github.com/project-lovelace/lovelace-engine/pull/39) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Bypass TEST\_CASE\_TYPE\_ENUM global const for problem modules [\#37](https://github.com/project-lovelace/lovelace-engine/pull/37) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Properly glob files to feed into engine [\#35](https://github.com/project-lovelace/lovelace-engine/pull/35) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Time tests for performance benchmarking [\#31](https://github.com/project-lovelace/lovelace-engine/pull/31) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Select between dev and production paths [\#29](https://github.com/project-lovelace/lovelace-engine/pull/29) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Julia support [\#18](https://github.com/project-lovelace/lovelace-engine/pull/18) ([ali-ramadhan](https://github.com/ali-ramadhan))

## [v1.1](https://github.com/project-lovelace/lovelace-engine/tree/v1.1) (2019-01-04)

[Full Changelog](https://github.com/project-lovelace/lovelace-engine/compare/v1.0...v1.1)

**Closed issues:**

- Add support for Julia [\#13](https://github.com/project-lovelace/lovelace-engine/issues/13)
- Augment the Python Runner with the ability to use either Python 2 or 3 [\#10](https://github.com/project-lovelace/lovelace-engine/issues/10)
- Set up automated deployment of the Engine [\#6](https://github.com/project-lovelace/lovelace-engine/issues/6)

## [v1.0](https://github.com/project-lovelace/lovelace-engine/tree/v1.0) (2018-11-26)

[Full Changelog](https://github.com/project-lovelace/lovelace-engine/compare/a61bdfecd254ddc1134e193a6ef4a7c3e314f2d8...v1.0)

**Closed issues:**

- Add support for Fortran [\#14](https://github.com/project-lovelace/lovelace-engine/issues/14)
- Engine must run users' code securely [\#11](https://github.com/project-lovelace/lovelace-engine/issues/11)
- Setup a custom global logger. [\#8](https://github.com/project-lovelace/lovelace-engine/issues/8)
- Accurate reporting of CPU time and RAM usage by the engine. [\#7](https://github.com/project-lovelace/lovelace-engine/issues/7)
- As a user, I want my submissions to undergo static Python code analysis. [\#5](https://github.com/project-lovelace/lovelace-engine/issues/5)
- As a developer, I would like to have a Makefile to automate setting up my development environment   [\#4](https://github.com/project-lovelace/lovelace-engine/issues/4)
- Allow engine clients to send code for execution [\#3](https://github.com/project-lovelace/lovelace-engine/issues/3)
- Decide: what kind of format should we use for inputs and outputs? [\#2](https://github.com/project-lovelace/lovelace-engine/issues/2)
- Decide: should we expect submitted code to read input from a file, command line, or both? [\#1](https://github.com/project-lovelace/lovelace-engine/issues/1)

**Merged pull requests:**

- Alpha2018 [\#17](https://github.com/project-lovelace/lovelace-engine/pull/17) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Secure code execution via lxc [\#16](https://github.com/project-lovelace/lovelace-engine/pull/16) ([ali-ramadhan](https://github.com/ali-ramadhan))
- Small fixes to get the Engine to run in production [\#15](https://github.com/project-lovelace/lovelace-engine/pull/15) ([basimr](https://github.com/basimr))
- Automated virtual env setup for development with a Makefile [\#9](https://github.com/project-lovelace/lovelace-engine/pull/9) ([basimr](https://github.com/basimr))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
