# python-enphase-export
=====

If you have an Enphase solar energy system and want to access your data, you can 
do so via the [Enphase developer APIs](https://developer.enphase.com/docs#stats).

There is rate limit on the free tier so if you want to compute stats you
may be better exporting the data to a relational data store, or heaven forbid, a spreadsheet!

This script will make it easier, just set your Enphase credentials, set the start/end date range you want
then go grab a coffee, your data will be saved to json files per day.

Stats exporter
=====
Use this script if you want to export your enphase stats to json files

Set the config in `.envrc.example`, either use direnv or just export the vars on your own.

Run using `python3 stats.py`

Have a look in the `out/` directory once the script has finished, you'll see
a json file per day, with the stats for that day.

Stats to Db
======
Use this if you want to export your enphase stats to RDS on AWS

build and package up the application:
`make build package`

Deploy the application into AWS
`make deploy`

TODO
=====
* Add other API calls, currently just power generation, I'd like consumption exports too
* Relation data store / export to AWS
* Run as an AWS scheduled lambda
