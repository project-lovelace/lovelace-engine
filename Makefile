SHELL := /bin/bash

ENGINE_PID_FILE := /var/run/lovelace-engine.pid
ENGINE_PORT := 14714

PYTHON37 := /root/anaconda3/envs/lovelace_engine_env/bin/python
GUNICORN := /root/anaconda3/envs/lovelace_engine_env/bin/gunicorn

prepare-venv: clean
	@echo "Preparing virtual environment..."
	@echo "Not implemented..."

update-requirements:
	@echo "Updating environment requirements..."

start-engine: stop-engine
	# @echo "Starting the Lovelace Engine in the background..."
	# $(PYTHON37) $(GUNICORN) --daemon --workers 1 --log-level info ---access-logfile /var/log/lovelace/gunicorn-access.log --error-logfile /var/log/lovelace/gunicorn-error.log --preload --pid $(ENGINE_PID_FILE) --bind localhost:$(ENGINE_PORT) engine.api:app

start-engine-fg: stop-engine
	@echo "Starting the Lovelace Engine in the foreground..."
	$(PYTHON37) $(GUNICORN) --workers 1 --log-level debug --timeout 600 --preload --reload --bind localhost:$(ENGINE_PORT) engine.api:app

stop-engine:
	@echo "Stopping the Lovelace Engine gracefully..."
	if [ -a $(ENGINE_PID_FILE) ]; then kill -15 `cat $(ENGINE_PID_FILE)` ; sudo rm -f $(ENGINE_PID_FILE) ; fi;
	@echo "Deleting linux containers by force..."
	-lxc list -c n | grep lovelace | cut -d " " -f2 | xargs lxc delete --force

clean:
	@echo "Deleting old virtual environment..."
	@echo "Not implemented..."
