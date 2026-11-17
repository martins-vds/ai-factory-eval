.PHONY: tailwind-install tailwind-build

TAILWIND_DIR ?= /tmp/ll-01-tailwind

tailwind-install:
	mkdir -p "$(TAILWIND_DIR)"
	npm install --prefix "$(TAILWIND_DIR)" --no-save --no-package-lock @tailwindcss/cli@4.3.5 tailwindcss@4.3.5 daisyui@5.8.1

tailwind-build: tailwind-install
	printf '@import "tailwindcss";\n@plugin "daisyui";\n@source "%s/templates";\n' "$(CURDIR)" > "$(TAILWIND_DIR)/input.css"
	"$(TAILWIND_DIR)/node_modules/.bin/tailwindcss" --input "$(TAILWIND_DIR)/input.css" --output static/css/tailwind.css --minify
