TAILWIND_CLI = ./node_modules/.bin/tailwindcss
TAILWIND_VERSION = 4.3.5

.PHONY: tailwind-install tailwind-build

tailwind-install:
	npm install --no-save --no-package-lock @tailwindcss/cli@$(TAILWIND_VERSION)

tailwind-build:
	mkdir -p static/css
	@input=$$(mktemp static/css/tailwind-input.XXXXXX.css); \
	trap 'rm -f "$$input"' EXIT; \
	printf '@import "tailwindcss";\n@source "../../templates";\n' > "$$input"; \
	$(TAILWIND_CLI) --input "$$input" --output static/css/tailwind.css --minify
