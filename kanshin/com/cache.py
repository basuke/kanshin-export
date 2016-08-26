import boto3

s3 = boto3.resource('s3', region_name='us-west-2')
rip_bucket = s3.Bucket('raw.kanshin.rip')

def get_page(path):
    obj = rip_bucket.Object(path[1:])
    return (obj.content_type, obj.get()['Body'].read())

def save_page(path, content_type, content):
    obj = rip_bucket.Object(path[1:])
    obj.put(Body=content, ContentType=content_type, ACL='public-read')

def is_page_saved(path):
    obj = rip_bucket.Object(path[1:])

    try:
        obj.metadata # test if obj exists
    except:
        return False

    return True

