from __future__ import print_function
from datetime import datetime
import boto3
from dateutil import tz
import time


# ----------Used code---------

# stop_instance
def stop(ins):
    # ins is instance-id
    # "ec2" is ec2 object

    ec2 = boto3.resource('ec2')
    # "instance" points to ins
    instance = ec2.Instance(ins)
    instance.stop()


# start_instance
def start(ins):
    print("in start")
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(ins)
    instance.start()
    # wait till the instance starts
    print("waiting....")
    time.sleep(220)
    # if even now instance doesn't start.. wait till its state becomes running
    while (1):

        # chck instance state (instance.state returns dictionary thus check for value corresponding to "Name" ..it returns "stopped" or "pending" or "running")

        if (instance.state['Name'] == 'running'):
            print(instance.state['Name'])
            # break if its running
            break
        else:
            print(instance.state['Name'])
            continue


# update_service_task_count
def update_inc(id):
    # "dynamodb" is dynamod's object
    dynamodb = boto3.resource('dynamodb')

    # "table" points to our ECSOrchestration table
    table = dynamodb.Table('ECSOrchestration')

    # "ecs" is ecs object
    ecs = boto3.client('ecs')

    # id 1 implies 1st instance
    if (id == 1):
        # get row for time=9
        response = table.get_item(Key={'time': '9am'})

        # item is row,ins is instance id
        item = response['Item']

        # ins is instance id
        ins = item['ins_id']

        # call start to start the instance first
        start(ins)
        time.sleep(10)

        # inc task-count to 1 for Final service.. since initially there was no service , count was 0 , we can directly increment count to 1
        ecs.update_service(service='Final', desiredCount=1)

        # set stat to on
        table.update_item(Key={'time': '9am'}, UpdateExpression='SET stat = :val1',
                          ExpressionAttributeValues={':val1': 'on'})

    # id 2 implies 2nd instance
    elif (id == 2):
        # get row for 11am
        response = table.get_item(Key={'time': '11am'})

        # item is row
        item = response['Item']

        # ins is instance id
        ins = item['ins_id']

        # starts the instance
        start(ins)
        time.sleep(5)

        # inc task-count to 1 for Final service.. since initially there was no service , count was 0 , we can directly increment count to 1
        ecs.update_service(service='Final', desiredCount=2)

        # set stat to on
        table.update_item(Key={'time': '9am'}, UpdateExpression='SET stat = :val1',
                          ExpressionAttributeValues={':val1': 'on'})


def update_dec(id):
    # "dynamodb" is dynamodb's object
    dynamodb = boto3.resource('dynamodb')

    # table points to ECSOrchestration table
    table = dynamodb.Table('ECSOrchestration')

    # ecs object
    ecs = boto3.client('ecs')

    # id=1 implies 1st instance
    if (id == 1):
        # get row for 6pm
        response = table.get_item(Key={'time': '6pm'})

        # item is the row
        item = response['Item']

        # container_id
        container_id = item['container']

        # ins is instane id
        ins = item['ins_id']

        # get task_id from container_id
        task_id = ecs.list_tasks(containerInstance=container_id)['taskArns'][0].split('/')[1]

        # stop the task
        ecs.stop_task(task=task_id)

        # dec service count from 2 to 1
        ecs.update_service(cluster='default', service="Final", desiredCount=1)

        # set stat to off
        table.update_item(Key={'time': '9am'}, UpdateExpression='SET stat = :val1',
                          ExpressionAttributeValues={':val1': 'off'})

        # stop the instance with instance id ins
        stop(ins)

    elif (id == 2):
        # get row for 8pm
        response = table.get_item(Key={'time': '8pm'})

        # item is the row
        item = response['Item']

        # container_id
        container_id = item['container']

        # ins is instane id
        ins = item['ins_id']

        # get task_id from container_id
        task_id = ecs.list_tasks(containerInstance=container_id)['taskArns'][0].split('/')[1]

        # stop the task
        ecs.stop_task(task=task_id)

        # dec service count from 1 to 0 since its last instance
        ecs.update_service(service="Final", desiredCount=0)

        # set stat to off
        table.update_item(Key={'time': '11am'}, UpdateExpression='SET stat = :val1',
                          ExpressionAttributeValues={':val1': 'off'})

        # stop the instance with instance id ins
        stop(ins)


# main function
def lambda_handler(event, context):
    # get_current_time
    now = datetime.now()
    # converts time to gmt+5:30 i.e indian time
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('GMT+5:30')
    now = now.replace(tzinfo=from_zone)
    central = now.astimezone(to_zone)
    # get hour and minute
    hour = central.hour
    minute = central.minute
    print(hour, minute)

    # update_inc for starting instance and service on it
    # update_dec for stopping service and shutting down instance

    # accordingly call these  functions with id=1 or id=2 for 1st and 2nd instance respectively
    # instance-id  --> id  --> time
    # 'i-48d7b9cb' --> 1   --> 9 to 6
    # 'i-1d9b6f80' --> 2   --> 11 to 8

    # chck for current hour and call functions
    if (hour == 9):
        update_inc(1)
    elif (hour == 11):
        update_inc(2)
    elif (hour == 18):
        update_dec(1)
    elif (hour == 20):
        update_dec(2)


# TEST

# uncomment one at a time

# print ("starting 1...")
# update_inc(1)
# time.sleep(30)

# print ("starting 2..")
# update_inc(2)
## time.sleep(60)

# print ("stopping 1..")
# update_dec(1)
# time.sleep(60)

# print ("stopping 2..")
# update_dec(2)


# -------------Not used for now---------------
"""
def describe():
    ec2=boto3.resource('ec2')
    ecs = boto3.client('ecs')
    #decribe_cluster
    print(ecs.describe_clusters(clusters=['default',]))    

def run_task():
    #to_run_task given task_definition(here Aviate:9)
    ec2=boto3.resource('ec2')
    ecs = boto3.client('ecs')
    x=ecs.run_task(cluster='default',taskDefinition='Aviate:9')
    task_id= x['tasks'][0]['taskArn'].split('/')[1]
    print(ecs.list_tasks(cluster='default',containerInstance='47465365-edcf-4932-926e-77ba3474d2a6')) 
    print (task_id)
    return task_id

def stop_task(task_id):
    ecs.stop_task(cluster='default',task=task_id)

def create():
    #create_service
    ec2=boto3.resource('ec2')
    ecs = boto3.client('ecs')
    x=ecs.create_service(cluster='default',serviceName='service1',taskDefinition='Aviate:9',loadBalancers=[{'loadBalancerName':'ecs-service-elb','containerName':'aviate','containerPort':8080},],role='ecsServiceRole',desiredCount=1)
    print (x)
"""


