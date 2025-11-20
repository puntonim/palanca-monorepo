<p align="center">
  <h1 align="center">
    Palanca monorepo: TradingView Client
  </h1>
  <p align="center">
    Just a basic client for TradingView un-official API.
  <p>
</p>

<br>

⚡ Usage
=======
See top docstrings in [tradingview_client.py](tradingview_client/tradingview_client.py).

Poetry install
--------------
From Github:
```sh
$ poetry add git+https://github.com/puntonim/palanca-monorepo#subdirectory=libs/tradingview-client
# at a specific version:
$ poetry add git+https://github.com/puntonim/palanca-monorepo@3da9603977a5e2948429627ac83309353cca693d#subdirectory=libs/tradingview-client
```

From a local dir:
```sh
$ poetry add ../palanca-monorepo/libs/tradingview-client
$ poetry add "tradingview-client @ file:///Users/myuser/workspace/palanca-monorepo/libs/tradingview-client"
```

Pip install
-----------
Same syntax as Poetry, but change `poetry add` with `pip install`.


🛠️ Development setup
====================

1 - System requirements
----------------------
**Python 3.10**\
The target Python 3.10 for a wide compatibility.\
Install it with pyenv:
```sh
$ pyenv install -l  # List all available versions.
$ pyenv install 3.10.16
```

**Poetry**\
Pipenv is used to manage requirements (and virtual environments).\
Read more about Poetry [here](https://python-poetry.org/). \
Follow the [install instructions](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions).

**Pre-commit**\
Pre-commit is used to format the code with black before each git commit:
```sh
$ pip install --user pre-commit
# On macOS you can also:
$ brew install pre-commit
```

2 - Virtual environment and requirements
----------------------------------------
Create a virtual environment and install all deps with one Make command:
```sh
$ make poetry-create-env
# Or to recreate:
$ make poetry-destroy-and-recreate-env
# Then you can activate the virtual env with:
$ eval $(poetry env activate)
# And later deactivate the virtual env with:
$ deactivate
```

Without using Makefile the full process is:
```sh
# Activate the Python version for the current project:
$ pyenv local 3.10  # It creates `.python-version`, to be git-ignored.
$ pyenv which python
/Users/nimiq/.pyenv/versions/3.10.16/bin/python

# Now create a venv with poetry:
$ poetry env use ~/.pyenv/versions/3.10.16/bin/python
# Now you can open a shell and/or install:
$ eval $(poetry env activate)
# And finally, install all requirements:
$ poetry install
# And later deactivate the virtual env with:
$ deactivate
```

To add new requirements:
```sh
$ poetry add requests

# Dev or test only.
$ poetry add -G test pytest
$ poetry add -G dev ipdb

# With extra reqs:
$ poetry add -G dev "aws-lambda-powertools[aws-sdk]"
$ poetry add "requests[security,socks]"

# From Git:
$ poetry add git+https://github.com/aladagemre/django-notification

# From a Git subdir:
$ poetry add git+https://github.com/puntonim/utils-monorepo#subdirectory=log-utils
# and with extra reqs:
$ poetry add "git+https://github.com/puntonim/utils-monorepo#subdirectory=log-utils[rich-adapter,loguru-adapter]"
# and at a specific version:
$ poetry add git+https://github.com/puntonim/utils-monorepo@00a49cb64524df19bf55ab5c7c1aaf4c09e92360#subdirectory=log-utils
# and at a specific version, with extra reqs:
$ poetry add "git+https://github.com/puntonim/utils-monorepo@00a49cb64524df19bf55ab5c7c1aaf4c09e92360#subdirectory=log-utils[rich-adapter,loguru-adapter]"

# From a local dir:
$ poetry add ../utils-monorepo/log-utils/
$ poetry add "log-utils @ file:///Users/myuser/workspace/utils-monorepo/log-utils/"
# and with extra reqs:
$ poetry add "../utils-monorepo/log-utils/[rich-adapter,loguru-adapter]"
# and I was able to choose a Git version only with pip (not poetry):
$ pip install "git+file:///Users/myuser/workspace/utils-monorepo@00a49cb64524df19bf55ab5c7c1aaf4c09e92360#subdirectory=log-utils" 
```

3 - Pre-commit
--------------
```sh
$ pre-commit install
```


🚀 Deployment
=============

*Not deployed* as it can be (pip-)installed directly from Github o local dir 
 (see Usage section).\
And *not versioned* as when (pip-)installing from Github, it is possible to choose
 any version with a hash commit (see Usage section).


🔨 Test
======

```sh
$ make test
```


©️ Copyright
=============

Copyright puntonim (https://github.com/puntonim). No License.
