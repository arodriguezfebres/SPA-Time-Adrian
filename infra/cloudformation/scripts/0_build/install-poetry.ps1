Invoke-Expression -Command "(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python"
Invoke-Expression -Command "source $HOME/.poetry/env"
Invoke-Expression -Command "poetry install"