# GitHub Repository Audit Tool

The audit dashboard provides a _declarative_ approach to managing repository changes over time for current and future projects in a GitHub organization. It's built using [Streamlit](https://www.streamlit.io) and can be [configured](https://github.com/siegerts/github-repository-audit/blob/main/audit_config.toml) for multiple organizations and repositories within those organizations.

#### Repo meta

![](https://github.com/siegerts/github-repository-audit/blob/main/audit-dashboard.png)

#### Labels

![](https://github.com/siegerts/github-repository-audit/blob/main/audit-labels.png)

## Focus areas

### Repository meta information

- Homepage link
- Code Of Conduct
- Code Of Conduct File
- Contributing
- Pull Request Template
- License
- Readme

### Marketing and Discoverability

GitHub topics help with marketing and discoverability for a repository. Also, ensure that certain topics are present.

### Consistent core label set

The expectation is that the label set may change over time which will be captured through the audit process.

- Present - standardize names, colors, and descriptions
- Missing - identify similar labels for adjustment and not present
- Deprecated - stop using and transition away

### Open for contribution indicators

_Provide entry points for open source contributions._

In GitHub, issues labeled with `good first issue` indicate to open source contributors that the contribution requires a lower barrier to entry.

- `good first issue`
- `question`

### Automation & Ops utilities

Utilities and configurations to help develop consistency in communication and expectations across repositories.

- Code Owners
- Issue templates
  - Examples can be found in the Amplify CLI repo ([issue](https://github.com/aws-amplify/amplify-cli/issues/new?assignees=&labels=&template=1.bug_report.yaml), [feature-request](https://github.com/aws-amplify/amplify-cli/issues/new?assignees=&labels=feature-request&template=2.feature_request.yaml))
- Suggested GH Actions

## Getting started & development

1. Create a Python virtual environment.

Using `pyenv`:

```
pyenv virtualenv github-repository-audit
```

2. Activate the virtual environment

```
pyenv activate github-repository-audit
```

3. Install the dependencies from `requirements.txt`

```
pip install -r requirements.txt
```

4. Add a GitHub token in the `.env` file
5. Update the `audit_config.toml` file
6. Run `streamlit run app.py`

## Configuration options

The following configurations can be set adjusted in the `audit_config.toml`.

| Name                | Description                                               | Example                                                                                                  |
| ------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `deprecated_labels` | Existing labels that are no longer used                   | `["enhancement"]`                                                                                        |
| `required_topics`   | Required repository marketing topics                      | `["aws-amplify"]`                                                                                        |
| `topics`            | Additional topic suggestions                              | `["aws-amplify","serverless",]`                                                                          |
| `repo_health_items` | Settings and files that help facilitate OSS contributions | `["code_of_conduct","code_of_conduct_file","contributing","pull_request_template","license","readme", ]` |

### Organizations & repos

For example:

```
[[orgs]]
name = "aws-amplify"
[[orgs.repositories]]
name = "amplify-cli"
label = "CLI"

[[orgs.repositories]]
name = "amplify-js"
label = "JS"

[[orgs.repositories]]
name = "amplify-ui"
label = "UI"
```

### Required labels

For example:

```
[[labels]]
label = "transferred"
color = "f9d0c4"
description = "This issue was transferred from another Amplify project"

[[labels]]
label = "question"
color = "cc317c"
description = "General question"

[[labels]]
label = "feature-request"
color = "6f8dfc"
description = "Request a new feature"
```

## Deployment options

Any example `Dockerfile` can be used as a starting point to deploy as a container. A few options include.

- [AWS Copilot](https://aws.github.io/copilot-cli/)
- [AWS Amplify Serverless Containers](https://docs.amplify.aws/cli/usage/containers/)
