![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/lukzmu/personal-website/pages.yml)
![Codecov](https://img.shields.io/codecov/c/github/lukzmu/personal-website)
![GitHub](https://img.shields.io/github/license/lukzmu/personal-website)

# Personal Website

Personal website written using Python thanks to the Pelican package.

The deployment is done through Github Actions and posted on GitHub Pages.

## Requirements

- [mise](https://github.com/jdx/mise)

## Environment Variables

| **Variable** | **Description** |
| :--- | :--- |
| `SITEURL` | The url of the final website |
| `GH_TOKEN` | GitHub personal access token for projects |

## Useful commands

| **Action** | **Command** |
| :--- | :--- |
| Install dependencies and hooks | `mise run bootstrap` |
| Build the project | `mise run build` |
| Run the project | `mise run serve` |
| Format project | `mise run lint_fix` |
| Lint project | `mise run lint` |
| Test project | `mise run test` |
