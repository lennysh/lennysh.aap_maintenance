# How to Contribute

We welcome contributions. Here are a few ways you can help improve this collection.

## Open an Issue

If you see something you'd like changed, but aren't sure how to change it, submit an issue describing what you'd like to see.

## Working Locally

This collection has **no** external Ansible collection dependencies
(`collections/requirements.yml` is empty; modules use ansible-core + AAP REST).

Python's pre-commit tool can be installed, and hooks installed, to clean up whitespace, newlines, and run yamllint and ansible-lint against your local changes before committing. This will help you avoid failures in the GitHub workflows.

1. Create a local virtual environment (suggested).
2. Use pip to install pre-commit: `pip install pre-commit`
3. Install pre-commit hooks with `pre-commit install --install-hooks -c .pre-commit-config.yaml`
4. With hooks installed, they will be run automatically when you call `git commit`, blocking commit if any hooks fail.
5. [Optional] If you want to ignore hook failures and commit anyway, use `git commit -n`
6. [Optional] Run pre-commit checks at any time with `pre-commit run --all -c .pre-commit-config.yaml`.

Please see pre-commit documentation for further explanation: [Pre-commit](https://pre-commit.com/)

```bash
# Unit tests (no AAP required)
python3 -m unittest discover -s tests/unit -v
```

## Submit a Pull Request

1. Fork the repo on GitHub, and then clone it locally.
2. Create a branch named appropriately for the change you are going to make.
3. Make your code change.
4. When preparing a public release, add a changelog fragment in `changelogs/fragments` as per <https://docs.ansible.com/ansible/latest/community/development_process.html#changelogs> (not required for every private devel commit).
5. Push your code change up to your forked repo.
6. Open a Pull Request to merge your changes into this repo. The comment box will be filled in automatically via a template.
7. All Pull Requests are subject to Ansible and YAML linting checks. Please make sure that your code complies and fix any warnings that arise.
8. All Pull Requests are subject to testing.

See [Using Pull Requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) for more information on how to use GitHub PRs.

## Code of Conduct

As with all Ansible projects, we have a [Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html).
