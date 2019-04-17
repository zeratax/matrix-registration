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


