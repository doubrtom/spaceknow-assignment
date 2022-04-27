check-all:
	black --check sk_client
	pylint sk_client
	flake8 sk_client
	@echo "\033[0;32m == OK == \033[0m"
