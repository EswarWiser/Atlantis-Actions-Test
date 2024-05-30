import boto3
import pandas as pd
import csv

def get_vpc_info(vpc_id, session):
    ec2 = session.client('ec2')
    vpc_response = ec2.describe_vpcs(VpcIds=[vpc_id])
    vpc_info = vpc_response['Vpcs'][0]
    return {
        'VpcId': vpc_info['VpcId'],
        'CidrBlock': vpc_info['CidrBlock'],
        'IsDefault': vpc_info['IsDefault'],
        'State': vpc_info['State']
    }

def get_subnets_info(vpc_id, session):
    ec2 = session.client('ec2')
    subnets_response = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    subnets_info = []

    for subnet in subnets_response['Subnets']:
        subnet_id = subnet['SubnetId']
        cidr_block = subnet['CidrBlock']
        availability_zone = subnet['AvailabilityZone']
        subnets_info.append(f"{subnet_id}-{cidr_block}-{availability_zone}")

    return subnets_info or ["No Subnets"]

def get_route_tables_info(vpc_id, session):
    ec2 = session.client('ec2')
    route_tables_response = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    route_tables_info = []

    for route_table in route_tables_response['RouteTables']:
        route_table_id = route_table['RouteTableId']
        routes = ', '.join([f"{route['DestinationCidrBlock']}->{route.get('GatewayId', 'N/A')}" for route in route_table['Routes']])
        associations = ', '.join([assoc['SubnetId'] for assoc in route_table['Associations'] if 'SubnetId' in assoc])
        route_tables_info.append(f"RT_ID: {route_table_id}\nRoutes: {routes}\nSubnets: {associations}")

    return route_tables_info or ["No Route Tables"]

def get_flow_logs_info(vpc_id, session):
    ec2 = session.client('ec2')
    flow_logs_response = ec2.describe_flow_logs(Filters=[{'Name': 'resource-id', 'Values': [vpc_id]}])
    flow_logs_info = []

    for flow_log in flow_logs_response['FlowLogs']:
        flow_log_id = flow_log['FlowLogId']
        log_group_name = flow_log['LogGroupName']
        traffic_type = flow_log['LogGroupName']
        log_destination = flow_log.get('LogDestination', 'N/A')
        flow_logs_info.append(f"FlowLogId: {flow_log_id}, LogGroupName: {log_group_name}, TrafficType: {log_group_name}, LogDestination: {log_destination}")

    return flow_logs_info or ["No Flow Logs"]

def main():
    all_info = []

    with open('vpcs.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:
            aws_profile, region, vpc_id = row
            session = boto3.Session(profile_name=aws_profile, region_name=region)

            # Fetch VPC information
            vpc_info = get_vpc_info(vpc_id, session)

            # Fetch subnet information
            subnets_info = get_subnets_info(vpc_id, session)

            # Fetch route table information
            route_tables_info = get_route_tables_info(vpc_id, session)

            # Fetch flow logs information
            flow_logs_info = get_flow_logs_info(vpc_id, session)

            row_info = {
                'AWSProfile': aws_profile,
                'Region': region,
                'VpcId': vpc_info['VpcId'],
                'VpcCidrBlock': vpc_info['CidrBlock'],
                'VpcIsDefault': vpc_info['IsDefault'],
                'VpcState': vpc_info['State'],
                'Subnets': '\n'.join(subnets_info),
                'RouteTables': '\n'.join(route_tables_info),
                'FlowLogs': '\n'.join(flow_logs_info)
            }
            all_info.append(row_info)

    # Store the collected data in an Excel file
    df = pd.DataFrame(all_info)
    df.to_excel('vpc_details.xlsx', index=False)

if __name__ == "__main__":
    main()