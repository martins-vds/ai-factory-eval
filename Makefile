TAILWIND_VERSION := 4.1.11
TAILWIND_BIN ?= $(HOME)/.local/bin/tailwindcss

.PHONY: tailwind-install tailwind-build

tailwind-install:
	mkdir -p "$(dir $(TAILWIND_BIN))"
	curl -fsSL "https://github.com/tailwindlabs/tailwindcss/releases/download/v$(TAILWIND_VERSION)/tailwindcss-linux-x64" -o "$(TAILWIND_BIN)"
	chmod +x "$(TAILWIND_BIN)"

tailwind-build: tailwind-install
	@input=$$(mktemp); trap 'rm -f "$$input"' EXIT; \
	printf '@import "tailwindcss" source(none);\n@source "$(CURDIR)/templates";\n' > "$$input"; \
	"$(TAILWIND_BIN)" -i "$$input" -o static/css/tailwind.css --minify
