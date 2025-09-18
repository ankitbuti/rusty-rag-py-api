import os
import weaviate
from weaviate.classes.init import Auth
import weaviate.classes as wvc
import weaviate.classes.config as wc

WEAVIATE_CLUSTER_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')
MODEL = "Snowflake/snowflake-arctic-embed-l-v2.0"

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_CLUSTER_URL,
    auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
)

client.collections.delete(name="crates")
print(client.is_connected())

client.collections.create(
    name="crates",
    vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_weaviate(model=MODEL),
    generative_config=wvc.config.Configure.Generative.friendliai(model="meta-llama-3.3-70b-instruct"),
    properties=[
        wc.Property(name="name", data_type=wc.DataType.TEXT),
        wc.Property(name="readme", data_type=wc.DataType.TEXT),
        wc.Property(name="description", data_type=wc.DataType.TEXT),
        wc.Property(name="repository", data_type=wc.DataType.TEXT, skip_vectorization=True)
    ]
)

client.close()
