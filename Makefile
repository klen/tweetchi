ENVBIN=$(CURDIR)/.env/bin
PIP=$(ENVBIN)/pip
PYTHON=$(ENVBIN)/python
PYBABEL=$(ENVBIN)/pybabel
BABELDIR=$(CURDIR)/base/translations
MODULE=base
CONFIG=$(MODULE).config.develop

all: .env

.env: requirements.txt
	virtualenv --no-site-packages .env
	$(PIP) install -M -r requirements.txt


.PHONY: shell
shell: .env/ manage.py
	$(PYTHON) manage.py shell -c $(CONFIG)


.PHONY: run
run: .env/ manage.py
	$(PYTHON) manage.py runserver -c $(CONFIG)


.PHONY: db
db: .env/ manage.py
	$(PYTHON) manage.py migrate upgrade head -c $(CONFIG)

.PHONY: audit
audit:
	pylama $(MODULE) -i E501

.PHONY: test
test: .env/ manage.py
	$(PYTHON) manage.py test -c $(MODULE).config.test

.PHONY: clean
clean:
	find $(CURDIR) -name "*.pyc" -delete
	find $(CURDIR) -name "*.orig" -delete

.PHONY: babel
babel: $(BABELDIR)/ru
	$(PYBABEL) extract -F $(BABELDIR)/babel.ini -k _gettext -k _ngettext -k lazy_gettext -o $(BABELDIR)/babel.pot --project Flask-base $(CURDIR)
	$(PYBABEL) update -i $(BABELDIR)/babel.pot -d $(BABELDIR)
	$(PYBABEL) compile -d $(BABELDIR)

$(BABELDIR)/ru:
	$(PYBABEL) init -i $(BABELDIR)/babel.pot -d $(BABELDIR) -l ru

.PHONY: chown
chown:
	sudo chown $(USER):$(USER) -R $(CURDIR)

.PHONY: pep8
pep8:
	find $(MODULE) -name "*.py" | xargs -n 1 autopep8 -i

.PHONY: celery
celery:
	celery worker -A base.tweetchi.celery.celery -B --loglevel=info
