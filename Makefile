PYTHON ?= python3.12
VENV_PYTHON := .venv/bin/python
HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: help install run dev test check

help:
	@printf '%s\n' \
		'make install  — создать окружение и установить зависимости' \
		'make run      — запустить приложение' \
		'make dev      — запустить с перезагрузкой при изменении кода' \
		'make test     — запустить тесты' \
		'make check    — проверить /health и /version запущенного сервера'

$(VENV_PYTHON):
	$(PYTHON) -m venv .venv

install: $(VENV_PYTHON)
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt
	@test -e .env || cp .env.example .env

run:
	$(VENV_PYTHON) -m uvicorn app_final:app --host $(HOST) --port $(PORT)

dev:
	$(VENV_PYTHON) -m uvicorn app_final:app --host $(HOST) --port $(PORT) --reload

test:
	$(VENV_PYTHON) -m pytest -v

check:
	curl -fsS -i -w '\n' "http://$(HOST):$(PORT)/health"
	curl -fsS -i -w '\n' "http://$(HOST):$(PORT)/version"
