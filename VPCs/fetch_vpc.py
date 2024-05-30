import boto3
import csv
import pandas as pd

def fetch_vpc_peering_connections(session, vpc_id):
    ec2 = session.client('ec2')
    # Fetch peering connections where the VPC is the requester
    requester_peering_connections = ec2.describe_vpc_peering_connections(
        Filters=[{'Name': 'requester-vpc-info.vpc-id', 'Values': [vpc_id]}]
    ).get('VpcPeeringConnections', [])

    # Fetch peering connections where the VPC is the accepter
    accepter_peering_connections = ec2.describe_vpc_peering_connections(
        Filters=[{'Name': 'accepter-vpc-info.vpc-id', 'Values': [vpc_id]}]
    ).get('VpcPeeringConnections', [])

    # Combine both sets of peering connections
    return requester_peering_connections + accepter_peering_connections

def main():
    csv_file = 'vpcs.csv'
    output_file = 'vpc_peering_connections.xlsx'

    # Data structure to store the details
    data = []

    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            aws_profile, region, vpc_id = row
            aws_profile = aws_profile.strip()
            session = boto3.Session(profile_name=aws_profile, region_name=region)

            print(f"Fetching peering connections for VPC {vpc_id} in profile {aws_profile} and region {region}")
            peering_connections = fetch_vpc_peering_connections(session, vpc_id)
            if not peering_connections:
                data.append({
                    'Profile': aws_profile,
                    'Region': region,
                    'VPC ID': vpc_id,
                    'Peering Connection ID': 'No peering connections',
                    'Requester VPC ID': 'N/A',
                    'Requester VPC Owner': 'N/A',
                    'Requester VPC CIDR': 'N/A',
                    'Accepter VPC ID': 'N/A',
                    'Accepter VPC Owner': 'N/A',
                    'Accepter VPC CIDR': 'N/A',
                    'Status Code': 'N/A',
                    'Status Message': 'N/A'
                })
            else:
                for connection in peering_connections:
                    connection_details = {
                        'Profile': aws_profile,
                        'Region': region,
                        'VPC ID': vpc_id,
                        'Peering Connection ID': connection['VpcPeeringConnectionId'],
                        'Requester VPC ID': connection['RequesterVpcInfo']['VpcId'],
                        'Requester VPC Owner': connection['RequesterVpcInfo']['OwnerId'],
                        'Requester VPC CIDR': connection['RequesterVpcInfo'].get('CidrBlock', 'N/A'),
                        'Accepter VPC ID': connection['AccepterVpcInfo']['VpcId'],
                        'Accepter VPC Owner': connection['AccepterVpcInfo']['OwnerId'],
                        'Accepter VPC CIDR': connection['AccepterVpcInfo'].get('CidrBlock', 'N/A'),
                        'Status Code': connection['Status']['Code'],
                        'Status Message': connection['Status']['Message']
                    }
                    data.append(connection_details)

    # Convert the data to a DataFrame
    df = pd.DataFrame(data)

    # Write the DataFrame to an Excel file
    df.to_excel(output_file, index=False)

if __name__ == "__main__":
    main()