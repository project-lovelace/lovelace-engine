SHELL := /bin/bash

ENGINE_PID_FILE := /var/run/engine.pid
ENGINE_PORT := 14714

prepare-venv: clean
	@echo "Preparing virtual environment..."
	virtualenv -p python3.6 --verbose --prompt='(lovelace-engine) ' env
	env/bin/pip install -r requirements.txt

update-requirements:
	@echo "Updating environment requirements..."
	cp requirements.txt requirements.txt.old
	env/bin/pip freeze > requirements.txt
	sed -i '/pkg-resources==0.0.0/d' requirements.txt  # Ubuntu 16.04 bug causes this erroneous requirement
	@echo "Applied the following changes to requirements.txt..."
	diff requirements.txt.old requirements.txt ; [ $$? -eq 1 ]  # diff returns non-zero codes
	rm -f requirements.txt.old

start-engine: stop-engine
	@echo "Starting the Lovelace Engine in the background..."
	env/bin/python env/bin/gunicorn --reload --bind localhost:$(ENGINE_PORT) engine.api:app &
	echo "$$!" | sudo tee $(ENGINE_PID_FILE)

start-engine-fg: stop-engine
	@echo "Starting the Lovelace Engine in the foreground..."
	env/bin/python env/bin/gunicorn --reload --bind localhost:$(ENGINE_PORT) engine.api:app

stop-engine:
	@echo "Stopping the Lovelace Engine gracefully..."
	if [ -a $(ENGINE_PID_FILE) ]; then kill -SIGTERM `cat $(ENGINE_PID_FILE)` ; sudo rm -f $(ENGINE_PID_FILE) ; fi;

clean:
	@echo "Deleting old virtual environment..."
	rm -rf ./env
