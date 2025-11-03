#!/usr/bin/env python3
"""
Vector Algorithm Benchmark: FLAT vs HNSW vs SVS-VAMANA

This script benchmarks FLAT, HNSW, and SVS-VAMANA vector search algorithms using 
real data from Hugging Face across different embedding dimensions.

What You'll Learn:
- Memory usage comparison across algorithms and dimensions
- Index creation performance with real text data
- Query performance and latency analysis
- Search quality with recall metrics on real embeddings
- Algorithm selection guidance based on your requirements

Benchmark Configuration:
- Dataset: SQuAD (Stanford Question Answering Dataset) from Hugging Face
- Algorithms: FLAT, HNSW, SVS-VAMANA
- Dimensions: 384, 768, 1536 (native sentence-transformer embeddings)
- Dataset Size: 1,000 documents per dimension
- Query Set: 50 real questions per configuration
- Focus: Real-world performance with actual text embeddings

Prerequisites:
- Redis Stack 8.2.0+ with RediSearch 2.8.10+
"""

# Import required libraries
import os
import json
import time
import psutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict

# Redis and RedisVL imports
import redis
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.redis.utils import array_to_buffer, buffer_to_array
from redisvl.utils import CompressionAdvisor
from redisvl.redis.connection import supports_svs

# Configuration
REDIS_URL = "redis://localhost:6379"
np.random.seed(42)  # For reproducible results

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

print("📚 Libraries imported successfully!")

# Benchmark configuration
@dataclass
class BenchmarkConfig:
    dimensions: List[int]
    algorithms: List[str]
    docs_per_dimension: int
    query_count: int
    
# Initialize benchmark configuration
config = BenchmarkConfig(
    dimensions=[384, 768, 1536],
    algorithms=['flat', 'hnsw', 'svs-vamana'],
    docs_per_dimension=1000,
    query_count=50
)

print(
    "🔧 Benchmark Configuration:",
    f"Dimensions: {config.dimensions}",
    f"Algorithms: {config.algorithms}",
    f"Documents per dimension: {config.docs_per_dimension:,}",
    f"Test queries: {config.query_count}",
    f"Total documents: {len(config.dimensions) * config.docs_per_dimension:,}",
    f"Dataset: SQuAD from Hugging Face",
    sep="\n"
)

def verify_redis_connection():
    """Test Redis connection and capabilities"""
    try:
        client = redis.Redis.from_url(REDIS_URL)
        client.ping()
        
        redis_info = client.info()
        redis_version = redis_info['redis_version']
        
        svs_supported = supports_svs(client)
        
        print(
            "✅ Redis connection successful",
            f"📊 Redis version: {redis_version}",
            f"🔧 SVS-VAMANA supported: {'✅ Yes' if svs_supported else '❌ No'}",
            sep="\n"
        )
        
        if not svs_supported:
            print("⚠️  SVS-VAMANA not supported. Benchmark will skip SVS tests.")
            config.algorithms = ['flat', 'hnsw']  # Remove SVS from tests
            
        return client
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("Please ensure Redis Stack is running on localhost:6379")
        raise

def load_squad_dataset(num_docs: int) -> List[Dict[str, Any]]:
    """Load SQuAD dataset from Hugging Face"""
    try:
        from datasets import load_dataset
        
        print("📥 Loading SQuAD dataset from Hugging Face...")
        
        # Load SQuAD dataset
        dataset = load_dataset("squad", split="train")
        
        # Take a subset for our benchmark
        dataset = dataset.select(range(min(num_docs, len(dataset))))
        
        # Convert to our format
        documents = []
        for i, item in enumerate(dataset):
            # Combine question and context for richer text
            text = f"{item['question']} {item['context']}"
            
            documents.append({
                'doc_id': f'squad_{i:06d}',
                'title': item['title'],
                'question': item['question'],
                'context': item['context'][:500],  # Truncate long contexts
                'text': text,
                'category': 'qa',  # All are Q&A documents
                'score': 1.0
            })
        
        print(f"✅ Loaded {len(documents)} documents from SQuAD")
        return documents
        
    except ImportError:
        print("⚠️  datasets library not available, falling back to local data")
        return load_local_fallback_data(num_docs)
    except Exception as e:
        print(f"⚠️  Failed to load SQuAD dataset: {e}")
        print("Falling back to local data...")
        return load_local_fallback_data(num_docs)

