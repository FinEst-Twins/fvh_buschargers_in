To bring up service:

Note: the environment variables file config.env must be at root folder and the ssl root cert (pem file) should be in folder /platform_in

dev config (flask dev server):

docker-compose up
send POST requests to localhost:5000/peoplecounter/v1/ with xml data
should return success or failure response
prod config (nginx+gunicorn)

docker-compose -f docker-compose.prod.yml up
2,3,4 same as previous but port for prod is 1337

example POST data:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<EventNotificationAlert version="1.0" xmlns="urn:psialliance-org">
<ipAddress>10.60.108.22</ipAddress>
<protocolType>HTTP</protocolType>
<macAddress>44:47:cc:50:00:c1</macAddress>
<channelID>1</channelID>
<dateTime>2020-04-19T19:35:00+02:00</dateTime>
<activePostCount>1560</activePostCount>
<eventType>PeopleCounting</eventType>
<eventState>active</eventState>
<eventDescription>peopleCounting alarm</eventDescription>
<channelName>Camera 01</channelName>
<peopleCounting>
<statisticalMethods>timeRange</statisticalMethods>
<TimeRange>
<startTime>2020-04-19T19:33:00+02:00</startTime>
<endTime>2020-04-19T19:35:00+02:00</endTime>
</TimeRange>
<enter>0</enter>
<exit>0</exit><pass>0</pass>
</peopleCounting>
</EventNotificationAlert>
```
