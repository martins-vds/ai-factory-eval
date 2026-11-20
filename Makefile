.PHONY: tailwind-install tailwind-build

tailwind-install:
	npm install --no-save --package-lock=false --no-audit --no-fund @tailwindcss/cli@4.1.17 tailwindcss@4.1.17 daisyui@5.0.0

tailwind-build:
	mkdir -p static/css
	input=$$(mktemp /tmp/lending-library-tailwind.XXXXXX.css); trap 'rm -f "$$input"' EXIT; \
	printf '%s\n' '@import "$(CURDIR)/node_modules/tailwindcss/index.css";' \
		'@plugin "$(CURDIR)/node_modules/daisyui/index.js";' \
		'@source "$(CURDIR)/templates";' > "$$input"; \
	./node_modules/.bin/tailwindcss --input "$$input" --output static/css/tailwind.css
