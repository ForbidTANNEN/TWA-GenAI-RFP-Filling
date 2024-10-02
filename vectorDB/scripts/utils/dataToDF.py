import os
import pandas as pd

#---Gets text from a directory or file into a pandas DF
def dataToDF(givenFilePath) -> pd.DataFrame:
    data = []
    #if given directory
    if os.path.isdir(givenFilePath):
        for filename in os.listdir(givenFilePath):
            if filename.endswith('.txt'):
                file_path = os.path.join(givenFilePath, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    # Add file content and filename to the list
                    data.append({'filename': filename, 'text': text})
    #if given file
    else:
        with open(givenFilePath, 'r', encoding='utf-8') as file:
            text = file.read()
            # Add file content and filename to the list
            data.append({'filename': os.path.basename(givenFilePath), 'text': text})
    return pd.DataFrame(data)