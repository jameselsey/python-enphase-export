import pendulum
import time
import requests
import os
import MySQLdb
import logging
from warnings import filterwarnings




def lambda_handler(event, context):

    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    logger.info("Entered lambda_handler")

    # Ingore DB warnings, likely duplicates
    filterwarnings('ignore', category = MySQLdb.Warning)


    conn = MySQLdb.Connection(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        passwd=os.environ['DB_PASSWORD'],
        port=int(os.environ['DB_PORT']),
        db=os.environ['DB_NAME']
    )

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


    logger.info('Starting report between %s and %s', startDate.to_date_string(), endDate.to_date_string())

    period = pendulum.period(startDate, endDate)

    for dt in period.range('days'):
        time.sleep(1)

        logger.info('Requesting stats for date [%s] START [%s] END [%s]', dt, dt.start_of('day'), dt.end_of('day'))
        # HTTP Params
        params = {'user_id': userId,
                  'key': key,
                  'datetime_format': 'iso8601',
                  'start_at': dt.start_of('day').int_timestamp,
                  'end_at': dt.end_of('day').int_timestamp}

        r = requests.get(url=url, params=params, timeout=5)

        dailyIntervals = []
        if r.status_code == 200:
            logger.info('Got data for %s', dt.to_date_string())

            for interval in r.json()['intervals']:
                logger.debug('Processing interval %s %s', r.json()['system_id'], interval['end_at'])

                systemId = r.json()['system_id']
                endAt = pendulum.parse(interval['end_at']).to_datetime_string()
                devicesReporting = interval['devices_reporting']
                powr = interval['powr']
                enwh = interval['enwh']
                thisInterval = (endAt, systemId, devicesReporting, powr, enwh)
                dailyIntervals.append(thisInterval)
        else:
            logger.error('Failed to get data for %s, response code %s and body %s', dt.to_date_string(), r.status_code, r.text)


        logger.info('Inserting %s rows for %s', len(dailyIntervals), dt.to_date_string())
        # print(dailyIntervals)
        x = conn.cursor()
        try:
            sql = "INSERT IGNORE INTO stats (end_at, system_id, devices_reporting, powr, enwh) VALUES (%s,%s,%s,%s,%s)"
            # print(sql % dailyIntervals)
            x.executemany(sql, dailyIntervals)
            conn.commit()
            logger.info('Inserted %s rows for %s', len(dailyIntervals), dt.to_date_string())
        except Exception as e:
            logger.error('Got exception inserting %s %s', dt.to_date_string(), e)
            # print(x._last_executed)
            conn.rollback()

    conn.close()

#  This is so you can run it locally using: python3 stats_to_db.py
if __name__ == "__main__":
    lambda_handler("Test Event", "Test Context")