def load_local_fallback_data(num_docs: int) -> List[Dict[str, Any]]:
    """Fallback to local movie dataset if SQuAD is not available"""
    try:
        import json
        with open('resources/movies.json', 'r') as f:
            movies = json.load(f)
        
        # Expand the small movie dataset by duplicating with variations
        documents = []
        for i in range(num_docs):
            movie = movies[i % len(movies)]
            documents.append({
                'doc_id': f'movie_{i:06d}',
                'title': f"{movie['title']} (Variant {i // len(movies) + 1})",
                'question': f"What is {movie['title']} about?",
                'context': movie['description'],
                'text': f"What is {movie['title']} about? {movie['description']}",
                'category': movie['genre'],
                'score': movie['rating']
            })
        
        print(f"✅ Using local movie dataset: {len(documents)} documents")
        return documents
        
    except Exception as e:
        print(f"❌ Failed to load local data: {e}")
        raise

def generate_embeddings_for_texts(texts: List[str], dimensions: int) -> np.ndarray:
    """Generate embeddings for texts using sentence-transformers"""
    try:
        from sentence_transformers import SentenceTransformer
        
        # Choose model based on target dimensions
        if dimensions == 384:
            model_name = 'all-MiniLM-L6-v2'
        elif dimensions == 768:
            model_name = 'all-mpnet-base-v2'
        elif dimensions == 1536:
            # For 1536D, use gtr-t5-xl which produces native 1536D embeddings
            model_name = 'sentence-transformers/gtr-t5-xl'
        else:
            model_name = 'all-MiniLM-L6-v2'  # Default
        
        print(f"🤖 Generating {dimensions}D embeddings using {model_name}...")
        
        model = SentenceTransformer(model_name)
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        
        # Handle dimension adjustment
        current_dims = embeddings.shape[1]
        if current_dims < dimensions:
            # Pad with small random values (better than zeros)
            padding_size = dimensions - current_dims
            padding = np.random.normal(0, 0.01, (embeddings.shape[0], padding_size))
            embeddings = np.concatenate([embeddings, padding], axis=1)
        elif current_dims > dimensions:
            # Truncate
            embeddings = embeddings[:, :dimensions]
        
        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        
        print(f"✅ Generated embeddings: {embeddings.shape}")
        return embeddings.astype(np.float32)
        
    except ImportError:
        print(f"⚠️  sentence-transformers not available, using synthetic embeddings")
        return generate_synthetic_embeddings(len(texts), dimensions)
    except Exception as e:
        print(f"⚠️  Error generating embeddings: {e}")
        print("Falling back to synthetic embeddings...")
        return generate_synthetic_embeddings(len(texts), dimensions)

def generate_synthetic_embeddings(num_docs: int, dimensions: int) -> np.ndarray:
    """Generate synthetic embeddings as fallback"""
    print(f"🔄 Generating {num_docs} synthetic {dimensions}D embeddings...")
    
    # Create base random vectors
    embeddings = np.random.normal(0, 1, (num_docs, dimensions)).astype(np.float32)
    
    # Add some clustering structure
    cluster_size = num_docs // 3
    embeddings[:cluster_size, :min(50, dimensions)] += 0.5
    embeddings[cluster_size:2*cluster_size, min(50, dimensions):min(100, dimensions)] += 0.5
    
    # Normalize vectors
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms
    
    return embeddings

def load_and_generate_embeddings():
    """Load real dataset and generate embeddings"""
    print("🔄 Loading real dataset and generating embeddings...")

    # Load the base dataset once
    raw_documents = load_squad_dataset(config.docs_per_dimension)
    texts = [doc['text'] for doc in raw_documents]

    # Generate separate query texts (use questions from SQuAD)
    query_texts = [doc['question'] for doc in raw_documents[:config.query_count]]

    benchmark_data = {}
    query_data = {}

    for dim in config.dimensions:
        print(f"\n📊 Processing {dim}D embeddings...")
        
        # Generate embeddings for documents
        embeddings = generate_embeddings_for_texts(texts, dim)
        
        # Generate embeddings for queries
        query_embeddings = generate_embeddings_for_texts(query_texts, dim)
        
        # Combine documents with embeddings
        documents = []
        for i, (doc, embedding) in enumerate(zip(raw_documents, embeddings)):
            documents.append({
                **doc,
                'embedding': array_to_buffer(embedding, dtype='float32')
            })
        
        benchmark_data[dim] = documents
        query_data[dim] = query_embeddings

    print(
        f"\n✅ Generated benchmark data:",
        f"Total documents: {sum(len(docs) for docs in benchmark_data.values()):,}",
        f"Total queries: {sum(len(queries) for queries in query_data.values()):,}",
        f"Dataset source: {'SQuAD (Hugging Face)' if 'squad_' in raw_documents[0]['doc_id'] else 'Local movies'}",
        sep="\n"
    )
    
    return benchmark_data, query_data, raw_documents

