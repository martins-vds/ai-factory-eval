TAILWIND_VERSION := 4.1.17
TAILWIND_CLI ?= $(HOME)/.local/bin/tailwindcss
TAILWIND_URL := https://github.com/tailwindlabs/tailwindcss/releases/download/v$(TAILWIND_VERSION)/tailwindcss-linux-x64
TAILWIND_SHA256 := cc115d9b6c4ede4e423bfea6a3cfc3f03e6c1702b7d910369b9540e2b4cf3860

.PHONY: tailwind-install tailwind-build

tailwind-install:
	@set -eu; \
	if [ -x "$(TAILWIND_CLI)" ] && printf '%s  %s\n' "$(TAILWIND_SHA256)" "$(TAILWIND_CLI)" | sha256sum -c - >/dev/null 2>&1; then exit 0; fi; \
	tmp="$(TAILWIND_CLI).tmp"; \
	trap 'rm -f "$$tmp"' EXIT; \
	mkdir -p "$(dir $(TAILWIND_CLI))"; \
	curl -fsSL "$(TAILWIND_URL)" -o "$$tmp"; \
	printf '%s  %s\n' "$(TAILWIND_SHA256)" "$$tmp" | sha256sum -c -; \
	chmod +x "$$tmp"; \
	mv "$$tmp" "$(TAILWIND_CLI)"

tailwind-build: tailwind-install
	@set -eu; \
	mkdir -p static/css; \
	input=$$(mktemp static/css/.tailwind-input.XXXXXX.css); \
	trap 'rm -f "$$input"' EXIT; \
	printf '@import "tailwindcss" source("../../");\n' > "$$input"; \
	"$(TAILWIND_CLI)" --input "$$input" --output static/css/tailwind.css --minify
