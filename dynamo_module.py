import boto3
import pandas as pd
from botocore.exceptions import ClientError

def scan_table(table_name):
    response = dynamodb.scan(TableName=table_name)
    items = response['Items']
    unwrapped_data = []

    for item in items:
        unwrapped_item = {}
        for key, value in item.items():
            data_type, real_value = next(iter(value.items()))
            real_value = real_value.strip()
            unwrapped_item[key] = real_value
        unwrapped_data.append(unwrapped_item)
    return unwrapped_data

def get_sku_count(table_name, primary_key):
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=primary_key
        )
        
        item = response.get('Item')
        if item and 'sku_count' in item and 'N' in item['sku_count']:
            sku_count = int(item['sku_count']['N'])
            return sku_count
        else:
            raise ValueError("Invalid or missing 'sku_count' in the response.")
    except Exception as e:
        print("Error getting 'sku_count':", e)
        return None
    
def get_codename(table_name, primary_key):
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=primary_key
        )
        
        item = response.get('Item')
        if item and 'product_codename' in item and 'S' in item['product_codename']:
            codename = item['product_codename']['S']
            return codename
        else:
            raise ValueError("Invalid or missing 'product_codename' in the response.")
    except Exception as e:
        print("Error getting 'product_codename':", e)
        return None
    
def get_product_data(table_name, product_codename):
    try:
        response = dynamodb.scan(
            TableName=table_name,
            ExpressionAttributeNames={
                '#DT': 'Datetime',
                '#PC': 'Product_count',
            },
            ProjectionExpression='#DT, #PC',
            FilterExpression='Product_codename = :codename',
            ExpressionAttributeValues={
                ':codename': {'S': product_codename}
            }
        )
        
        items = response.get('Items', [])

        unwrapped_data = []
        for item in items:
            unwrapped_item = {}
            for key, value in item.items():
                data_type, real_value = next(iter(value.items()))
                real_value = real_value.strip()
                unwrapped_item[key] = real_value
            unwrapped_data.append(unwrapped_item)
        return unwrapped_data
    
    except Exception as e:
        print("Error scanning data:", e)
        return []
    
def check_key(table_name, primary_key):
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=primary_key
        )
        return 'Item' in response
    except ClientError as e:
        print("Error checking if key exists:", e)
        return False

def add_item(table_name, item_data, primary_key):
    try:
        if check_key(table_name, primary_key):
            print("Error: Duplicate key - item already exists.")
        else:
            response = dynamodb.put_item(
                TableName=table_name,
                Item=item_data
            )
            print("Item added successfully:", response)
    except Exception as e:
        print("General error adding item:", e)

def delete_item(table_name, primary_key):
    try:
        if check_key(table_name, primary_key):
            # if not get_sku_count(table_name,key):
                response = dynamodb.delete_item(
                    TableName=table_name,
                    Key=primary_key
                )
                print("Item deleted successfully:", response)
            # else:
            #     print("Error: SKU is still available.")
        else:
            print("Error: Item not found - key does not exist.")
    except Exception as e:
        print("Error deleting item:", e)

if __name__ == '__main__':

    # dynamodb = boto3.client('dynamodb', region_name='us-west-2')

    # table_name = 'BRD_final_proj_products'
    
    # prod_data = scan_table(table_name)
    # df = pd.DataFrame(prod_data)
    # print(prod_data)

    item_data = {
        'product_name': {'S': 'DEL MONTE FIT AND RIGHT FOUR SEASONS 340ML'},
        'sku_count': {'N': '125'},
        'product_id': {'S': '4800024570024'}
    }
    key = "product_id"
    key_value = "4800024570024"
    primary_key = {
        key: {'S': key_value}
    }
    # print(check_key(table_name, key))
    # print(get_sku_count(table_name, primary_key))

    # add_item(table_name, item_data, primary_key)

    # delete_item(table_name, primary_key)

    # prod_data = scan_table(table_name)
    # df = pd.DataFrame(prod_data)
    # print(df)
    # prod_ids = df['product_id'].tolist()

    # prod_codenames = [get_codename(table_name, {key: {'S':  id}}) for id in prod_ids]
    # print(prod_codenames)
    
    dynamodb = boto3.client('dynamodb', region_name='us-west-2')

    table_name = 'BRD_final_proj_logs'
    product_codename = 'person'

    result = get_product_data(table_name, product_codename)
    df = pd.DataFrame(result)
    print(df)