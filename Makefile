SHELL := /bin/bash

ENGINE_PID_FILE := /var/run/lovelace-engine.pid
ENGINE_PORT := 14714

PYTHON37 := /root/anaconda3/envs/lovelace_engine_env/bin/python
GUNICORN := /root/anaconda3/envs/lovelace_engine_env/bin/gunicorn

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
	rm -rf ./env
