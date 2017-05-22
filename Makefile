prepare-venv: clean
	@echo "Preparing virtual environment..."
	virtualenv -p python3.6 --no-site-packages env
	env/bin/pip install -r requirements.txt

start-engine:
	@echo "Starting the Lovelace Engine..."
	env/bin/python env/bin/gunicorn --reload engine.api:app

clean:
	@echo "Deleting old virtual environment..."
	rm -rf ./env
