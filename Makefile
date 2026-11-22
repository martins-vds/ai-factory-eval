TAILWIND_VERSION := v4.1.4
TAILWIND_OS := $(shell if [ "$$(uname -s)" = Darwin ]; then echo macos; else echo linux; fi)
TAILWIND_ARCH := $(shell uname -m | sed -e 's/x86_64/x64/' -e 's/aarch64/arm64/')
TAILWIND_BINARY := $(HOME)/.local/bin/tailwindcss-$(TAILWIND_VERSION)
TAILWIND_URL := https://github.com/tailwindlabs/tailwindcss/releases/download/$(TAILWIND_VERSION)/tailwindcss-$(TAILWIND_OS)-$(TAILWIND_ARCH)

.PHONY: tailwind-install tailwind-build

tailwind-install:
	@if [ ! -x "$(TAILWIND_BINARY)" ]; then \
		mkdir -p "$(HOME)/.local/bin"; \
		curl -fsSL "$(TAILWIND_URL)" -o "$(TAILWIND_BINARY)"; \
		chmod +x "$(TAILWIND_BINARY)"; \
	fi

tailwind-build: tailwind-install
	@mkdir -p static/css
	@printf '@import "tailwindcss";\n' | "$(TAILWIND_BINARY)" --cwd . --input - --output static/css/tailwind.css --minify
