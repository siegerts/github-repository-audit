import base64
import difflib
import os
from typing import Any

import pandas as pd
import streamlit as st
import toml
from dotenv import load_dotenv

from github import GitHubAPI
from utils import swatch

config = toml.load("audit_config.toml")
load_dotenv()

token = os.getenv("GH_TOKEN")
deployed = bool(os.getenv("DEPLOYED", False))

if token is None:
    raise ValueError("GH_TOKEN not found in .env")

gh = GitHubAPI(token=token)

orgs = config.get("orgs", [])

common_topics = config.get("topics", [])
common_topics.sort()

required_labels = config.get("labels", [])
required_labels.sort(key=lambda label: label["label"])

deprecated_labels = config.get("deprecated_labels", [])
deprecated_labels.sort()

if deployed:
    # hide menu
    hide_menu_style = """
        <style>
            #MainMenu {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


###################
#      Sidebar    #
###################

selected_org = st.sidebar.selectbox(
    "Select GitHub organization", [org["name"] for org in orgs]
)

repositories = []
for idx, org in enumerate(orgs):
    if org["name"] == selected_org:
        repositories = orgs[idx]["repositories"]
        break

selected_repo: Any = st.sidebar.selectbox(
    "Select repository", repositories, format_func=lambda x: x["label"]
)

repo = selected_repo["name"] or ""


###################
#      Main       #
###################

if selected_org and repo:

    ###################
    #      Heading    #
    ###################

    st.title("GitHub Repository Health 📊")
    st.markdown("---")

    repo_meta: pd.DataFrame = gh.get_repo(selected_org, repo)
    repo_name: str = repo_meta["name"].values[0] or ""

    st.header(repo_name)

    repo_description = repo_meta["description"].values[0]

    if repo_description and repo_description != "None":
        st.write(repo_description)
    else:
        st.markdown("🚨 There isn't a description stated in this repo.")

    try:
        repo_license: str = repo_meta["license.name"].values[0] or ""

        if repo_license.lower() == "other":
            repo_license += " (Check License file linked below)"
        st.write(repo_license)
    except KeyError:
        st.markdown("🚨 There isn't a license file in this repo.")

    ###################
    #      Health     #
    ###################

    st.subheader("Repo health")
    health = gh.get_repo_health(selected_org, repo)

    # issue_template identified in Ops section
    repo_health_items = config.get("repo_health_items", [])

    if repo_meta["homepage"].values[0]:
        st.markdown(f"✅ [Homepage link]({repo_meta['homepage'].values[0]})")
    else:
        st.markdown(f"🚨 **Missing** Homepage link")

    for item in repo_health_items:
        it = health["files"].get(item, None)
        if it:
            st.markdown(f"✅ [{item.replace('_',' ').title()}]({it['html_url']})")
        else:
            st.markdown(f"🚨 **Missing** {item.replace('_',' ').title()}")

    ###################
    # Discoverability #
    ###################

    st.subheader("Topics")

    topics: list = sorted(gh.get_repo_topics(selected_org, repo).values[0].tolist()[0])

    expander = st.expander("Classifying your repository with topics")

    expander.markdown(
        """
    [Classifying your repository with topics](https://docs.github.com/en/github/administering-a-repository/managing-repository-settings/classifying-your-repository-with-topics)\n \
    > To help other people find and contribute to your project, you can add topics to your repository related to your project's intended purpose, subject area, affinity groups, or other important qualities.\n
    """
    )

    required_topics = config.get("required_topics", [])
    topic_suggestions = ""
    missing_topics = set(required_topics) - set(topics)

    if missing_topics:
        topic_suggestions = f"The project is missing the following topic(s): {(', ').join(missing_topics)}."

    if len(topics) < 6:
        topic_suggestions += (
            "Consider adding some more topics to help make the project stand out."
        )

    if topics:
        st.info("The below topics are listed on the repository. " + topic_suggestions)
        st.write(", ".join(["`{}`".format(t) for t in topics]))
    else:
        st.error(
            f"""
    🚨 The repository **doesn't** have any topics listed.
    Some common topics across projects include {', '.join(['`{}`'.format(t) for t in common_topics])}...
    """
        )

    ##############
    #   Labels   #
    ##############

    st.header("Labels")

    labels = gh.get_repo_labels(selected_org, repo)[["name", "color", "description"]]

    st.markdown("\n\n")
    if st.checkbox("Display all repo labels"):
        st.write(labels)

    st.write(
        """
    These are the common labels required across all repositories.
    This ensures consistency for customers, contributors, and development team members interacting across projects.
    """
    )

    md = """
| Label | Color |  Status  | Needs updated |\n\
|-------|-------|----------|---------------|\n"""

    repo_labels = [label[0] for label in labels.values]
    req_labels = [label["label"] for label in required_labels]

    missing_labels = []
    present_labels = []

    for i, label in enumerate(req_labels):
        try:
            idx = repo_labels.index(label)
            present_labels.append(required_labels[i])

        except ValueError:
            idx = None
            missing_labels.append(required_labels[i])

        if idx:
            notes = ""
            color_flag = (
                labels.values[idx][1].lower() != required_labels[i]["color"].lower()
            )

            if color_flag:
                notes += f"Color needs changed to **{required_labels[i]['color'].lower()}**. "

            desc_flag = labels.values[idx][2] != required_labels[i]["description"]

            if desc_flag:
                notes += f"Description needs changed to **{required_labels[i]['description']}**."

            flag = color_flag or desc_flag

            md += f"|`{labels.values[idx][0]}`"
            md += f"|{swatch(labels.values[idx][1])}"
            md += f"| {'✔️' if not flag else '⚠️'}"
            md += f"| <small>{notes}</small> |\n"

    if present_labels:
        st.markdown("\n\n")
        st.subheader("Present")

        if not missing_labels:
            st.success("All required labels are present.")

        st.markdown(md, unsafe_allow_html=True)

    if missing_labels:
        st.markdown("\n\n")
        st.subheader("Missing")
        st.error("🚨 The following required labels are missing in the repository.")
        st.markdown(
            """
            Similar labels may already exist (i.e. **In Repo**) in the project. If present, adjust the existing label(s) to map to the required label.
            The label update will propagate to all issues tagged with that labels reference.
        """
        )
        missing_md = """
    | Label | Swatch | Color | Description | In Repo |\n\
    |-------|--------|-------|-------------|---------|\n"""

        for label in missing_labels:
            similar = [
                f"`{l}`"
                for l in difflib.get_close_matches(
                    label["label"], repo_labels, cutoff=0.8
                )
            ]

            missing_md += f"| `{label['label']}` |{swatch(label['color'])} | {label['color'].lower()} | <small>{label['description']}</small> | <small>{' ,'.join(similar)}</small>\n"

        st.markdown(missing_md, unsafe_allow_html=True)

    deprecated = set(repo_labels) & set(deprecated_labels)

    if deprecated:
        st.markdown("\n\n")
        st.subheader("Deprecated")
        st.warning(
            "🚨 The following required labels are deprecated. Transition away from use before deleting."
        )
        st.write(f"`{', '.join(set(repo_labels) & set(deprecated_labels))}`")

    ##########################
    # Open for contribution  #
    ##########################

    st.markdown("\n\n")
    st.subheader("Open for contribution")
    st.markdown(
        f"""
    Why is the `good first issue` label so important? GitHub _automatically_ creates a contributor page for each repo. Issues with this label are used to populate this page.

    [View the {repo} GitHub Contributor page](https://github.com/{selected_org}/{repo}/contribute).

    Is it welcoming to a new contributor to the project?

    """
    )

    st.markdown("\n")
    st.markdown(
        """
    _More about [Good First Issues](https://github.blog/2020-01-22-browse-good-first-issues-to-start-contributing-to-open-source/)._
    """
    )

    contrib_md = """
| Label | Issue Count |\n \
|-------|-------------|\n"""

    contrib_labels = gh.get_open_for_contrib_issues(selected_org, repo, deployed)

    for k, v in contrib_labels.items():
        contrib_md += f"| `{k}` | {v} |\n"

    st.markdown(contrib_md)

    ###############
    #     Ops     #
    ###############

    st.markdown("\n\n\n")
    st.header("Automation & Ops")

    codeowners: list[str] = ["CODEOWNERS"]
    issue_templates: list[str] = ["ISSUE_TEMPLATE"]
    actions: list[str] = ["workflows"]

    ##############
    # Codeowners #
    ##############

    st.subheader("Codeowners")

    expander = st.expander("What are codeowners? 👉")
    expander.markdown(
        """
        [Code owners](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-repository-on-github/about-code-owners)
        are automatically requested for review when someone opens a pull request that modifies code that they own.
    """
    )

    for f in codeowners:
        fp = gh.get_repo_files(selected_org, repo, f)
        if fp:
            codeowners_present = True
            st.markdown(f"- {fp['html_url']}")
            message_bytes = base64.b64decode(fp["content"])
            raw = message_bytes.decode("ascii")
            st.write("Is this up to date?")
            st.code(raw)
        else:
            st.error("🚨 The CODEOWNERS configuration is missing.")

    ###################
    # Issue Templates #
    ###################

    st.subheader("Issue Templates")

    issue_forms_present = False
    issue_form_count = 0
    for f in issue_templates:
        fp = gh.get_repo_files(selected_org, repo, f)
        if fp:
            for item in fp:
                name = item["name"]

                if not name.startswith("config"):
                    issue_form_count += 1
                    if name.endswith(".yml") or name.endswith(".yaml"):
                        issue_forms_present = True

                st.markdown(f"- [{name}]({item['html_url']})")

    if issue_form_count < 2:
        st.error(
            """
            🚨 There may be missing forms and/or templates in the repo. A form for each is nescessary:
            - Issues
            - Feature Requests
        """
        )

    if not issue_forms_present:
        issue_forms_msg = "🚨 Consider using structured issue forms for this 👉"
    else:
        issue_forms_msg = "✅ It looks like structured issue forms exist 👉"

    expander = st.expander(issue_forms_msg)
    expander.markdown(
        """
        [Structured issue forms](https://gh-community.github.io/issue-template-feedback/welcome/) \
        are available in all **public** GitHub repos.

        Examples can be found in the Amplify CLI repo ([issue](https://github.com/aws-amplify/amplify-cli/issues/new?assignees=&labels=&template=1.bug_report.yaml),
        [feature request](https://github.com/aws-amplify/amplify-cli/issues/new?assignees=&labels=feature-request&template=2.feature_request.yaml))

    """
    )