def create_index_schema(algorithm: str, dimensions: int, prefix: str) -> Dict[str, Any]:
    """Create index schema for the specified algorithm"""

    base_schema = {
        "index": {
            "name": f"benchmark_{algorithm}_{dimensions}d",
            "prefix": prefix,
        },
        "fields": [
            {"name": "doc_id", "type": "tag"},
            {"name": "title", "type": "text"},
            {"name": "category", "type": "tag"},
            {"name": "score", "type": "numeric"},
            {
                "name": "embedding",
                "type": "vector",
                "attrs": {
                    "dims": dimensions,
                    "distance_metric": "cosine",
                    "datatype": "float32"
                }
            }
        ]
    }

    # Algorithm-specific configurations
    vector_field = base_schema["fields"][-1]["attrs"]

    if algorithm == 'flat':
        vector_field["algorithm"] = "flat"

    elif algorithm == 'hnsw':
        vector_field.update({
            "algorithm": "hnsw",
            "m": 16,
            "ef_construction": 200,
            "ef_runtime": 10
        })

    elif algorithm == 'svs-vamana':
        # Get compression recommendation
        compression_config = CompressionAdvisor.recommend(dims=dimensions, priority="memory")

        vector_field.update({
            "algorithm": "svs-vamana",
            "datatype": compression_config.get('datatype', 'float32')
        })

        # Handle dimensionality reduction for high dimensions
        if 'reduce' in compression_config:
            vector_field["dims"] = compression_config['reduce']

    return base_schema

def benchmark_index_creation(algorithm: str, dimensions: int, documents: List[Dict], client) -> Tuple[SearchIndex, float, float]:
    """Benchmark index creation and return index, build time, and memory usage"""

    prefix = f"bench:{algorithm}:{dimensions}d:"

    # Clean up any existing index
    try:
        client.execute_command('FT.DROPINDEX', f'benchmark_{algorithm}_{dimensions}d')
    except:
        pass

    # Create schema and index
    schema = create_index_schema(algorithm, dimensions, prefix)

    start_time = time.time()

    # Create index
    index = SearchIndex.from_dict(schema, redis_url=REDIS_URL)
    index.create(overwrite=True)

    # Load data in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        index.load(batch)

    # Wait for indexing to complete
    if algorithm == 'hnsw':
        time.sleep(3)  # HNSW needs more time for graph construction
    else:
        time.sleep(1)

    build_time = time.time() - start_time

    # Get index info for memory usage
    try:
        index_info = index.info()
        index_size_mb = float(index_info.get('vector_index_sz_mb', 0))
    except:
        index_size_mb = 0.0

    return index, build_time, index_size_mb

def run_index_creation_benchmarks(benchmark_data, client):
    """Run index creation benchmarks"""
    print("🏗️ Running index creation benchmarks...")

    creation_results = {}
    indices = {}

    for dim in config.dimensions:
        print(f"\n📊 Benchmarking {dim}D embeddings:")

        for algorithm in config.algorithms:
            print(f"  Creating {algorithm.upper()} index...")

            try:
                index, build_time, index_size_mb = benchmark_index_creation(
                    algorithm, dim, benchmark_data[dim], client
                )

                creation_results[f"{algorithm}_{dim}"] = {
                    'algorithm': algorithm,
                    'dimensions': dim,
                    'build_time_sec': build_time,
                    'index_size_mb': index_size_mb,
                    'num_docs': len(benchmark_data[dim])
                }

                indices[f"{algorithm}_{dim}"] = index

                print(
                    f"    ✅ {algorithm.upper()}: {build_time:.2f}s, {index_size_mb:.2f}MB"
                )

            except Exception as e:
                print(f"    ❌ {algorithm.upper()} failed: {e}")
                creation_results[f"{algorithm}_{dim}"] = None

    print("\n✅ Index creation benchmarks complete!")
    return creation_results, indices

