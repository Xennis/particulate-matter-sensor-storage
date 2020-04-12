GCP_REGION = europe-west1

deploy:
	gcloud functions deploy pm_sensor_storage \
		--runtime python37 \
		--trigger-http \
		--region $(GCP_REGION)

check: format-check unittest

unittest:
	python -m unittest discover -p '*_test.py'

format-check:
	black --check --target-version py38 --line-length 132 *.py

format:
	black --target-version py38 --line-length 132 *.py
