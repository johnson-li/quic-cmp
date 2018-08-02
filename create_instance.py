import argparse
import os
import time
import libcloud
import googleapiclient.discovery
import urllib2
from six.moves import input
from oauth2client.client import GoogleCredentials
import json

credentials = GoogleCredentials.get_application_default()
compute = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)


# [START list_instances]
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items']
# [END list_instances]


# [START create_instance]
def create_instance(compute, project, zone, name, bucket):
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(project='centos-cloud',
        family='centos-7').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone

    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }]
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()
# [END create_instance]


# [START delete_instance]
def delete_instance(compute, project, zone, name):
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()
# [END delete_instance]


# [START wait_for_operation]
def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)
# [END wait_for_operation]

def stop_instance(compute, project, zone, name):
    return compute.instances().stop(
        project=project,
        zone=zone,
        instance=name).execute()

def start_instance(compute, project, zone, name):
    return compute.instances().start(
        project=project,
        zone=zone,
        instance=name).execute()


# [START run]
def main(project, bucket, zone, instance_name, wait=True):
    print('Creating instance.')

    operation = create_instance(compute, project, zone, instance_name, bucket)
    wait_for_operation(compute, project, zone, operation['name'])

    instances = list_instances(compute, project, zone)

    print('Instances in project %s and zone %s:' % (project, zone))
    for instance in instances:
        print(' - ' + instance['name'])

    print("""
Instance created.
It will take a minute or two for the instance to complete work.
Check this URL: http://storage.googleapis.com/{}/output.png
Once the image is uploaded press enter to delete the instance.
""".format(bucket))

    # if wait:
    #     input()
    #
    # print('Deleting instance.')
    #
    # operation = delete_instance(compute, project, zone, instance_name)
    # wait_for_operation(compute, project, zone, operation['name'])


if __name__ == '__main__':
    # zone_list = ['asia-east1-a', 'asia-east1-b', 'asia-east1-c', 'asia-northeast1-a', 'asia-northeast1-b', 'asia-northeast1-c',
    #              'asia-south1-a', 'asia-south1-b', 'asia-south1-c', 'asia-southeast1-a', 'asia-southeast1-b', 'asia-southeast1-c',
    #              'australia-southeast1-a', 'australia-southeast1-b', 'australia-southeast1-c', 'europe-north1-a', 'europe-north1-b',
    #              'europe-north1-c', 'europe-west1-b', 'europe-west1-c', 'europe-west1-d', 'europe-west2-a',
    #              'europe-west2-b', 'europe-west2-c', 'europe-west3-a', 'europe-west3-b', 'europe-west3-c', 'europe-west4-a',
    #              'europe-west4-b', 'europe-west4-c', 'northamerica-northeast1-a', 'northamerica-northeast1-b', 'northamerica-northeast1-c',
    #              'southamerica-east1-a', 'southamerica-east1-b', 'southamerica-east1-c', 'us-central1-a', 'us-central1-b',
    #              'us-central1-c', 'us-central1-f', 'us-east1-b', 'us-east1-c', 'us-east1-d', 'us-east4-a', 'us-east4-b', 'us-east4-c',
    #              'us-west1-a', 'us-west1-b', 'us-west1-c', 'us-west2-a', 'us-west2-b', 'us-west2-c']
    zone_list = ['asia-east1-a', 'asia-east1-b', 'asia-east1-c']
    project_id = 'certain-bonito-211309'
    bucket_name = ''
    client_external_ip = {}
    client_internal_ip = {}
    for zone in zone_list:
        name = 'client-' + zone
        main(project_id, bucket_name, zone, name)
    for zone in zone_list:
        name = 'client-' + zone
        request = compute.instances().list(project=project_id, zone=zone)
        if request is not None:
            response = request.execute()
            for instance in response['items']:
                # print instance
                external_ip = instance[u'networkInterfaces'][0][u'accessConfigs'][0][u'natIP']
                internal_ip = instance[u'networkInterfaces'][0][u'networkIP']
                client_external_ip[zone] = external_ip
                client_internal_ip[zone] = internal_ip
            # request = compute.instances().list_next(previous_request=request, previous_response=response)
    
    print client_external_ip
    print client_internal_ip
    with open('./client_external_ip.json', 'w') as json_file:
        json.dump(client_external_ip, json_file)
    json_file.close()
    with open('./client_internal_ip.json', 'w') as json_file:
        json.dump(client_internal_ip, json_file)
    json_file.close()

    # for zone in zone_list:
    #     name = 'client-' + zone
    #     stop_instance(compute, project_id, zone, name)
    # for zone in zone_list:
    #     name = 'client-' + zone
    #     start_instance(compute, project_id, zone, name)
# [END run]