# changelog
Create a changelog file from all the merged pull requests

## Usage
Install with pip (only do it once):
````
git clone git@github.com:neuropoly/changelog.git .
cd changelog
pip install -e .
````
Then you can use changelog from anywhere:
````
changelog --repo-url <user/repo> [--log-level <LEVEL> --token <github_api_personal_token>]
````

where:
- `--repo_url` (mandatory) is the url of the repository (e.g. `neuropoly/spinalcordtoolbox`)
- `--log-level` (optional) is the logging level as per python logging docs (e.g. INFO, DEBUG, etc)
- `--token` (optional) is your personal access token which was generated via your github account (see https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token). Making authenticated requests increases the API rate limits for some resources.

The script will produce a `[user]_[repo]_changelog.[tagId].md` file with changelog contents. The contents can then be verified manually and copied over to the respective project `CHANGES.md` file.

Contributions are welcome (via a fork of the repository and pull request) 🎉 
