GCP_REGION = europe-west1

deploy:
	gcloud functions deploy pm_sensor_storage \
		--runtime python37 \
		--trigger-http \
		--region $(GCP_REGION)
