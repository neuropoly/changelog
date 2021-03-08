    #!/usr/bin/env python
import sys
import io
import os
import logging
import datetime
import argparse

import requests

logger = logging.getLogger(__name__)


class GithubAPI(object):
    """
    Simple wrapper around the github API that respects rate limiting and supports authentication.
    """

    def __init__(self, repo_url):
        self._token = os.environ.get('GITHUB_TOKEN', None)
        self.repo_url = repo_url
        self.api_url_prefix = "https://api.github.com"
        self.check_rate_limit()

    def check_rate_limit(self):
        """
        API limits reset every hour so there is no point in spacing the requests over time
        as the delays will make the script unuseable. Instead check monitor the requests
        remaining and notify user accordingly.
        It is recommended to use a PAT (personal access token) as this will increase the api
        limit for some resources.
        """
        logger.info("Checking API rate limits:")

        url = f"{self.api_url_prefix}/rate_limit"
        r = self.request(url).json()

        logger.debug(f"rate_limits: {r}")

        core_api = r['resources']['core']
        search_api = r['resources']['search']

        logger.info(f"Core api limit={core_api['limit']} remaining={core_api['remaining']} reset={datetime.datetime.fromtimestamp(core_api['reset'])}")
        logger.info(f"Search api limit={search_api['limit']} remaining={search_api['remaining']} reset={datetime.datetime.fromtimestamp(search_api['reset'])}")

        if core_api['remaining'] == 0:
            raise ValueError(f"Core API limit reached! Retry at {datetime.datetime.fromtimestamp(core_api['reset'])}")

        if search_api['remaining'] == 0:
            raise ValueError(f"Search API limit reached! Retry at {datetime.datetime.fromtimestamp(search_api['reset'])}")

    def request(self, url, method="GET", headers=None, params=None, data=None):
        headers = headers or {}
        if self._token is not None:
            headers['Authorization'] = f"token {self._token}"
        headers['Accept'] = 'application/json'

        def callback(response, *args, **kwargs):
            if not response.ok:
                logger.error(f"Got a non 200 code from server: {response.status_code}: {response.json()}")
                raise RuntimeError(response.status_code, response.json())

            limit = response.headers.get('X-RateLimit-Limit')
            remaining = response.headers.get('X-RateLimit-Limit')
            reset = response.headers.get('X-RateLimit-Reset')

            logger.debug(f"api rate limit stats: limit={limit}, remaining={remaining}, reset={datetime.datetime.fromtimestamp(int(reset))}")

            if remaining == 0:
                raise ValueError(f"API limit reached! Retry at {datetime.datetime.fromtimestamp(reset)} or use an authentication token!")

        return requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            hooks={'response': callback}
        )

    def fetch_open_milestones(self):
        """
        Fetch list of milestone dicts. Each dict contains metadata about an open milestone.
        """
        url = f"{self.api_url_prefix}/repos/{self.repo_url}/milestones"
        open_milestones = self.request(url).json()
        if not open_milestones:
            raise ValueError("No open milestone was found on github.")
        logger.debug(f"Open milestones found: {open_milestones}")
        return open_milestones

    def get_most_recently_updated_milestone(self):
        """
        Get info about the most recently updated milestone.
        """
        open_milestones = self.fetch_open_milestones()
        milestone = sorted(open_milestones, key=lambda m: m['updated_at'])[-1]
        logger.info(f"Using most recently updated milestone: '{milestone['title']}'")
        return milestone

    def get_milestone(self, requested_title: str = None):
        """
        Get info about an open milestone (specified by name).
        """
        open_milestones = self.fetch_open_milestones()
        milestone = next((m for m in open_milestones if m["title"] == requested_title), None)
        if milestone:
            logger.info(f"Requested milestone '{requested_title}' found in open milestones.")
        else:
            raise ValueError(f"Requested milestone '{requested_title}' not found. "
                             f"Available milestones: {[m['title'] for m in open_milestones]}.")
        return milestone

    def get_tags_compare_url(self, new_tag):
        """
        Return the Github URL comparing the last tag with the new_tag.
        """
        url = f"{self.api_url_prefix}/repos/{self.repo_url}/releases"
        r = self.request(url).json()
        previous_tag = r[0]['tag_name']
        return f"https://github.com/{self.repo_url}/compare/{previous_tag}...{new_tag}"

    def search(self, milestone, label=None):
        """
        Return a list of merged pull requests linked to the milestone and label provided.
        """
        url = f"{self.api_url_prefix}/search/issues"
        query = f'milestone:"{milestone}" is:pr repo:{self.repo_url} state:closed is:merged'
        if label:
            query += f' label:{label}'
        else:
            query += f' no:label'
        payload = {'q': query}
        r = self.request(url=url, params=payload).json()
        logger.info(f"Milestone: {milestone}, Label: {label}, Count: {r['total_count']}")
        return r

def get_custom_options(repo):
    """
    If repo has customizations defined for changelog use them, otherwise use defaults.
    """
    if not repo in options:
        repo = 'default'

    generator, labels = options[repo]['generator'], options[repo]['labels']
    return generator, labels

