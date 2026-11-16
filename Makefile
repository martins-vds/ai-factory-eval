TAILWIND_VERSION := v4.1.12
TAILWIND_BIN ?= $(HOME)/.local/bin/tailwindcss-$(TAILWIND_VERSION)
TAILWIND_RELEASE := https://github.com/tailwindlabs/tailwindcss/releases/download/$(TAILWIND_VERSION)

.PHONY: tailwind-install tailwind-build

tailwind-install:
	@mkdir -p "$(dir $(TAILWIND_BIN))"
	@set -eu; \
	if [ ! -x "$(TAILWIND_BIN)" ]; then \
		case "$$(uname -s)-$$(uname -m)" in \
			Linux-x86_64) asset=tailwindcss-linux-x64; checksum=5eeee66ea237eae9a160fa3314fd0cf76ab993551a99fafb16fa1db6c6b90289 ;; \
			Linux-aarch64|Linux-arm64) asset=tailwindcss-linux-arm64; checksum=181332974fff1b3423ad75d6a2f1d09adf1ca63eb1324db0afbc4c30ff1ad086 ;; \
			*) echo "Unsupported Tailwind CLI platform: $$(uname -s)-$$(uname -m)" >&2; exit 1 ;; \
		esac; \
		tmp=$$(mktemp); \
		trap 'rm -f "$$tmp"' EXIT; \
		curl --fail --location --silent --show-error "$(TAILWIND_RELEASE)/$$asset" -o "$$tmp"; \
		printf '%s  %s\n' "$$checksum" "$$tmp" | sha256sum --check --status; \
		chmod +x "$$tmp"; \
		mv "$$tmp" "$(TAILWIND_BIN)"; \
	fi

tailwind-build: tailwind-install
	@mkdir -p static/css
	@set -eu; \
		input=$$(mktemp); \
		trap 'rm -f "$$input"' EXIT; \
		printf '@import "tailwindcss";\n@source "%s/templates";\n@theme { --font-serif: Georgia, "Times New Roman", serif; --color-paper: #f5f0e5; --color-ink: #2f3428; --color-muted: #666b5c; --color-accent: #a94e37; --color-line: #d8cdbb; --color-surface: #fffdf7; }\n' "$(CURDIR)" > "$$input"; \
		"$(TAILWIND_BIN)" -i "$$input" -o static/css/tailwind.css --minify
