import pandas as pd
from ibm_botocore.client import Config
import ibm_boto3
from IBM_WATSON_CRED import credentials_1


#client object w/ relevant credentials
client = ibm_boto3.client(service_name='s3',
    ibm_api_key_id = credentials_1['IBM_API_KEY_ID'],
    ibm_auth_endpoint= credentials_1['IBM_AUTH_ENDPOINT'],
    config=Config(signature_version='oauth'),
    endpoint_url= credentials_1['ENDPOINT'])

body = client.get_object(Bucket=credentials_1['BUCKET'],Key='sp201710.csv')['Body']
# # add missing __iter__ method, so pandas accepts body as file-like object
if not hasattr(body, "__iter__"): body.__iter__ = types.MethodType( __iter__, body )
df_0to1 = pd.read_csv(body, encoding='latin-1')
df_0to1.head()
