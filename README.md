# GitHub Repository Audit Tool

The audit dashboard provides a _declarative_ approach to managing repository changes over time for current and future projects in a GitHub organization.

![](https://github.com/siegerts/github-repository-audit/blob/main/audit-dashboard.png)

## Repository meta information

- Homepage link
- Code Of Conduct
- Code Of Conduct File
- Contributing
- Pull Request Template
- License
- Readme

## Marketing and Discoverability

GitHub topics help with marketing and discoverability for a repository. Also, ensure that certain topics are present.

## Consistent core label set

The expectation is that the label set may change over time which will be captured through the audit process.

- Present - standardize names, colors, and descriptions
- Missing - identify similar labels for adjustment and not present
- Deprecated - stop using and transition away

## Open for contribution indicators

_Provide entry points for open source contributions._

In GitHub, issues labeled with `good first issue` indicate to open source contributors that the contribution requires a lower barrier to entry.

- good first issue
- question

## Automation & Ops utilities

Utilities and configurations to help develop consistency in communication and expectations across repositories.

- Code Owners
- Issue templates
  - Examples can be found in the Amplify CLI repo (issue (https://github.com/aws-amplify/amplify-cli/issues/new?assignees=&labels=&template=1.bug_report.yaml), feature request (https://github.com/aws-amplify/amplify-cli/issues/new?assignees=&labels=feature-request&template=2.feature_request.yaml))
- Suggested GH Actions

## Development

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

5 .Update the `audit_config.toml` file

6. Run `streamlit run app.py`
