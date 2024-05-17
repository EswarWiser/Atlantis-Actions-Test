import boto3
import csv

def delete_security_group(security_group_id, session):
    ec2 = session.client('ec2')
    try:
        response = ec2.delete_security_group(GroupId=security_group_id)
        print(f"Security Group {security_group_id} deleted successfully")
    except ec2.exceptions.NoSuchGroup:
        print(f"Security Group {security_group_id} not found")
    except Exception as e:
        print(f"Error deleting Security Group {security_group_id}: {e}")

def delete_route_table(route_table_id, session):
    ec2 = session.client('ec2')
    try:
        response = ec2.delete_route_table(RouteTableId=route_table_id)
        print(f"Route Table {route_table_id} deleted successfully")
    except ec2.exceptions.NoSuchRouteTable:
        print(f"Route Table {route_table_id} not found")
    except Exception as e:
        print(f"Error deleting Route Table {route_table_id}: {e}")

def delete_vpc(vpc_id, session):
    ec2 = session.client('ec2')
    try:
        response = ec2.delete_vpc(VpcId=vpc_id)
        print(f"VPC {vpc_id} deleted successfully")
    except ec2.exceptions.ClientError as e:
        if 'dependency' in str(e):
            print(f"Cannot delete VPC {vpc_id}: There are dependencies attached to it")
        else:
            print(f"Error deleting VPC {vpc_id}: {e}")

def main():
    with open('sgs.csv', newline='') as sg_file:
        reader = csv.reader(sg_file)
        next(reader)
        for row in reader:
            account_profile, region, sg_id = row
            aws_profile = account_profile.strip()
            session = boto3.Session(profile_name=aws_profile, region_name=region)
            print(f"Deleting Security Group {sg_id} from {aws_profile} in {region}")
            delete_security_group(sg_id, session)

    with open('rts.csv', newline='') as rt_file:
        reader = csv.reader(rt_file)
        next(reader)
        for row in reader:
            account_profile, region, rt_id = row
            aws_profile = account_profile.strip()
            session = boto3.Session(profile_name=aws_profile, region_name=region)
            print(f"Deleting Route Table {rt_id} from {aws_profile} in {region}")
            delete_route_table(rt_id, session)

    with open('vpcs.csv', newline='') as vpc_file:
        reader = csv.reader(vpc_file)
        next(reader)
        for row in reader:
            account_profile, region, vpc_id = row
            aws_profile = account_profile.strip()
            session = boto3.Session(profile_name=aws_profile, region_name=region)
            print(f"Deleting VPC {vpc_id} from {aws_profile} in {region}")
            delete_vpc(vpc_id, session)

if __name__ == "__main__":
    main()