def calculate_recall(retrieved_ids: List[str], ground_truth_ids: List[str], k: int) -> float:
    """Calculate recall@k between retrieved and ground truth results"""
    if not ground_truth_ids or not retrieved_ids:
        return 0.0

    retrieved_set = set(retrieved_ids[:k])
    ground_truth_set = set(ground_truth_ids[:k])

    if len(ground_truth_set) == 0:
        return 0.0

    intersection = len(retrieved_set.intersection(ground_truth_set))
    return intersection / len(ground_truth_set)

def benchmark_query_performance(index: SearchIndex, query_vectors: np.ndarray,
                               algorithm: str, dimensions: int, indices) -> Dict[str, float]:
    """Benchmark query performance and quality"""

    latencies = []
    all_results = []

    # Get ground truth from FLAT index (if available)
    ground_truth_results = []
    flat_index_key = f"flat_{dimensions}"

    if flat_index_key in indices and algorithm != 'flat':
        flat_index = indices[flat_index_key]
        for query_vec in query_vectors:
            query = VectorQuery(
                vector=query_vec,
                vector_field_name="embedding",
                return_fields=["doc_id"],
                dtype="float32",
                num_results=10
            )
            results = flat_index.query(query)
            ground_truth_results.append([doc["doc_id"] for doc in results])

    # Benchmark the target algorithm
    for i, query_vec in enumerate(query_vectors):
        # Adjust query vector for SVS if needed
        if algorithm == 'svs-vamana':
            compression_config = CompressionAdvisor.recommend(dims=dimensions, priority="memory")

            if 'reduce' in compression_config:
                target_dims = compression_config['reduce']
                if target_dims < dimensions:
                    query_vec = query_vec[:target_dims]

            if compression_config.get('datatype') == 'float16':
                query_vec = query_vec.astype(np.float16)
                dtype = 'float16'
            else:
                dtype = 'float32'
        else:
            dtype = 'float32'

        # Execute query with timing
        start_time = time.time()

        query = VectorQuery(
            vector=query_vec,
            vector_field_name="embedding",
            return_fields=["doc_id", "title", "category"],
            dtype=dtype,
            num_results=10
        )

        results = index.query(query)
        latency = time.time() - start_time

        latencies.append(latency * 1000)  # Convert to milliseconds
        all_results.append([doc["doc_id"] for doc in results])

    # Calculate metrics
    avg_latency = np.mean(latencies)

    # Calculate recall if we have ground truth
    if ground_truth_results and algorithm != 'flat':
        recall_5_scores = []
        recall_10_scores = []

        for retrieved, ground_truth in zip(all_results, ground_truth_results):
            recall_5_scores.append(calculate_recall(retrieved, ground_truth, 5))
            recall_10_scores.append(calculate_recall(retrieved, ground_truth, 10))

        recall_at_5 = np.mean(recall_5_scores)
        recall_at_10 = np.mean(recall_10_scores)
    else:
        # FLAT is our ground truth, so perfect recall
        recall_at_5 = 1.0 if algorithm == 'flat' else 0.0
        recall_at_10 = 1.0 if algorithm == 'flat' else 0.0

    return {
        'avg_query_time_ms': avg_latency,
        'recall_at_5': recall_at_5,
        'recall_at_10': recall_at_10,
        'num_queries': len(query_vectors)
    }

def run_query_performance_benchmarks(query_data, indices):
    """Run query performance benchmarks"""
    print("🔍 Running query performance benchmarks...")

    query_results = {}

    for dim in config.dimensions:
        print(f"\n📊 Benchmarking {dim}D queries:")

        for algorithm in config.algorithms:
            index_key = f"{algorithm}_{dim}"

            if index_key in indices:
                print(f"  Testing {algorithm.upper()} queries...")

                try:
                    performance = benchmark_query_performance(
                        indices[index_key],
                        query_data[dim],
                        algorithm,
                        dim,
                        indices
                    )

                    query_results[index_key] = performance

                    print(
                        f"    ✅ {algorithm.upper()}: {performance['avg_query_time_ms']:.2f}ms avg, "
                        f"R@5: {performance['recall_at_5']:.3f}, R@10: {performance['recall_at_10']:.3f}"
                    )

                except Exception as e:
                    print(f"    ❌ {algorithm.upper()} query failed: {e}")
                    query_results[index_key] = None
            else:
                print(f"  ⏭️  Skipping {algorithm.upper()} (index creation failed)")

    print("\n✅ Query performance benchmarks complete!")
    return query_results

