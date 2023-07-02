format:
	python -m black .
	python -m isort . 

start:
	python service.py

zip_lambda:
	./lambda/bin/zip_lambda.sh
