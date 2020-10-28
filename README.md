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
usage: changelog.py [-h] [--log-level LOG_LEVEL] repo-url

Changelog generator script

required arguments:
  repo-url               Repository url in the format <GITHUB_USER/REPO_NAME>. Example: neuropoly/spinalcordtoolbox

optional arguments:
  -h, --help             show this help message and exit
  --log-level LOG_LEVEL  Logging level (eg. INFO, see Python logging docs)
````

To use a Github Personal Access Token (https://github.com/settings/tokens) simply export the token string via the `GITHUB_TOKEN` environment variable.

The script will produce a `[user]_[repo]_changelog.[tagId].md` file with changelog contents. The contents can then be verified manually and copied over to the respective project `CHANGES.md` file.

Contributions are welcome (via a fork of the repository and pull request) 🎉
