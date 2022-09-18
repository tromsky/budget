# budget
A CLI personal budgeting tool

## Development

Clone this repo

```git clone git@github.com:tromsky/budget.git && cd budget```

Create a virtual environment

```pyenv install 3.10.6 && pyenv local 3.10.6 && python3 -m venv . --copies && source bin/activate```

Install requirements (and optional dev requirements)

```pip install -r requirements.txt```

```pip install -r requirements-dev.txt``` (Includes pylint, black, isort, pdbpp)

Create the database (TEMP, TODO: Automate as part of initialization process)

In the REPL (`python` or `python3`)
`from entities import *`

To run

```python main.py```

Tests and coverage

```
coverage run -m unittest discover  
open htmlcov/index.html
```