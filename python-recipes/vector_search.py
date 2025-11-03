import numpy as np
import pandas as pd
from redis import Redis
from redisvl.extensions.cache.embeddings import EmbeddingsCache
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery, RangeQuery, VectorRangeQuery, TextQuery, HybridQuery
from redisvl.query.filter import Tag, Num, Text
from redisvl.schema import IndexSchema
from redisvl.utils.vectorize import HFTextVectorizer
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def get_schema(client):
    index_name = "movies"

    schema = IndexSchema.from_dict({
        "index": {
            "name": index_name,
            "prefix": index_name,
            "storage_type": "hash"
        },
        "fields": [
            {
                "name": "title",
                "type": "text",
            },
            {
                "name": "description",
                "type": "text",
            },
            {
                "name": "genre",
                "type": "tag",
                "attrs": {
                    "sortable": True
                }
            },
            {
                "name": "rating",
                "type": "numeric",
                "attrs": {
                    "sortable": True
                }
            },
            {
                "name": "vector",
                "type": "vector",
                "attrs": {
                    "dims": 384,
                    "distance_metric": "cosine",
                    "algorithm": "flat",
                    "datatype": "float32"
                }
            }
        ]
    })

    index = SearchIndex(schema, client)
    index.create(overwrite=True, drop=True)
    return index

def run(client):


    df = pd.read_json("vector-search/resources/movies.json")
    print("Loaded", len(df), "movie entries")

    hf=HFTextVectorizer(
        model="sentence-transformers/all-MiniLM-L6-v2",
        cache = EmbeddingsCache(
            name="embedcache",
            ttl=600,
            redis_client=client,
        )
    )
    df["vector"] = hf.embed_many(df["description"].tolist(), as_buffer=True)

    index=get_schema(client)
    x = 2
    index.load(df.to_dict(orient="records"))

    # querying

    user_query="Action movie with high tech"
    embedded_user_query = hf.embed(user_query)
    vec_query = VectorQuery(
       vector=embedded_user_query,
        vector_field_name="vector",
        num_results=5,
        return_fields=["title", "genre", "rating"],
        return_score=True,
    )
    results=index.query(vec_query)
    [print(x) for x in results]
    print(1)
    # Vector search with filters
    tag_filter=Tag("genre") == "action"
    num_filter = Num("rating") >= 8
    combined_filter=tag_filter & num_filter
    vec_query.set_filter(combined_filter)
    results=index.query(vec_query)
    [print(x) for x in results]

    print(2)
    # query with text search
    text_filter=Text("description") % "hero"
    vec_query.set_filter(text_filter)
    results=index.query(vec_query)
    [print(x) for x in results]


    print(3)

    text_filter = Text("description") % "%thermopoli%"

    vec_query = VectorQuery(
        vector=embedded_user_query,
        vector_field_name="vector",
        num_results=3,
        return_fields=["title", "rating", "genre", "description"],
        return_score=True,
        filter_expression=text_filter
    )

    results = index.query(vec_query)
    [print(x) for x in results]
    print(4)
    # range queries
    user_query = "Family friendly super hero movies"
    embedded_query = hf.embed(user_query)
    tag_filter = Tag("genre") == "action"
    num_filter = Num("rating") >= 8
    combined_filter = tag_filter & num_filter
    range_query = VectorRangeQuery(
        vector=embedded_query,
        vector_field_name="vector",
        return_fields=["title", "rating", "genre"],
        return_score=True,
        distance_threshold=0.8,
        filter_expression=combined_filter
    )

    results = index.query(range_query)
    [print(x) for x in results]
    print(5)
    user_query="das High tech, action packed, superheros mit fight scenes"
    # Full text search
    text_query=TextQuery(
        text=user_query,
        text_field_name="description",
        text_scorer="BM25STD",
        num_results=10,
        return_fields=["title", "description"],
        stopwords="german"
    )
    results = index.query(text_query)
    [print(x) for x in results]
    print(6)
    # Hybrid search
    user_query="Family movie with action scenes"
    embedded_user_query = hf.embed(user_query)
    hybrid_query=HybridQuery(
        text=user_query,
        text_field_name="description",
        vector=embedded_user_query,
        vector_field_name="vector",
        return_fields=["title", "description"],
        num_results=10,
        alpha=0.7, # 70% emphasis on vector similarity and 30% on text
        # stopwords="english"
    )
    """
    FT.SEARCH movies 
    "(@description:user_query_text) => {$weight: 0.3} [KNN 10 @vector $vector_blob
    AS vector_score]"
    PARAMS 2 vector_blob <encoded_vector_bytes>
    RETURN 6 title description vector_score
    SORTBY vector_score ASC
    LIMIT 0 10
    """
    results = index.query(hybrid_query)
    [print(x) for x in results]


if __name__=="__main__":


    client = Redis.from_url("redis://localhost:6379")
    # index= SearchIndex.from_dict(schema, redis_client=client, validate_on_load=True)
    # alternative: index = SearchIndex.from_dict(schema, redis_url="redis://localhost:6379", validate_on_load=True)
    run(client)





