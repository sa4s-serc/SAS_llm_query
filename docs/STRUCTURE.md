
```
.
├── README.md
├── app
│   ├── __init__.py
│   ├── builder
│   │   ├── __init__.py
│   │   └── builder_app.py
│   ├── config.py
│   ├── main.py
│   ├── microservices
│   │   ├── __init__.py
│   │   ├── air_quality
│   │   │   └── service.py
│   │   ├── base.py
│   │   └── booking_event
│   │       ├── extra.py
│   │       └── service.py
│   ├── run_microservices.py
│   ├── services.toml
│   ├── templates
│   │   ├── __init__.py
│   │   └── generated_app_template.py
│   └── utils
│       ├── __init__.py
│       ├── app_generator.py
│       ├── chatbot.py
│       ├── logger.py
│       └── port_manager.py
├── docker-compose.yml
├── docs
│   ├── CONTRIBUTING.md
│   ├── INSTALLATION.md
│   ├── SERVICES.md
│   ├── STRUCTURE.md
│   └── TROUBLESHOOTING.md
├── get_services.sh
├── microservice_info.txt
├── requirements.txt
├── run.py
└── tests
    ├── __init__.py
    ├── test_builder.py
    ├── test_microservices.py
    └── test_utils.py

```