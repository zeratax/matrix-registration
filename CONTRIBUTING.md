# CONTRIBUTING
## Code of Conduct
See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
## How Can I Contribute?
### Issues
Filling issues is a great and easy way to help find bugs and get new features implemented.
#### Bugs
If you're reporting a security issue, please email me at security@zera.tax, otherwise
if you're reporting a bug, please fill out this [form](https://github.com/ZerataX/matrix-registration/issues/new?labels=bug&template=bug_report.md).
#### Feature Requests
If you have an idea for a new feature or an enhancement, please fill out this [form](https://github.com/ZerataX/matrix-registration/issues/new?labels=enhancement&template=feature_request.md).
#### Translations
You can translate the registration page over at https://l10n.dmnd.sh/engage/matrix-registration/

[![Translation status](https://l10n.dmnd.sh/widgets/matrix-registration/-/open-graph.png)](https://l10n.dmnd.sh/engage/matrix-registration/)

#### Getting Started

To begin working on translating with WebLate, you will need to create an account linked to your GitHub account. From there, you'll be able to see a list of currently translated languages as well as incomplete lines.


If you have any further questions about how to contribute, please make an issue on the GitHub page.


### Pull Requests

Every PR should not break tests and ideally include tests for added functionality.
Also it is recommend to follow the [PEP8](https://www.python.org/dev/peps/pep-0008/) styleguide
#### Setting up the Project

```bash
git clone https://github.com/ZerataX/matrix-registration.git
cd matrix-registration

virtualenv -p /usr/bin/python3.6 .
source ./bin/activate

python setup.py develop
cp config.sample.yaml config.yaml
```

and edit config.yaml

You can run tests by executing the following command in the project root
```bash
python setup.py test
```


