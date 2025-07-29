try:
    import pinecone
    print("Pinecone installed successfully")
except ImportError:
    print("Pinecone not installed")

try:
    import neo4j
