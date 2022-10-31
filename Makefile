.EXPORT_ALL_VARIABLES:
DATASTORE_DATASET := noseiquela-dev
DATASTORE_EMULATOR_HOST := 0.0.0.0:8081
DATASTORE_EMULATOR_HOST_PATH := 0.0.0.0:8081/opt/datastore
DATASTORE_HOST := http://0.0.0.0:8081
DATASTORE_PROJECT_ID := noseiquela-dev

.PHONY: test.unit
test.unit: PYTHONPATH=$(shell pwd)/src/
test.unit:
	pytest tests/unit/ -vvv

.PHONY: test
test: PYTHONPATH=$(shell pwd)/src/
test: test.unit

.PHONY: docker.build
docker.build:
	docker-compose build

.PHONY: docker.run.emulator
docker.run.emulator:
	docker-compose up datastore

.PHONY: docker.run.viewer
docker.run.viewer:
	docker-compose up datastore-viewer

.PHONY: docker.run
docker.run: docker.build
	docker-compose up

.PHONY: clear
clear:
	@rm -rf build
	@rm -rf dist
	@find . -type f -name '*.py[co]' -exec rm -rf {} \;
	@find . -type d -name '__pycache__' -exec rm -rf {} \;
	@find . -type d -name 'noseiquela_orm.egg-info' -exec rm -rf {} \;