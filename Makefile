TAILWIND_VERSION := v4.1.14
TAILWIND_BIN := .tools/tailwindcss

.PHONY: tailwind-install tailwind-build

tailwind-install:
	mkdir -p .tools
	curl -fL "https://github.com/tailwindlabs/tailwindcss/releases/download/$(TAILWIND_VERSION)/tailwindcss-linux-x64" -o $(TAILWIND_BIN)
	chmod +x $(TAILWIND_BIN)

tailwind-build: tailwind-install
	printf '@import "tailwindcss";\n@source "./templates";\n' > .tailwind.css
	$(TAILWIND_BIN) -i .tailwind.css -o static/css/tailwind.css --minify
	rm -f .tailwind.css
