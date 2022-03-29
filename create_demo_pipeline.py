import configparser
import time
import warnings

# Import the ControlHub class from the SDK.
from streamsets.sdk import ControlHub

start_time = time.time()
# sys.path.insert(1, os.path.abspath('/Users/sanjeev/SDK_4x'))
config = configparser.ConfigParser()
config.optionxform = lambda option: option
config.read('credentials.properties')
CRED_ID = config.get("SECURITY", "CRED_ID")
CRED_TOKEN = config.get("SECURITY", "CRED_TOKEN")

config.read('deployment.conf')
ENGINE_ID = config.get("DEPLOYMENT", "ENGINE_ID")
ENGINE_TYPE = config.get("DEPLOYMENT", "ENGINE_TYPE")

warnings.simplefilter("ignore")
# Connect to the StreamSets DataOps Platform.
control_hub = ControlHub(credential_id=CRED_ID, token=CRED_TOKEN)
builder = control_hub.get_pipeline_builder(engine_id=ENGINE_ID, engine_type=ENGINE_TYPE)
jdbc_query_consumer = builder.add_stage('JDBC Query Consumer')
dir(jdbc_query_consumer)
help(jdbc_query_consumer)
jdbc_query_consumer.set_attributes(jdbc_connection_string='${JDBC_CONNECTION_STRING}',
                                   offset_column='id',
                                   password='${JDBC_PASSWORD}',
                                   sql_query='SELECT * FROM ${TABLE_NAME} WHERE id > ${OFFSET} ORDER BY id',
                                   username='${JDBC_USERNAME}')
field_remover = builder.add_stage('Field Remover')

field_remover.fields = ['/id']
field_splitter = builder.add_stage('Field Splitter')

field_splitter.set_attributes(field_to_split='/name',
                              new_split_fields=["/firstName", "/lastName"])
jython_evaluator = builder.add_stage('Jython Evaluator')

jython_evaluator.set_attributes(init_script='',
                                destroy_script='',
                                record_processing_mode='RECORD',
                                script=("record = records[0]\n\n# JOHN => John.\n"
                                        "record.value['firstName'] = record.value['firstName'].title()\n\n"
                                        "# DOE  => Doe.\n"
                                        "record.value['lastName'] = record.value['lastName'].title()\n\n"
                                        "output.write(record)"))

elastic_search = builder.add_stage('Elasticsearch')

elastic_search.set_attributes(http_urls='${ELASTICSEARCH_URI}',
                              index='${ELASTICSEARCH_INDEX}',
                              mapping='tourdefrance',
                              password='${ELASTICSEARCH_PASSWORD}',
                              user_name='${ELASTICSEARCH_USERNAME}',
                              use_security=True)
# Connect the stages and build the pipeline
jdbc_query_consumer >> field_remover >> field_splitter >> jython_evaluator >> elastic_search

pipeline = builder.build('DataOps CI-CD pipeline')

pipeline.parameters = {'JDBC_CONNECTION_STRING': 'jdbc:mysql://10.10.52.163:3306/default',
                       'JDBC_USERNAME': 'mysql',
                       'JDBC_PASSWORD': 'mysql',
                       'ELASTICSEARCH_URI': 'http://10.10.52.163:9200',
                       'ELASTICSEARCH_USERNAME': 'elastic',
                       'ELASTICSEARCH_PASSWORD': 'changeme',
                       'TABLE_NAME': 'tour_de_france',
                       'ELASTICSEARCH_INDEX': 'tourdefrance'
                       }
# Add a label
pipeline.add_label('CI-CD-pipeline')

control_hub.publish_pipeline(pipeline)
