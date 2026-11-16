TAILWIND_VERSION := 4.1.17
TAILWIND_BIN ?= $(HOME)/.local/bin/tailwindcss
TAILWIND_URL := https://github.com/tailwindlabs/tailwindcss/releases/download/v$(TAILWIND_VERSION)/tailwindcss-linux-x64
TAILWIND_SHA256 := cc115d9b6c4ede4e423bfea6a3cfc3f03e6c1702b7d910369b9540e2b4cf3860

.PHONY: tailwind-install tailwind-build

tailwind-install:
	@mkdir -p "$(dir $(TAILWIND_BIN))"
	@curl -fsSL "$(TAILWIND_URL)" -o "$(TAILWIND_BIN).tmp"
	@echo "$(TAILWIND_SHA256)  $(TAILWIND_BIN).tmp" | sha256sum --check
	@chmod +x "$(TAILWIND_BIN).tmp"
	@mv "$(TAILWIND_BIN).tmp" "$(TAILWIND_BIN)"

tailwind-build: tailwind-install
	@set -eu; input=$$(mktemp "$(CURDIR)/.tailwindcss.XXXXXX"); \
	trap 'rm -f "$$input"' EXIT; \
	printf '%s\n' '@import "tailwindcss";' '@source "./templates";' > "$$input"; \
	"$(TAILWIND_BIN)" -i "$$input" -o static/css/tailwind.css --minify
