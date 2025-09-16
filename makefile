ARCHIVE = tests/example-filesystem.tar.gz
SRC_DIR = tests/example-filesystem
FOLDERS = test-repo the-big-folder

.PHONY: archive unarchive

archive:
	tar -czf $(ARCHIVE) -C $(SRC_DIR) $(FOLDERS)

unarchive:
	@mkdir -p $(SRC_DIR)
	tar -xzf $(ARCHIVE) -C $(SRC_DIR)

check:
	@mkdir -p extract
	@tar -xzf $(ARCHIVE) -C extract
	@echo "Comparing extracted archive with current data..."
	@if diff -qr extract $(SRC_DIR); then \
		echo "✅ Archive matches current content"; \
	else \
		echo "❌ Archive differs from current content"; \
	fi
	@rm -rf extract

test:
	@uv run pytest
