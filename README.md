# CodeHateChallenge

## Backend

In order to run backend, use:

```
docker-compose up
```

There are 3 APIs available:
* /ping - check if service is alive
* /ishate - checkt if input text is hateful
* /whyhate - obtain explanation for hateful paragraphs

To send API request from CLI, use:

```
curl -X POST -H "Content-Type: text/plain" --data "sample text" -v localhost:8080/ishate
curl -X POST -H "Content-Type: text/plain" --data "sample text" -v localhost:8080/whyhate
curl -X GET localhost:8080/ping
```
