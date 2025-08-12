![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/lukzmu/personal-website/pages.yml)
![Codecov](https://img.shields.io/codecov/c/github/lukzmu/personal-website)
![GitHub](https://img.shields.io/github/license/lukzmu/personal-website)

# Personal Website

Personal website written using Python thanks to the Pelican package.

The deployment is done through Github Actions and posted on GitHub Pages.

## Requirements

- Python 3.13
- [uv package](https://github.com/astral-sh/uv)

## Environment Variables

| **Variable** | **Description** |
| :--- | :--- |
| `SITEURL` | The url of the final website |
| `GH_TOKEN` | GitHub personal access token for projects |

## Useful commands

| **Action** | **Command** |
| :--- | :--- |
| Build the project | `uv run poe build` |
| Run the project | `uv run poe serve` |
| Format project | `uv run poe lint_fix` |
| Lint project | `uv run poe lint` |
| Test project | `uv run poe test` |
