# Lambda script for twa-chatbot-fileUpload. The lambda script that takes in the initially uploaded excel file on the website and returns a list of questions (which are taken from the first row of the excel spreadsheet).
import json
import base64
from io import BytesIO
import pandas as pd

def lambda_handler(event, context):
    if 'body' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps('No file found in request.')
        }

    excel_base64 = event['body']

    # Attempt to decode the base64 string and create a BytesIO object
    try:
        excel_bytes = BytesIO(base64.b64decode(excel_base64))
    except base64.binascii.Error as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Base64 decode error: {str(e)}')
        }

    # Try to load the Excel file into a DataFrame, specifying the engine
    try:
        df = pd.read_excel(excel_bytes, engine='openpyxl', header=None)
        questionList = df.iloc[:, 0].tolist()

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error loading DataFrame: {str(e)}')
        }

    return {
        'statusCode': 200,
        'body': json.dumps(questionList)
    }


if __name__ == '__main__':
    df = pd.read_excel("code/file-upload/test.xlsx", engine='openpyxl', header=None)

    # lambda test code once got df:
    questionList = df.iloc[:, 0].tolist()
    print(json.dumps(questionList))

