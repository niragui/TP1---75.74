SHELL := /bin/bash
PWD := $(shell pwd)

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init

default: build

all:

docker-image-server:
	docker build -f ./Server/Server/Dockerfile -t "server:latest" .
	docker build -f ./Server/Parser/Dockerfile -t "parser:latest" .
	docker build -f ./Server/RainFilter/Dockerfile -t "rainfilter:latest" .
	docker build -f ./Server/YearFilter/Dockerfile -t "yearfilter:latest" .
	docker build -f ./Server/MontrealFilter/Dockerfile -t "montrealfilter:latest" .
	docker build -f ./Server/RainJoiner/Dockerfile -t "rainjoiner:latest" .
	docker build -f ./Server/YearJoiner/Dockerfile -t "yearjoiner:latest" .
	docker build -f ./Server/MontrealJoiner/Dockerfile -t "montrealjoiner:latest" .
.PHONY: docker-image-server

docker-image-client:
	docker build -f ./Client/Source/Dockerfile -t "client:latest" .
.PHONY: docker-image-client

docker-compose-server-up:
	make docker-image-server
	docker compose -f server-docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-server-up

docker-compose-server-down:
	docker compose -f server-docker-compose-dev.yaml stop -t 1
	docker compose -f server-docker-compose-dev.yaml down
.PHONY: docker-compose-server-down

docker-compose-server-logs:
	docker compose -f server-docker-compose-dev.yaml logs -f
.PHONY: docker-compose-server-logs

docker-compose-client-up:
	make docker-image-client
	docker compose -f client-docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-client-up

docker-compose-client-down:
	docker compose -f client-docker-compose-dev.yaml stop -t 1
	docker compose -f client-docker-compose-dev.yaml down
.PHONY: docker-compose-client-down

docker-compose-client-logs:
	docker compose -f client-docker-compose-dev.yaml logs -f
.PHONY: docker-compose-client-logs