def create_results_dataframe(creation_results, query_results) -> pd.DataFrame:
    """Combine all benchmark results into a pandas DataFrame"""

    results = []

    for dim in config.dimensions:
        for algorithm in config.algorithms:
            key = f"{algorithm}_{dim}"

            if key in creation_results and creation_results[key] is not None:
                creation_data = creation_results[key]
                query_data_item = query_results.get(key, {})

                result = {
                    'algorithm': algorithm,
                    'dimensions': dim,
                    'num_docs': creation_data['num_docs'],
                    'build_time_sec': creation_data['build_time_sec'],
                    'index_size_mb': creation_data['index_size_mb'],
                    'avg_query_time_ms': query_data_item.get('avg_query_time_ms', 0),
                    'recall_at_5': query_data_item.get('recall_at_5', 0),
                    'recall_at_10': query_data_item.get('recall_at_10', 0)
                }

                results.append(result)

    return pd.DataFrame(results)

def analyze_results(df_results, raw_documents):
    """Analyze and display benchmark results"""
    print("📊 Real Data Benchmark Results Summary:")
    print(df_results.to_string(index=False, float_format='%.3f'))

    # Display key insights
    if not df_results.empty:
        print(f"\n🎯 Key Insights from Real Data:")

        # Memory efficiency
        best_memory = df_results.loc[df_results['index_size_mb'].idxmin()]
        print(f"🏆 Most memory efficient: {best_memory['algorithm'].upper()} at {best_memory['dimensions']}D ({best_memory['index_size_mb']:.2f}MB)")

        # Query speed
        best_speed = df_results.loc[df_results['avg_query_time_ms'].idxmin()]
        print(f"⚡ Fastest queries: {best_speed['algorithm'].upper()} at {best_speed['dimensions']}D ({best_speed['avg_query_time_ms']:.2f}ms)")

        # Search quality
        best_quality = df_results.loc[df_results['recall_at_10'].idxmax()]
        print(f"🎯 Best search quality: {best_quality['algorithm'].upper()} at {best_quality['dimensions']}D (R@10: {best_quality['recall_at_10']:.3f})")

        # Dataset info
        dataset_source = 'SQuAD (Hugging Face)' if 'squad_' in raw_documents[0]['doc_id'] else 'Local movies'
        print(f"\n📚 Dataset: {dataset_source}")
        print(f"📊 Total documents tested: {df_results['num_docs'].iloc[0]:,}")
        print(f"🔍 Total queries per dimension: {config.query_count}")

def create_real_data_visualizations(df: pd.DataFrame):
    """Create visualizations for real data benchmark results"""

    if df.empty:
        print("⚠️  No results to visualize")
        return

    # Set up the plotting area
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Real Data Vector Algorithm Benchmark Results', fontsize=16, fontweight='bold')

    # 1. Memory Usage Comparison
    ax1 = axes[0, 0]
    pivot_memory = df.pivot(index='dimensions', columns='algorithm', values='index_size_mb')
    pivot_memory.plot(kind='bar', ax=ax1, width=0.8)
    ax1.set_title('Index Size by Algorithm (Real Data)')
    ax1.set_xlabel('Dimensions')
    ax1.set_ylabel('Index Size (MB)')
    ax1.legend(title='Algorithm')
    ax1.tick_params(axis='x', rotation=0)

    # 2. Query Performance
    ax2 = axes[0, 1]
    pivot_query = df.pivot(index='dimensions', columns='algorithm', values='avg_query_time_ms')
    pivot_query.plot(kind='bar', ax=ax2, width=0.8)
    ax2.set_title('Average Query Time (Real Embeddings)')
    ax2.set_xlabel('Dimensions')
    ax2.set_ylabel('Query Time (ms)')
    ax2.legend(title='Algorithm')
    ax2.tick_params(axis='x', rotation=0)

    # 3. Search Quality
    ax3 = axes[1, 0]
    pivot_recall = df.pivot(index='dimensions', columns='algorithm', values='recall_at_10')
    pivot_recall.plot(kind='bar', ax=ax3, width=0.8)
    ax3.set_title('Search Quality (Recall@10)')
    ax3.set_xlabel('Dimensions')
    ax3.set_ylabel('Recall@10')
    ax3.legend(title='Algorithm')
    ax3.tick_params(axis='x', rotation=0)
    ax3.set_ylim(0, 1.1)

    # 4. Memory Efficiency
    ax4 = axes[1, 1]
    df['docs_per_mb'] = df['num_docs'] / df['index_size_mb']
    pivot_efficiency = df.pivot(index='dimensions', columns='algorithm', values='docs_per_mb')
    pivot_efficiency.plot(kind='bar', ax=ax4, width=0.8)
    ax4.set_title('Memory Efficiency (Real Data)')
    ax4.set_xlabel('Dimensions')
    ax4.set_ylabel('Documents per MB')
    ax4.legend(title='Algorithm')
    ax4.tick_params(axis='x', rotation=0)

    plt.tight_layout()
    plt.show()

