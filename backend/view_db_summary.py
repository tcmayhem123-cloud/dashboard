import pymongo

MONGO_URI = "mongodb://localhost:27017"

try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    # Ping to check connection
    client.admin.command('ping')
    print("=== Connected to MongoDB Server successfully ===")
    
    # List databases of interest
    dbs_to_show = ["file_DB", "auth_DB", "user_DB", "ai_tools"]
    
    for db_name in dbs_to_show:
        print(f"\nDatabase: {db_name}")
        db = client[db_name]
        collections = db.list_collection_names()
        
        if not collections:
            print("  (No collections found)")
            continue
            
        for coll_name in collections:
            coll = db[coll_name]
            count = coll.count_documents({})
            print(f"  - Collection: {coll_name} ({count} documents)")
            
            # Print one sample document if database is not empty
            if count > 0:
                sample = coll.find_one()
                # Clean ObjectId and datetime for prettier printing
                formatted_sample = {k: str(v) if not isinstance(v, (dict, list, str, int, float, bool)) else v for k, v in sample.items()}
                # Truncate lists/dicts if too large
                for k, v in formatted_sample.items():
                    if isinstance(v, list) and len(v) > 2:
                        formatted_sample[k] = v[:2] + [f"... and {len(v)-2} more items"]
                print(f"    Sample Document: {formatted_sample}")
                
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    print("Please make sure MongoDB is running on port 27017.")
