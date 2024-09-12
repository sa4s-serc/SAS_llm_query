# Installation Guide

If you are a Windows user, make sure to execute the following commands before proceeding with the installation:

In Command Prompt:

```
set PYTHONUTF8=1
```

In PowerShell:

```
$env:PYTHONUTF8 = "1"
```

This will help counter any UTF-8 encoding issues. If it doesn't work, then execute this command

```
chcp 65001
```

## Prerequisites

- Conda or Miniconda (for managing environments)

## ~~Set Up the Environment Using Conda~~ (Deprecated)

~~It's recommended to use Conda or Miniconda for managing environments. This keeps dependencies required by different projects separate.~~

~~Create the environment using the provided `environment.yml` file:~~

```
conda env create -f environment.yml
```

~~Activate the environment:~~

```
conda activate iot
```

## Set Up the Environment Using `python venv`

### For Linux

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### For Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Step 3: Configuration

Review the `app/config.py` file and adjust any settings if needed. You can modify port numbers, app name, or add any additional configuration parameters here.

## Step 4: Run the Application

To start the IIIT Companion application, run the following command from the project root directory:

```
python run.py
```

This will start all the microservices and launch the Streamlit app for the IIIT Companion Builder.

## Verifying the Installation

After running the application:

1. Open a web browser and navigate to `http://localhost:8501` (or the port specified in your configuration).
2. You should see the IIIT Companion Builder interface.
3. Try creating a custom dashboard by selecting various features and clicking the "Create My IIIT Companion App" button.
4. If a new URL is generated and you can access the custom dashboard, the installation was successful.

## Troubleshooting

If you encounter any issues during the installation process, please refer to the [Troubleshooting](TROUBLESHOOTING.md) guide or open an issue on the GitHub repository.

## Next Steps

Now that you have successfully installed the IIIT Companion app, you can proceed to the [Usage Guide](USAGE.md) to learn how to use and customize the application.
