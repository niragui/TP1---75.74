SHELL := /bin/bash
PWD := $(shell pwd)

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init

default: build

all:


docker-image-server:
	docker build -f ./Server/Filters/Dockerfile -t "filter:latest" .
	docker build -f ./Server/Joiner/Dockerfile -t "joiner:latest" .
	docker build -f ./Server/Server/Dockerfile -t "server:latest" .
.PHONY: docker-image-server

docker-image-client:
	docker build -f ./Client/Source/Dockerfile -t "client:latest" .
.PHONY: docker-image-client

docker-compose-up: 
	docker-image-server
	docker-image-client
	docker compose -f docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-up

docker-compose-down:
	docker compose -f docker-compose-dev.yaml stop -t 1
	docker compose -f docker-compose-dev.yaml down
.PHONY: docker-compose-down

docker-compose-logs:
	docker compose -f docker-compose-dev.yaml logs -f
.PHONY: docker-compose-logs