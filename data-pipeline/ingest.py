import os
import sys
import csv
import weaviate
from weaviate.classes.init import Auth

WEAVIATE_CLUSTER_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_CLUSTER_URL,
    auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
)

crates = client.collections.get(name="crates")

try:
    reader = csv.reader(sys.stdin)

    for crate in reader:
        try:
            properties = {
                "name": crate[0],
                "readme": crate[1],
                "description": crate[2],
                "repository": crate[3],
            }
        except:
            continue

        uuid = crates.data.insert(properties)
        print(f"{crate[0]}: {uuid}", end='\n')
except Exception as e:
    raise e
finally:
    client.close()
