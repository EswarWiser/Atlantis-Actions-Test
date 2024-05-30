import boto3
import csv

def delete_security_group(sg_id, session):
    ec2 = session.client('ec2')
    try:
        ec2.delete_security_group(GroupId=sg_id)
        return True, f"Security Group {sg_id} deleted successfully"
    except Exception as e:
        return False, str(e)

def find_sg_dependencies(sg_id, session):
    ec2 = session.client('ec2')
    dependencies = []

    # Check ENIs (Elastic Network Interfaces)
    response = ec2.describe_network_interfaces(Filters=[{'Name': 'group-id', 'Values': [sg_id]}])
    for interface in response['NetworkInterfaces']:
        dependencies.append(f"ENI: {interface['NetworkInterfaceId']}")

    # Check Security Groups
    response = ec2.describe_security_groups(Filters=[{'Name': 'ip-permission.group-id', 'Values': [sg_id]}])
    for sg in response['SecurityGroups']:
        dependencies.append(f"Security Group: {sg['GroupId']}")

        # Remove only rules referencing the current security group from other security groups
        for rule in sg['IpPermissions']:
            for pair in rule.get('UserIdGroupPairs', []):
                if pair['GroupId'] == sg_id:
                    try:
                        ec2.revoke_security_group_ingress(
                            GroupId=sg['GroupId'],
                            IpPermissions=[{
                                'IpProtocol': rule['IpProtocol'],
                                'FromPort': rule.get('FromPort'),
                                'ToPort': rule.get('ToPort'),
                                'UserIdGroupPairs': [pair]
                            }]
                        )
                        dependencies.append(f"  - Removed ingress rule from {sg['GroupId']} referencing {sg_id}")
                    except Exception as e:
                        dependencies.append(f"  - Error removing ingress rule from {sg['GroupId']}: {str(e)}")

        for rule in sg['IpPermissionsEgress']:
            for pair in rule.get('UserIdGroupPairs', []):
                if pair['GroupId'] == sg_id:
                    try:
                        ec2.revoke_security_group_egress(
                            GroupId=sg['GroupId'],
                            IpPermissions=[{
                                'IpProtocol': rule['IpProtocol'],
                                'FromPort': rule.get('FromPort'),
                                'ToPort': rule.get('ToPort'),
                                'UserIdGroupPairs': [pair]
                            }]
                        )
                        dependencies.append(f"  - Removed egress rule from {sg['GroupId']} referencing {sg_id}")
                    except Exception as e:
                        dependencies.append(f"  - Error removing egress rule from {sg['GroupId']}: {str(e)}")

    return dependencies

def main():
    with open('sample_sgs.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            account_profile, region, sg_id = row
            aws_profile = account_profile.strip()
            session = boto3.Session(profile_name=aws_profile, region_name=region)
           
            dependencies = find_sg_dependencies(sg_id, session)
            if dependencies:
                print(f"Security Group {sg_id} has dependencies and cannot be deleted:")
                for dep in dependencies:
                    print(f"  - {dep}")
            else:
                success, message = delete_security_group(sg_id, session)
                if success:
                    print(message)
                else:
                    print(f"Error deleting Security Group {sg_id}: {message}")

if __name__ == "__main__":
    main()