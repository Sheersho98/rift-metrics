import boto3
import json
import os
from botocore.exceptions import ClientError

def get_secret(secret_name):
    #secret from aws secret manager
    region = os.getenv("AWS_REGION", "us-east-1")
    
    client = boto3.client('secretsmanager', region_name=region)
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret
    except ClientError as e:
        print(f"Error fetching secret: {e}")
        return None

def get_riot_api_key():
    # Try Secrets Manager first
    secrets = get_secret("rift-metrics/riot-api-key")
    if secrets and "RIOT_API_KEY" in secrets:
        return secrets["RIOT_API_KEY"]
    
    # Fallback to environment variable for local development
    return os.getenv("RIOT_API_KEY")