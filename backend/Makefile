SHELL := /bin/bash
.ONESHELL:

.PHONY: build build_cuda run_build run_build_gpu run_dev isort black lint check_and_rename_env

isort:
	isort

black:
	black .

lint: isort black

check_and_rename_env:
	  @if [ -e ".env" ]; then \
        echo "env file exists."; \
      else \
      	cp .env.example .env | \
        echo "File does not exist."; \
      fi

build: check_and_rename_env
	docker compose build


build_cuda: check_and_rename_env
	docker compose  -f docker_compose.gpu.yml build


run_build :
		docker compose build

run_build_gpu :
		docker compose -f docker_compose.gpu.yml up

run_dev : 
	docker compose up postgres redis -d
	. .venv/bin/activate 
	uv pip install -r requirements.txt
	alembic upgrade head
	uvicorn src.main:app --port 8000 --reload
	