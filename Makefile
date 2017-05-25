prepare-venv: clean
	@echo "Creating new virtual environment..."
	virtualenv -p python3.6 --no-site-packages env
	env/bin/pip install -r requirements.txt

update-requirements:
	@echo "Updating environment requirements..."
	env/bin/pip freeze > requirements.txt

start-engine:
	@echo "Starting the Lovelace Engine..."
	env/bin/python env/bin/gunicorn --reload engine.api:app

clean:
	@echo "Deleting old virtual environment..."
	rm -rf ./env
