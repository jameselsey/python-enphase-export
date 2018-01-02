# Update this to give whichever name you want. This may be set on the command line:
# > make build OUT_FILE=./outfile.zip
ZIP_FILE_NAME?=./node-importer.zip

ZIP_FILE_FQN=$(abspath $(ZIP_FILE_NAME))

# Install all the libs locally
install:
	pipenv install --three

# Destroy the virtualenv
uninstall:
	pipenv --rm

# Run the import
run:
	pipenv run python ./stats_to_db.py

clean:
	rm -f ${ZIP_FILE_FQN}

# Package up the application & environment into a zip file
build:
	$(eval VENV = $(shell pipenv --venv))
	cd ${VENV}/lib/python3.6/site-packages && zip -r9 ${ZIP_FILE_FQN} ./*
	zip -r9 ${ZIP_FILE_FQN} *.py

package:
	aws cloudformation package \
		--template-file cloudformation.yml \
		--output-template-file cloudformation.out.yaml \
		--s3-bucket iotdb-bucket \
		--s3-prefix sam \
		--profile jameselsey

deploy:
	aws cloudformation deploy \
		--template-file cloudformation.out.yaml \
		--stack-name iot-stack \
		--capabilities CAPABILITY_IAM \
		--profile jameselsey \
		--parameter-overrides \
			enphaseUserId=$(ENHPASE_USER_ID) \
			enphaseKey=$(ENPHASE_KEY) \
			enphaseSystemId=$(ENPHASE_SYSTEM_ID) \
			timezone=$(TIME_ZONE) \
			sleepBetweenRequests=$(SLEEP_BETWEEN_REQUESTS) \
			startDate=$(START_DATE) \
			endDate=$(END_DATE) \
			dbUser=$(DB_USER) \
			dbPassword=$(DB_PASSWORD) \
			dbPort=$(DB_PORT) \
			dbName=$(DB_NAME)

delete:
	aws cloudformation delete-stack --stack-name iot-stack --profile jameselsey

local:
	python3 stats_to_db.py