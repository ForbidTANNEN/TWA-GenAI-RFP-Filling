from pinecone import Pinecone
from lambdaFunctions.llmRetrieval.utils.properties import Properties

config = Properties()
PINECONE_API_KEY = config.PINECONE_API_KEY

pc = Pinecone(api_key=PINECONE_API_KEY)



def upsert_data(index, all_data):
    for namespace, ids_info in all_data.items():
        print(f"Processing namespace: {namespace} with {len(ids_info)} entries.")
        vectors_to_upsert = [(id, info['embedding'], info['metadata']) for id, info in ids_info.items() if
                             'embedding' in info and 'metadata' in info]
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            index.upsert(vectors=batch, namespace=namespace)
            print(f"Upserted batch {i // batch_size + 1} in namespace '{namespace}'")




if __name__ == '__main__':
    target_index_name = 'twa-chatbot2'
    index = pc.Index(target_index_name)

    # Path to your text file
    file_path = 'dbBackup.txt'

    # Read the content of the file
    with open(file_path, 'r') as file:
        dictionary_string = file.read()

    # Convert the string to a dictionary
    all_data = eval(dictionary_string)['']

    upsert_data(index, all_data)




