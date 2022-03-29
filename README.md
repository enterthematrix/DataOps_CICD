# Provisioning DataOps environment

### Pre-requisites
1. [Install](https://docs.streamsets.com/platform-sdk/learn/installation.html) StreamSets SDK for Python 
2. Install STF(StreamSets Test Framework)
3. Install STE(StreamSets Test Environment) ** optional if installing mysql/elasticsearch manually 

### Steps 

1. Create the following configuration files:

credentials.properties:
```
[DEFAULT]

[SECURITY]
CRED_ID=<SCH CRED_ID>
CRED_TOKEN=<SCH CRED_TOKEN>
```
deployment.conf:
```
[DEFAULT]
[DEPLOYMENT]
ENGINE_ID=<id>
ENGINE_TYPE=data_collector
```
2. Create Docker network
```
docker network create cluster
```
3. Create MySql instance
```
docker run -d -p 3306:3306 --net=cluster --name=MySQL_5.7  \
-e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=default -e MYSQL_USER=mysql \
-e MYSQL_PASSWORD=mysql  mysql:5.7

docker exec -i MySQL_5.7 mysql -uroot -proot default -e "GRANT ALL ON *.* TO 'mysql'@'%';FLUSH PRIVILEGES;"
```
4. Create ElasticSearch instance
```
ste start Elasticsearch_7.9.0 -p 9200:9200
```
5. Prepare Data Collector with necessary stage libs(jdbc,elasticsearch) and add "CICD-Demo" label
6. Import the attached pipeline OR create the pipeline using create_demo_pipeline.py
7. Clone this repo and switch to it's HOME dir
8. Command to run the test manually:
```
stf --docker-image streamsets/testframework-4.x:latest test -vs \
--sch-credential-id ${CRED_ID} --sch-token ${CRED_TOKEN} \
--sch-authoring-sdc '<SDC ID prepared in step #5>' \
--pipeline-id '<pipeline id created in step #6>' \
--sch-executor-sdc-label 'CICD-Demo' \
--database 'mysql://<mysql-host>:3306/default' \
--elasticsearch-url 'http://user:password@<elastic-host>:9200' \
test_tdf_data_to_elasticsearch.py
```
8. 
9. 






