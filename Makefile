.PHONY: tailwind-install tailwind-build

tailwind-install:
	mkdir -p bin
	curl -L --fail --silent --show-error -o bin/tailwindcss https://github.com/tailwindlabs/tailwindcss/releases/download/v4.1.17/tailwindcss-linux-x64
	chmod +x bin/tailwindcss

tailwind-build:
	bin/tailwindcss -i static/css/tailwind.css -o static/css/tailwind.css --minify
