To bring up service:

Note: the environment variables file config.env must be at root folder and the ssl root cert (pem file) should be in folder /platform_in

dev config (flask dev server):

docker-compose up
send POST requests to localhost:5000/TODO/v1/ with xml data
should return success or failure response
prod config (nginx+gunicorn)

docker-compose -f docker-compose.prod.yml up
2,3,4 same as previous but port for prod is 1337

example POST data:

```
TODO
```
