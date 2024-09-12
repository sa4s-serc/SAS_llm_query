## Logging

Remember to import the logger in any other files where you want to add logging. You can do this by adding:

```py
from app.utils.logger import setup_logger
logger = setup_logger(__name__)
```

at the top of the file, and then use logger.info(), logger.warning(), logger.error(), etc. as needed.

## Adding additional dependencies

### ~~Using Conda~~ (Deprecated)

~~
If you install any additional dependencies make sure to add them in the `environment.yml` file
you can do so by using~~

```sh
conda env export | grep -v "^prefix: " > environment.yml
```

~~make sure you are using this environment only for this project to avoid dependency conflicts~~

### Using Python

Make sure you are updating the `requirements.txt` file as you install new dependencies, you can do this by using

```sh
pip freeze > requirements.txt
```

## Generic Service template

```py
from app.microservices.base import MicroserviceBase

class ExampleService(MicroserviceBase):
    def __init__(self):
        super().__init__("example_service")
        self.update_service_info(
            description="Example microservice template",
            dependencies=[]  # Add any dependencies here
        )

    def register_routes(self):
        @self.app.get("/")
        async def root():
            return {"message": "Hello from Example Service"}

        @self.app.get("/data")
        async def get_data():
            return {"data": "Some example data"}

    # Add any service-specific methods here
    def some_service_method(self):
        return "Service-specific logic"

def start_example_service():
    service = ExampleService()
    service.run()

if __name__ == "__main__":
    start_example_service()

```
