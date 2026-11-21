TAILWIND_VERSION := 4.3.5
TAILWIND_SHA256 := e47695cee3f0d90623a91f3939b08bdee610eb5ad99340adff9d4145b284d6cc
TAILWIND_BIN ?= $(HOME)/.local/bin/tailwindcss

.PHONY: tailwind-install tailwind-build

tailwind-install:
	@mkdir -p "$(dir $(TAILWIND_BIN))"
	@set -eu; tmp=$$(mktemp); trap 'rm -f "$$tmp"' EXIT; \
		curl --fail --location --silent --show-error \
		  "https://github.com/tailwindlabs/tailwindcss/releases/download/v$(TAILWIND_VERSION)/tailwindcss-linux-x64" \
		  --output "$$tmp"; \
		printf '%s  %s\n' "$(TAILWIND_SHA256)" "$$tmp" | sha256sum --check; \
		install -m 0755 "$$tmp" "$(TAILWIND_BIN)"

tailwind-build:
	@mkdir -p static/css
	@set -eu; tmp=$$(mktemp); trap 'rm -f "$$tmp"' EXIT; \
		printf '@import "tailwindcss";\n@source "%s/templates";\n' "$(CURDIR)" > "$$tmp"; \
		"$(TAILWIND_BIN)" --input "$$tmp" --output static/css/tailwind.css --minify
