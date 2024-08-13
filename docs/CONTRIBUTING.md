
## Logging

Remember to import the logger in any other files where you want to add logging. You can do this by adding:
```py
from app.utils.logger import setup_logger
logger = setup_logger(__name__)
```
at the top of the file, and then use logger.info(), logger.warning(), logger.error(), etc. as needed.


## Adding additional dependencies

If you install any additional dependencies make sure to add them in the `environment.yml` file
you can do so by using 
```py
conda env export | grep -v "^prefix: " > environment.yml
```
make sure you are using this environment only for this project to avoid dependency conflicts