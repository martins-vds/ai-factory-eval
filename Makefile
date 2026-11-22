TAILWIND_VERSION := v4.1.17
TAILWIND_BIN ?= $(HOME)/.local/bin/tailwindcss
TAILWIND_URL := https://github.com/tailwindlabs/tailwindcss/releases/download/$(TAILWIND_VERSION)/tailwindcss-linux-x64

.PHONY: tailwind-install tailwind-build

tailwind-install:
	mkdir -p "$(dir $(TAILWIND_BIN))"
	curl -fsSL "$(TAILWIND_URL)" -o "$(TAILWIND_BIN)"
	chmod +x "$(TAILWIND_BIN)"

tailwind-build: tailwind-install
	mkdir -p static/css
	@input=$$(mktemp); trap 'rm -f "$$input"' EXIT; printf '%s\n' '@import "tailwindcss";' > "$$input"; "$(TAILWIND_BIN)" -i "$$input" -o static/css/tailwind.css --minify
