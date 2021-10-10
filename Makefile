style:
	flake8 .

types:
	mypy bot

check:
	make style types