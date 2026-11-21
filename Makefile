TAILWIND_VERSION := 4.3.5
TAILWIND_CLI := $(HOME)/.local/bin/tailwindcss
TAILWIND_SHA256 := e47695cee3f0d90623a91f3939b08bdee610eb5ad99340adff9d4145b284d6cc

.PHONY: tailwind-install tailwind-build

tailwind-install:
	@set -e; \
	if ! echo "$(TAILWIND_SHA256)  $(TAILWIND_CLI)" | sha256sum --check --status 2>/dev/null; then \
		mkdir -p "$(dir $(TAILWIND_CLI))"; \
		curl --fail --location --silent --show-error \
			"https://github.com/tailwindlabs/tailwindcss/releases/download/v$(TAILWIND_VERSION)/tailwindcss-linux-x64" \
			--output "$(TAILWIND_CLI)"; \
		echo "$(TAILWIND_SHA256)  $(TAILWIND_CLI)" | sha256sum --check; \
		chmod 755 "$(TAILWIND_CLI)"; \
	fi

tailwind-build: tailwind-install
	@set -e; \
	mkdir -p static/css; \
	input=$$(mktemp static/css/.tailwind-input.XXXXXX); \
	trap 'rm -f "$$input"' EXIT; \
	printf '%s\n' \
		'@import "tailwindcss";' \
		'@source "../../templates";' \
		'@theme {' \
		'  --color-library-paper: rgb(245 240 229);' \
		'  --color-library-ink: rgb(47 52 40);' \
		'  --color-library-rust: rgb(169 78 55);' \
		'  --color-library-line: rgb(216 205 187);' \
		'  --color-library-surface: rgb(255 253 247);' \
		'  --color-library-muted: rgb(98 99 89);' \
		'}' \
		'.library-page { font-family: Georgia, "Times New Roman", serif; }' \
		'.catalog-shell { max-width: 76rem; margin-inline: auto; padding-inline: 1.5rem; }' \
		'.catalog-grid { display: grid; grid-template-columns: minmax(0, 1fr) 19rem; gap: 3rem; }' \
		'.loan-entry { border-bottom: 1px solid var(--color-library-line); }' \
		'.catalog-note { box-shadow: 0 10px 24px rgb(47 52 40 / 6%); }' \
		'@media (max-width: 1023px) { .catalog-grid { grid-template-columns: 1fr; } }' \
		'@media (max-width: 640px) { .catalog-shell { padding-inline: 1rem; } }' \
		> "$$input"; \
	"$(TAILWIND_CLI)" --input "$$input" --output static/css/tailwind.css --minify
