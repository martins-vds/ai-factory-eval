TAILWINDCSS_VERSION ?= v4.3.3
PYTAILWINDCSS_VERSION ?= 0.4.2
PORT ?= 8080
export TAILWINDCSS_VERSION

.PHONY: run tailwind-install tailwind-build

run:
	python manage.py runserver 0.0.0.0:$(PORT)

tailwind-install:
	python -m pip install pytailwindcss==$(PYTAILWINDCSS_VERSION)
	tailwindcss_install

tailwind-build:
	@set -eu; \
	mkdir -p static/css; \
	input=$$(mktemp static/css/.tailwind-input.XXXXXX.css); \
	trap 'rm -f "$$input"' EXIT; \
	printf '%s\n' '@import "tailwindcss" source(none);' '@source "../../src";' '@source "../../templates";' > "$$input"; \
	tailwindcss -i "$$input" -o static/css/tailwind.css --minify
