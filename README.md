<img src="/images/readme.png" align="right" />

## CI-CD with DataOps platform

### Pre-requisites
1. [Install](https://docs.streamsets.com/platform-sdk/learn/installation.html) StreamSets SDK for Python 
2. [Install](https://docs.streamsets.com/stf/latest/installation.html) STF(StreamSets Test Framework)
3. Install STE(StreamSets Test Environment) ** optional if installing MySQL / ElasticSearch manually 
4. Jenkins

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
2. Create Docker network ** optional 
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
Table schema:
```
      CREATE TABLE `tour_de_france` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `year` int(11) DEFAULT NULL,
        `rank` int(11) DEFAULT NULL,
        `name` varchar(100) DEFAULT NULL,
        `number` int(11) DEFAULT NULL,
        `team` varchar(100) DEFAULT NULL,
        `time` varchar(100) DEFAULT NULL,
        `hours` int(11) DEFAULT NULL,
        `mins` int(11) DEFAULT NULL,
        `secs` int(11) DEFAULT NULL,
        PRIMARY KEY (`id`)
      ) AUTO_INCREMENT=1;
```
4. Create ElasticSearch instance
```
   ste start Elasticsearch_7.9.0 -p 9200:9200
```
5. Prepare Data Collector with necessary stage libs(jdbc,elasticsearch) and add "CICD-Demo" label
   - Alternatively please checkout [automated provisining](https://github.com/enterthematrix/dataops_provisioning) using StreamSets Python SDK. 

6. Import the [attached pipeline](https://github.com/enterthematrix/DataOps_CICD/blob/main/DataOps_CICD.json) OR create the pipeline using _create_demo_pipeline.py_

7. Create a subscription in the DataOps platform
<img src="/images/subscription.png" align="center"/>

8. Clone this repo and switch to it's HOME dir
   - Command to run the test manually:
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

9. Jenkins job setup:

    - Setup a new project(free-style)
    <img src="/images/jenkins_project.png" align="right"/>
   
   
   - Add project parameters 
   <img src="/images/project_params.png" align="right"/>

   
   - Configure GitHub repo for the tests
   <img src="/images/git_repo.png" align="right"/>

   
   - Configure a shell action under Build section
   <img src="/images/build_action.png" align="right"/>

   
   - Trigger the build using cURL ** Authentication options may vary depending upon Jenkins version

```
            # Trigger the Jenkins build 
            curl -u <jenkins-user>:<jenkins-api-token> -X POST http://<Jenkins-Server-URL>/job/<Job-Name>/buildWithParameters
```

10. With the above setup, a new commit on the pipeline will trigger a Webhook action to trigger the Jenkins job
    - If the "--upgrade-jobs" option is specified with the STF command, a successfull build will automatically upgrade the job to the latest version of the pipeline 
    - You optionally choose to upgrade the job manually 







