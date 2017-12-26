import pendulum
import time
import requests
import json
import os

userId = os.environ['ENHPASE_USER_ID']
key = os.environ['ENPHASE_KEY']
systemId = os.environ['ENPHASE_SYSTEM_ID']
# set tz code from http://www.localeplanet.com/java/en-AU/index.html
tzCode = os.environ['TIME_ZONE']
# free tier only allows so many requests per minute, space them out with delays
sleepBetweenRequests = int(os.environ['SLEEP_BETWEEN_REQUESTS'])
# Start/end dates to export
startDate = pendulum.parse(os.environ["START_DATE"], tzinfo=tzCode)
endDate = pendulum.parse(os.environ["END_DATE"], tzinfo=tzCode)
# Shouldn't need to modify this
url = 'https://api.enphaseenergy.com/api/v2/systems/%s/stats' % systemId

print('Starting report between %s and %s' % (startDate.to_date_string(), endDate.to_date_string()))

period = pendulum.period(startDate, endDate)

for dt in period.range('days'):
    time.sleep(sleepBetweenRequests)

    print('date [%s]  START [%s] END [%s]' % (dt, dt.start_of('day'), dt.end_of('day')))
    # HTTP Params
    params = {'user_id': userId,
              'key': key,
              'datetime_format': 'iso8601',
              'start_at': dt.start_of('day').int_timestamp,
              'end_at': dt.end_of('day').int_timestamp}

    r = requests.get(url=url, params=params)

    if r.status_code == 200:
        filename = "out/%s.json" % dt.to_date_string()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as outfile:
            json.dump(r.json(), outfile, indent=2)
        print('Success %s' % dt.to_date_string())
    else:
        print('Failed to get data for %s' % dt.to_date_string())