def generate_insights_and_recommendations(df_results, raw_documents):
    """Generate real data specific recommendations"""
    if not df_results.empty:
        dataset_source = 'SQuAD (Hugging Face)' if 'squad_' in raw_documents[0]['doc_id'] else 'Local movies'

        print(
            f"🎯 Real Data Benchmark Insights",
            f"Dataset: {dataset_source}",
            f"Documents: {df_results['num_docs'].iloc[0]:,} per dimension",
            f"Embedding Models: sentence-transformers",
            "=" * 50,
            sep="\n"
        )

        for dim in config.dimensions:
            dim_data = df_results[df_results['dimensions'] == dim]

            if not dim_data.empty:
                print(f"\n📊 {dim}D Embeddings Analysis:")

                for _, row in dim_data.iterrows():
                    algo = row['algorithm'].upper()
                    print(
                        f"  {algo}:",
                        f"    Index: {row['index_size_mb']:.2f}MB",
                        f"    Query: {row['avg_query_time_ms']:.2f}ms",
                        f"    Recall@10: {row['recall_at_10']:.3f}",
                        f"    Efficiency: {row['docs_per_mb']:.1f} docs/MB",
                        sep="\n"
                    )

        print(
            f"\n💡 Key Takeaways with Real Data:",
            "• Real embeddings show different performance characteristics than synthetic",
            "• Sentence-transformer models provide realistic vector distributions",
            "• SQuAD Q&A pairs offer diverse semantic content for testing",
            "• Results are more representative of production workloads",
            "• Consider testing with your specific embedding models and data",
            sep="\n"
        )
    else:
        print("⚠️  No results available for analysis")

def cleanup_indices(indices):
    """Clean up all benchmark indices"""
    print("🧹 Cleaning up benchmark indices...")

    cleanup_count = 0
    for index_key, index in indices.items():
        try:
            index.delete(drop=True)
            cleanup_count += 1
            print(f"  ✅ Cleaned up {index_key}")
        except Exception as e:
            print(f"  ⚠️  Failed to cleanup {index_key}: {e}")

    print(f"🧹 Cleanup complete! Removed {cleanup_count} indices.")

def main():
    """Main execution function"""
    print("🚀 Starting Vector Algorithm Benchmark with Real Data")
    print("=" * 60)

    # Step 1: Verify Redis connection
    print("\n## Step 1: Verify Redis and SVS Support")
    client = verify_redis_connection()

    # Step 2: Load real dataset and generate embeddings
    print("\n## Step 2: Load Real Dataset from Hugging Face")
    benchmark_data, query_data, raw_documents = load_and_generate_embeddings()

    # Step 3: Index creation benchmark
    print("\n## Step 3: Index Creation Benchmark")
    creation_results, indices = run_index_creation_benchmarks(benchmark_data, client)

    # Step 4: Query performance benchmark
    print("\n## Step 4: Query Performance Benchmark")
    query_results = run_query_performance_benchmarks(query_data, indices)

    # Step 5: Results analysis and visualization
    print("\n## Step 5: Results Analysis and Visualization")
    df_results = create_results_dataframe(creation_results, query_results)
    analyze_results(df_results, raw_documents)

    # Create visualizations
    create_real_data_visualizations(df_results)

    # Step 6: Generate insights and recommendations
    print("\n## Step 6: Real Data Insights and Recommendations")
    generate_insights_and_recommendations(df_results, raw_documents)

    # Step 7: Cleanup
    print("\n## Step 7: Cleanup")
    cleanup_indices(indices)

    print("\n🎉 Benchmark complete! Check the results above for insights.")
    return df_results

if __name__ == "__main__":
    main()
