TAILWIND_VERSION := 4.1.11
TAILWIND_BINARY := /tmp/tailwindcss-$(TAILWIND_VERSION)-linux-x64

.PHONY: tailwind-install tailwind-build

tailwind-install:
	curl -fsSL https://github.com/tailwindlabs/tailwindcss/releases/download/v$(TAILWIND_VERSION)/tailwindcss-linux-x64 -o $(TAILWIND_BINARY)
	chmod +x $(TAILWIND_BINARY)

tailwind-build: tailwind-install
	mkdir -p static/css
	@set -e; trap 'rm -f static/css/.tailwind-input.css' EXIT; \
	printf '%s\n' '@import "tailwindcss";' '@source "../../templates";' \
		'@theme {' '  --color-paper: #f5f0e5;' '  --color-ink: #2f3428;' \
		'  --color-accent: #a94e37;' '  --color-line: #d8cdbb;' \
		'  --color-surface: #fffdf7;' '}' > static/css/.tailwind-input.css; \
	$(TAILWIND_BINARY) -i static/css/.tailwind-input.css -o static/css/tailwind.css --minify
