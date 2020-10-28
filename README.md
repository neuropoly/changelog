# changelog
Create a changelog file from all the merged pull requests

## Usage
Install with pip (only do it once):

### Standard install
```
pip install changelog-neuropoly
```

### Development install
````
git clone git@github.com:neuropoly/changelog.git .
cd changelog
pip install -e .
````

Then you can use changelog from anywhere:
````
changelog --repo-url <user/repo> [--log-level <LEVEL>]
````

where:
- `--repo_url` (mandatory) is the url of the repository (e.g. `neuropoly/spinalcordtoolbox`)
- `--log-level` (optional) is the logging level as per python logging docs (e.g. INFO, DEBUG, etc)

To use a Github Personal Access Token (https://github.com/settings/tokens) simply export the token string via the `GITHUB_TOKEN` environment variable.

The script will produce a `[user]_[repo]_changelog.[tagId].md` file with changelog contents. The contents can then be verified manually and copied over to the respective project `CHANGES.md` file.

Contributions are welcome (via a fork of the repository and pull request) 🎉
