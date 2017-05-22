prepare-venv: clean
	virtualenv --no-site-packages env
	env/bin/pip install -r requirements.txt

start-engine:
	env/bin/python env/bin/gunicorn --reload engine.api:app

clean:
	rm -rf ./env