def default_changelog_generator(item):
    """
    Contruct the default changelog line for a given item (PR).
    """
    title = item['title']
    breaks_compat = 'compatibility' in item['labels']
    pr_url = item['html_url']

    if breaks_compat:
        compat_msg = "**WARNING: Breaks compatibility with previous version.**"
    else:
        compat_msg = ""

    return f" - {title}. {compat_msg} [View pull request]({pr_url})"

def sct_changelog_generator(item):
    """
    Custom changelog line generator for sct project.
    """

    def get_sct_function_from_label(labels=[]):
        labels_list = []
        for label in labels:
            if "sct_" in label['name']:
                labels_list.append(label['name'])
        return labels_list

    title = item['title']
    sct_labels = get_sct_function_from_label(item['labels'])
    breaks_compat = 'compatibility' in item['labels']
    pr_url = item['html_url']

    if breaks_compat:
        compat_msg = "**WARNING: Breaks compatibility with previous version.**"
    else:
        compat_msg = ""

    if sct_labels:
        return f" - **{','.join(label for label in sct_labels)}:** {title}. {compat_msg} [View pull request]({pr_url})"
    else:
        return f" - {title}. {compat_msg} [View pull request]({pr_url})"

def get_parser():

    parser = argparse.ArgumentParser(
        description="Changelog generator script",
        add_help=False,
    )

    mandatory = parser.add_argument_group("required arguments")
    mandatory.add_argument("repo-url",
        help="Repository url in the format <GITHUB_USER/REPO_NAME>. Example: neuropoly/spinalcordtoolbox",
    )

    optional = parser.add_argument_group('optional arguments')
    optional.add_argument("-h", "--help", action="help", help="show this help message and exit")

    optional.add_argument("--log-level",
        default="INFO",
        help="Logging level (eg. INFO, see Python logging docs)",
    )

    optional.add_argument("--update",
        action='store_true',
        help="Update an existing changelog file by prepending to it.",
    )

    optional.add_argument("--name",
        type=str,
        default='CHANGES.md',
        help="Existing changelog file to use.",
    )

    optional.add_argument(
        "--milestone",
        type=str,
        help="Name of milestone to generate changelog for. If not provided, the most recently updated milestone is "
             "used instead."
    )

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=args.log_level, format="%(levelname)s %(message)s")

    repo_url = getattr(args, 'repo-url')
    api = GithubAPI(repo_url=repo_url)
    user, repo = repo_url.split('/')

    if args.milestone is not None:
        milestone = api.get_milestone(args.milestone)
    else:
        milestone = api.get_most_recently_updated_milestone()
    tag = milestone['title'].split()[-1]

    lines = [
        f"## {tag} ({datetime.date.today()})",
        f"[View detailed changelog]({api.get_tags_compare_url(tag)})"
    ]

    changelog_pr = set()
    generator, labels = get_custom_options(repo)

    for label in labels:
        pull_requests = api.search(milestone['title'], label)
        items = pull_requests.get('items')
        if items:
            if label:
                lines.append(f"\n**{label.upper()}**\n")
            changelog_pr = changelog_pr.union(set([x['html_url'] for x in items]))
            for x in pull_requests.get('items'):
                items = [ generator(x) ]
                lines.extend(items)

    logger.info('Total number of pull requests with label: %d', len(changelog_pr))
    all_pr = set([x['html_url'] for x in api.search(milestone['title'])['items']])
    diff_pr = all_pr - changelog_pr
    for diff in diff_pr:
        logger.warning('Pull request not labeled: %s', diff)

    if args.update:
        filename = args.name
        if not os.path.exists(filename):
            raise IOError(f"The provided changelog file: {filename} does not exist!")

        with io.open(filename, 'r') as f:
            original = f.readlines()

        backup = f"{filename}.bak"
        os.rename(filename, backup)

        with io.open(filename, 'w') as changelog:
            # re-use first line from existing file since it most likely contains the title
            changelog.write(original[0] + '\n')

            # write current changelog
            changelog.write('\n'.join(lines))
            changelog.write('\n')

            # write back rest of changelog
            changelog.writelines(original[1:])

        logger.info(f"Backup created: {backup}")

    else:
        filename = f"{user}_{repo}_changelog.{milestone['number']}.md"
        with io.open(filename, "w") as changelog:
            changelog.write('\n'.join(lines))

    logger.info(f"Changelog written into {filename}")


# provides customization to changelog for some repos
options = {
    'default': {
        'labels': [None],
        'generator': default_changelog_generator,
    },
    'spinalcordtoolbox': {
        'labels': ['feature', 'documentation-internal', 'CI', 'bug', 'installation', 'documentation', 'enhancement', 'refactoring', 'git/github'],
        'generator': sct_changelog_generator,
    },
    'ivadomed': {
        'labels': ['bug', 'dependencies', 'documentation', 'enhancement'],
        'generator': default_changelog_generator,
    },
    'axondeepseg': {
        'labels': ['bug', 'enhancement', 'feature', 'documentation', 'installation', 'testing'],
        'generator': default_changelog_generator,
    }
}

if __name__ == '__main__':
    raise SystemExit(main())
