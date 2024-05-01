# make build
# make start

SHELL := /bin/bash
HIDE ?= @
DOCKER_IMAGE ?= brain/memory
DOCKER_CONTAINER ?= memory
VOLUME ?=-v $(PWD):/brain/src -v $(DOCKER_CONTAINER)-venv:/venv
ENV ?= --env-file=./docker/dev-env.rc --env-file=./docker/dev-env-secrets.rc


.PHONY: build install start neo4j


build:
	$(HIDE)docker build --build-arg GITHUB_TOKEN=$(GITHUB_TOKEN) -f Dockerfile -t $(DOCKER_IMAGE) $(PWD)
	$(HIDE)$(MAKE) install

install:
	$(HIDE)docker run --rm \
		$(VOLUME) \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-e ENVIRONMENT=development $(DOCKER_IMAGE) docker/setup.sh

start:
	$(HIDE)docker run -it --name=$(DOCKER_CONTAINER) --network=brain-dev-network -p8501:8501 $(VOLUME) $(ENV) --rm $(DOCKER_IMAGE) streamlit run streamlit_app/app.py
	$(HIDE)echo docker run -it --network=brain-dev-network -p8501:8501 $(VOLUME) $(ENV) --rm $(DOCKER_IMAGE) /bin/bash

neo4j:
	$(HIDE)docker run -it --network=brain-dev-network --rm --name=neo4j --publish=7474:7474 --publish=7687:7687 \
		--volume=${PWD}/neo4j/conf:/conf2 \
		--volume=${PWD}/neo4j/plugins:/plugins2 \
		--env=NEO4JLABS_PLUGINS='["apoc"]' \
		--env NEO4J_AUTH=none \
		--env NEO4J_PLUGINS='["apoc"]' \
		--volume=neo4j2:/data \
		neo4j:5.19.0
		#neo4j:4.4.33-community
		#neo4j@sha256:20c767b8eb4742bdcaa394dc25223ca40acf481a666f20b64c91fff82424dfcb

enter.%:
	$(HIDE)docker exec -it $* /bin/bash
