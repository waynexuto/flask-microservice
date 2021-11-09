##Endpoints
- GET /incidents (Basic Auth，given username password) get grouped incident by employee id
- GET /shutdown (Basic Auth，given username password) shutdown server

Eg.
- curl --location --request GET 'http://localhost:9000/incidents' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic changeit' \
--data-raw ''

- curl --location --request GET 'http://localhost:9000/shutdown' \
--header 'Authorization: Basic changeit'

##Config settings in config.yaml
ID/Password (change below before run docker build and start server, otherwise REST service won't work)
- SERVICE_ID: 'changeit'
- SERVICE_PASSWORD: 'changeit'

Cache refresh every 60 sec in background task run
- DEFAULT_CACHE_REFRESH: 60

Rate limits for APIs
- DEFAULT_RATE_LIMITS:
    '5 per second'
    '1000 per day'
- INCIDENTS_API_RATE_LIMITS: '20 per minute'

ThreadPool, max threads
- EXECUTOR_MAX_WORKERS: 10

##Build dependencies
    Python==3.7
    Docker==20.10.8
    
    fakeredis==1.6.1
    Flask==2.0.2
    Flask_APScheduler==1.12.2
    Flask_Caching==1.10.1
    Flask_Executor==0.10.0
    Flask_HTTPAuth==4.5.0
    Flask_Limiter==1.4
    jsonify==0.5
    PyYAML==6.0
    requests==2.26.0
    urllib3==1.26.7
    tzlocal==2.1
    redis==3.5.3

##How to run
- change username password in ./config/config.yaml, otherwise app won't work if not changed
- build and start rest api service (1st time running, run "up" to build)
    * docker-compose up
- shutdown rest api service
    * docker-compose down
    * or press Control^C twice in terminal
- start existing rest api service
    * docker-compose start
- check if both (redis and web) containers are up
    * docker-compose ps

##Sample Result
```
{
    "86": {
        "low": {
            "count": 0,
            "incidents": []
        },
        "medium": {
            "count": 0,
            "incidents": []
        },
        "high": {
            "count": 1,
            "incidents": [
                {
                    "type": "unauthorized",
                    "priority": "high",
                    "employee_id": 86,
                    "timestamp": 1636345473.350294
                }
            ]
        },
        "critical": {
            "count": 0,
            "incidents": []
        }
    },
    "775": {
        "low": {
            "count": 0,
            "incidents": []
        },
        "medium": {
            "count": 0,
            "incidents": []
        },
        "high": {
            "count": 0,
            "incidents": []
        },
        "critical": {
            "count": 1,
            "incidents": [
                {
                    "type": "other",
                    "priority": "critical",
                    "identifier": "17.55.3.214",
                    "timestamp": 1636364637.4511056
                }
            ]
        }
    },
    "3128": {
        "low": {
            "count": 1,
            "incidents": [
                {
                    "type": "probing",
                    "priority": "low",
                    "ip": "17.247.191.125",
                    "timestamp": 1636289243.5612853
                }
            ]
        },
        "medium": {
            "count": 0,
            "incidents": []
        },
        "high": {
            "count": 0,
            "incidents": []
        },
        "critical": {
            "count": 0,
            "incidents": []
        }
    }
}
```


##System design
- microservice contains mainly 3 parts
    * redis, cache system 
    * main rest service to handle incoming requests
    * background task runner, querying upstream endpoints, perform recalculation and refresh cache
- redis stores cached calculated results
    increase responsiveness to ~ 50ms to 500ms (less than 1 sec)
    avoid recalculation with in scheduled time interval
- system mainly has 2 performance bottlenecks, reduce wait time by multi-threading below 2 parts
    * Network I/O bounded, parallel data extracts from multiple upstream endpoints
    * CPU bounded, parallel data processing/grouping for each incident type
- first request after server startup tend to be slow since no cache available, and subsequent requests will return immediately from cache
- cache refreshes every min (or certain time interval) in the background, to provide more update to date data, push model is more appropriate compare to pull, since app
requires quick response, data pre-processing allows data gets ready before downstream pull request comes
- heapsort to give correct ordering of JSON output
- rate limit to protect server from overloading
- for demo purpose, password is stored as plain for now, in production this will required to hashed as secrete key

##Production Enhance
- add NoSQL DB and persist cache data into NoSQL DB periodically, increase reliability and availability, so cache data is immediately available (recover from DB) when server is recovered from a crash, increase server responsiveness
- have replica nodes and load balancer to reduce single point of failure on cache, rest service, to redirect network traffic to multiple nodes to perform business logic
- develop heartbeat functionality for all replica nodes, send heartbeat message periodically to master/monitor node to detect hanging/offline nodes
- use kubernetes to automate deployment and scaling along with docker in production environment
- have kubernetes secrets to manage user password and credentials
- decouple scheduled background task runner to become a independent microservice to allow reliability and scalability, communicate via independent message queue
- data sharding and data replication using consistent hashing are required, if need to save historical snapshots of upstream raw data
- increase test coverage, add more unit/integration test for regression test cases
- better encryption logic to protect username and password
