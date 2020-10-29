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
usage: changelog.py [-h] [--log-level LOG_LEVEL] [--update] [--name NAME] repo-url

Changelog generator script

required arguments:
  repo-url              Repository url in the format <GITHUB_USER/REPO_NAME>. Example: neuropoly/spinalcordtoolbox

optional arguments:
  -h, --help            show this help message and exit
  --log-level LOG_LEVEL Logging level (eg. INFO, see Python logging docs)
  --update              Update an existing changelog file by prepending current changelog to it.
  --name NAME           Existing changelog file to use (by default use CHANGES.md).


````

### Examples
```
# create a new changelog file [user]_[repo]_changelog.[tagId].md for spinalcordtoolbox
changelog neuropoly/spinalcordtoolbox

# prepend to an existing CHANGES.md file (default)
changelog neuropoly/spinalcordtoolbox --update

# prepend to an existing CUSTOM_CHANGELOG.md
changelog neuropoly/spinalcordtoolbox --update --name CUSTOM_CHANGELOG.md

# run in debug
changelog neuropoly/spinalcordtoolbox --log-level DEBUG
```

To use a Github Personal Access Token (https://github.com/settings/tokens) simply export the token string via the `GITHUB_TOKEN` environment variable.

Unless `--update` is passed, the script will produce a `[user]_[repo]_changelog.[tagId].md` file with changelog contents.

Contributions are welcome (via a fork of the repository and pull request) 🎉
