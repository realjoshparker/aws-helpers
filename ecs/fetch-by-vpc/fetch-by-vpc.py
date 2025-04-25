import boto3
import os

# Get a list of subnets for a given VPC
def get_vpc_subnets(vpc_id, region):
    subnets = []
    ec2 = boto3.client("ec2", region_name=region)
    try:
        subnet_info = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
        subnets = [subnet['SubnetId'] for subnet in subnet_info]
    except Exception as e:
        print(f"Error fetching subnets for VPC {vpc_id}: {e}")
        
    return subnets

# Checks if the ECS services belong to the given VPC
def check_ecs_services(vpc_id, region, subnets):
    services = []

    ecs = boto3.client("ecs", region_name=region)

    # Validate subnets were returned for the VPC
    if not subnets:
        print(f"No subnets found for VPC {vpc_id}")
        return services
    elif subnets:
        # Get a list of clusters
        clusters = ecs.list_clusters()['clusterArns']
        for cluster in clusters:
            # Get a list of Service ARNs
            service_arns = ecs.list_services(cluster=cluster)['serviceArns']
            if service_arns:
                # Get details for services
                services_details = ecs.describe_services(cluster=cluster, services=service_arns)
                for service in services_details['services']:
                    if 'networkConfiguration' in service: 
                        awsvpc_config = service['networkConfiguration'].get('awsvpcConfiguration', {})
                        if 'subnets' in awsvpc_config:
                            if any(subnet in subnets for subnet in awsvpc_config['subnets']):
                                services.append(service)                           
    return services

# Checks if tasks belong to a given VPC
def check_ecs_tasks(vpc_id, region, subnets):
    tasks = []
    
    ecs = boto3.client("ecs", region_name=region)
    
    if not subnets:
        print(f"No subnets found for VPC {vpc_id}")
        return tasks
    elif subnets:
        # Get a list of clusters
        clusters = ecs.list_clusters()['clusterArns']
        for cluster in clusters:
            # Get a list of Task ARNs
            task_arns = ecs.list_tasks(cluster=cluster)['taskArns']
            if task_arns:
                task_details = ecs.describe_tasks(cluster=cluster, tasks=task_arns)
                for task in task_details['tasks']:
                    # Filters out tasks that belong to a service
                    if 'family' in task['group']:
                        for attachment in task['attachments']:
                            for detail in attachment['details']:
                                if detail['name'] == 'subnetId' and detail['value'] in subnets:
                                    tasks.append(task)
    return tasks

def output_results(vpc_id, services, tasks):
    while True:
        print(f"\n1) Display the list\n2) Write to a file\n3) Exit")
        user_input = input("What would you like to do? Select an option (1 - 3): ")
        
        if user_input == "1":
            if services:
                print("\n--- ECS Services ---")
                for service in services:
                    print(service['serviceArn'])

            if tasks:
                print("\n--- ECS Tasks ---")
                for task in tasks:
                    print(task['taskArn'])
                    
            break

        elif user_input == "2":
            filename = vpc_id + "ecs_services.txt"
            with open(filename, 'w') as file:
                if services:
                    file.write("--- ECS Services ---\n")
                    for service in services:
                        file.write(f"{service['serviceArn']}\n")
                if tasks:
                    file.write("\n--- ECS Tasks ---\n")
                    for task in tasks:
                        file.write(f"{task['taskArn']}\n")
            print(f"Data has been written to {filename}")
            break
            
        elif user_input == "3": 
            exit()
            
def main():
    vpc_id = input("Enter the VPC ID(e.g. vpc-abc123): ")
    region = input("Enter the region (e.g. us-east-1): ")
    
    subnets = get_vpc_subnets(vpc_id, region)
    services = check_ecs_services(vpc_id, region, subnets)
    tasks = check_ecs_tasks(vpc_id, region, subnets)
    
    print(f"\n--- ECS Services ---\nFound {len(services)} ECS services in VPC {vpc_id}")
    print(f"\n--- ECS Tasks ---\nFound {len(tasks)} ECS tasks in VPC {vpc_id}")
    
    if services or tasks:
        output_results(vpc_id, services, tasks)
        exit()
    else:
        print("No ECS services or tasks found for the specified VPC")
        
if __name__ == "__main__":
    main()