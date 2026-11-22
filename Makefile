TAILWIND_VERSION := 4.1.13
TAILWIND_HOME := $(HOME)/.cache/ai-factory-eval/tailwind-$(TAILWIND_VERSION)
TAILWIND_BIN := $(TAILWIND_HOME)/node_modules/.bin/tailwindcss

.PHONY: tailwind-install tailwind-build

tailwind-install:
	npm install --prefix "$(TAILWIND_HOME)" --no-save --no-package-lock @tailwindcss/cli@$(TAILWIND_VERSION) tailwindcss@$(TAILWIND_VERSION)

tailwind-build: tailwind-install
	mkdir -p static/css
	@input=$$(mktemp "$(TAILWIND_HOME)/tailwind-input.XXXXXX.css"); \
	trap 'rm -f "$$input"' EXIT; \
	printf '@import "tailwindcss" source(none);\n@source "$(CURDIR)/templates";\n' > "$$input"; \
	"$(TAILWIND_BIN)" --input "$$input" --output static/css/tailwind.css --minify
