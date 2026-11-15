TAILWIND_VERSION := v4.1.11
TAILWIND_BIN := $(HOME)/.local/bin/tailwindcss

.PHONY: tailwind-install tailwind-build

tailwind-install:
	mkdir -p "$(dir $(TAILWIND_BIN))"
	curl --fail --location --silent --show-error "https://github.com/tailwindlabs/tailwindcss/releases/download/$(TAILWIND_VERSION)/tailwindcss-linux-x64" --output "$(TAILWIND_BIN)"
	chmod +x "$(TAILWIND_BIN)"

tailwind-build: tailwind-install
	@input=$$(mktemp); trap 'rm -f "$$input"' EXIT; \
	printf '@import "tailwindcss";\n@source "%s/templates";\n' "$(CURDIR)" > "$$input"; \
	mkdir -p static/css; \
	"$(TAILWIND_BIN)" -i "$$input" -o static/css/tailwind.css --minify
