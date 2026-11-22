TAILWIND_VERSION ?= v4.1.17
TAILWIND_BIN ?= /tmp/tailwindcss-$(TAILWIND_VERSION)

.PHONY: tailwind-install tailwind-build

tailwind-install:
	curl -fsSL "https://github.com/tailwindlabs/tailwindcss/releases/download/$(TAILWIND_VERSION)/tailwindcss-linux-x64" -o "$(TAILWIND_BIN)"
	chmod +x "$(TAILWIND_BIN)"

tailwind-build: tailwind-install
	@input=$$(mktemp --suffix=.css); \
	trap 'rm -f "$$input"' EXIT; \
	printf '@import "tailwindcss" source(none);\n@source "%s/templates";\n' "$(CURDIR)" > "$$input"; \
	mkdir -p static/css; \
	"$(TAILWIND_BIN)" -i "$$input" -o static/css/tailwind.css --minify
