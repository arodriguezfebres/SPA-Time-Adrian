Invoke-Expression -Command "Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python"
Invoke-Expression -Command "cd $TRAVIS_BUILD_DIR/project/cloudformation/"
Invoke-Expression -Command "poetry install"