import boto3
import csv

def delete_non_default_resources(vpc_id, ec2):
    # Delete all non-default security groups associated with the VPC
    sgs_response = ec2.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for sg in sgs_response['SecurityGroups']:
        if sg['GroupName'] != 'default':
            try:
                ec2.delete_security_group(GroupId=sg['GroupId'])
                print(f"Deleted security group {sg['GroupId']}")
            except Exception as e:
                print(f"Could not delete security group {sg['GroupId']}: {e}")

    # Detach and delete all internet gateways associated with the VPC
    ig_response = ec2.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])
    for ig in ig_response['InternetGateways']:
        try:
            ec2.detach_internet_gateway(InternetGatewayId=ig['InternetGatewayId'], VpcId=vpc_id)
            ec2.delete_internet_gateway(InternetGatewayId=ig['InternetGatewayId'])
            print(f"Deleted internet gateway {ig['InternetGatewayId']}")
        except Exception as e:
            print(f"Could not delete internet gateway {ig['InternetGatewayId']}: {e}")

    # Delete all non-main route tables associated with the VPC
    rt_response = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for rt in rt_response['RouteTables']:
        if not any(assoc['Main'] for assoc in rt['Associations']):
            try:
                ec2.delete_route_table(RouteTableId=rt['RouteTableId'])
                print(f"Deleted route table {rt['RouteTableId']}")
            except Exception as e:
                print(f"Could not delete route table {rt['RouteTableId']}: {e}")

    # Delete all non-default network ACLs associated with the VPC
    nacl_response = ec2.describe_network_acls(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for nacl in nacl_response['NetworkAcls']:
        if not nacl['IsDefault']:
            try:
                ec2.delete_network_acl(NetworkAclId=nacl['NetworkAclId'])
                print(f"Deleted network ACL {nacl['NetworkAclId']}")
            except Exception as e:
                print(f"Could not delete network ACL {nacl['NetworkAclId']}: {e}")

    # Delete all subnets associated with the VPC
    subnet_response = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for subnet in subnet_response['Subnets']:
        try:
            ec2.delete_subnet(SubnetId=subnet['SubnetId'])
            print(f"Deleted subnet {subnet['SubnetId']}")
        except Exception as e:
            print(f"Could not delete subnet {subnet['SubnetId']}: {e}")

def delete_vpc(vpc_id, ec2):
    # Delete non-default resources
    delete_non_default_resources(vpc_id, ec2)

    # Delete the VPC
    try:
        ec2.delete_vpc(VpcId=vpc_id)
        print(f"VPC {vpc_id} deleted successfully.")
    except Exception as e:
        print(f"Could not delete VPC {vpc_id}: {e}")

def main():
    # Read AWS profile, region, and VPC ID from CSV file
    with open('vpcs.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            aws_profile, region, vpc_id = row
            session = boto3.Session(profile_name=aws_profile, region_name=region)
            ec2 = session.client('ec2')
            delete_vpc(vpc_id, ec2)

if __name__ == "__main__":
    main()