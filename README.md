# Particulate Matter Sensor Storage

### Development setup

Create a virtual environment
```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies
```sh
pip install --requirement requirements.txt
```

### Deploy the Cloud Function

Deploy a new version
```sh
make deploy
```
