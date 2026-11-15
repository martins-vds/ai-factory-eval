TAILWIND_VERSION := 4.1.12
TAILWIND_CLI := /tmp/tailwindcss-$(TAILWIND_VERSION)-linux-x64
TAILWIND_INPUT := /tmp/ai-factory-eval-tailwind-$(TAILWIND_VERSION).css
TAILWIND_URL := https://github.com/tailwindlabs/tailwindcss/releases/download/v$(TAILWIND_VERSION)/tailwindcss-linux-x64
TAILWIND_SHA256 := 5eeee66ea237eae9a160fa3314fd0cf76ab993551a99fafb16fa1db6c6b90289

.PHONY: tailwind-install tailwind-build

tailwind-install: $(TAILWIND_CLI)

$(TAILWIND_CLI):
	curl --fail --location --silent --show-error $(TAILWIND_URL) --output $@ && \
	printf '%s  %s\n' '$(TAILWIND_SHA256)' '$@' | sha256sum --check && \
	chmod +x $@

tailwind-build: tailwind-install
	@set -e; trap 'rm -f $(TAILWIND_INPUT)' EXIT; \
	printf '%s\n' '@import "tailwindcss";' '@source "$(CURDIR)/templates";' > $(TAILWIND_INPUT); \
	mkdir -p static/css; \
	$(TAILWIND_CLI) --input $(TAILWIND_INPUT) --output static/css/tailwind.css --minify
