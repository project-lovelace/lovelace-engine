SHELL := /bin/bash

ENGINE_PID_FILE := /var/run/lovelace-engine.pid
ENGINE_PORT := 14714

PYTHON37 := /usr/local/bin/python3
GUNICORN := /usr/local/bin/gunicorn

prepare-venv: clean
	@echo "Preparing virtual environment..."
	@echo "Not implemented..."

update-requirements:
	@echo "Updating environment requirements..."

start-engine: stop-engine
	@echo "Starting the Lovelace Engine in the foreground..."
	$(PYTHON37) $(GUNICORN) --workers 1 --log-level debug --timeout 600 --preload --reload --bind localhost:$(ENGINE_PORT) engine.api:app

stop-engine:
	@echo "Stopping the Lovelace Engine gracefully..."
	if [ -a $(ENGINE_PID_FILE) ]; then kill -15 `cat $(ENGINE_PID_FILE)` ; sudo rm -f $(ENGINE_PID_FILE) ; fi;
	@echo "Deleting linux containers by force..."
	-lxc list -c n | grep lovelace | cut -d " " -f2 | xargs --no-run-if-empty lxc delete --force

test:
	@echo "Make sure the engine is running!"
	@echo "Running tests..."
	cd engine ; $(PYTHON37) -m unittest test_api.py

clean:
	@echo "Deleting old virtual environment..."
	@echo "Not implemented..."
