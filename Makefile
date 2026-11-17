TAILWINDCSS_VERSION ?= v4.3.3
PYTAILWINDCSS_VERSION ?= 0.4.2
export TAILWINDCSS_VERSION

.PHONY: tailwind-install tailwind-build

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
