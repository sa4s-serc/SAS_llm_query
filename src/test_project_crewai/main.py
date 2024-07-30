#!/usr/bin/env python
import sys
from test_project_crewai.server import app


def run():
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    run()
