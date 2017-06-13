ENGINE_PID_FILE := /var/run/engine.pid

prepare-venv: clean
	@echo "Preparing virtual environment..."
	virtualenv -p python3.6 --verbose --prompt='(lovelace-engine) ' env
	env/bin/pip install -r requirements.txt

update-requirements:
	@echo "Updating environment requirements..."
	env/bin/pip freeze > requirements.txt

start-engine:
	@echo "Starting the Lovelace Engine..."
	env/bin/python env/bin/gunicorn --reload engine.api:app & echo "$$!" | sudo tee $(ENGINE_PID_FILE)

stop-engine:
	@echo "Stopping the Lovelace Engine gracefully..."
	kill -SIGTERM `cat $(ENGINE_PID_FILE)`

clean:
	@echo "Deleting old virtual environment..."
	rm -rf ./env
