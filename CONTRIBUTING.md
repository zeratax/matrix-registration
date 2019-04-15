# CONTRIBUTING
## Code of Conduct
## How Can I Contribute?
### Issues
#### Bugs
#### Feature Requests

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
```

You can run tests by executing the following command in the project root
```bash
python setup.py test
```


