import boto3
from botocore import session


# get available profiles excluding specified ones
def get_aws_profiles(exclude_profiles):
    all_profiles = session.Session().available_profiles
    return [profile for profile in all_profiles if profile not in exclude_profiles]


# get all enabled regions per profile/acc
def enabled_regions(profile_name):
    ec2_client = boto3.Session(profile_name=profile_name).client('ec2', region_name='us-west-2')
    regions = []
    try:
        ec2_response = ec2_client.describe_regions()
        regions = [region['RegionName'] for region in ec2_response['Regions']]
    except Exception as e:
        print(f"Error fetching regions '{profile_name}': {e}")
    return regions


# profiles to exclude
exclude_profile_names = ['wiser', 'saml', 'default']

# loop through aws profiles except excluding ones
for aws_profile in get_aws_profiles(exclude_profile_names):
    # print("profile", aws_profile)
    # loop through enabled regions in each profile
    for aws_region in enabled_regions(aws_profile):
        # print(f"profile: {aws_profile}, Region: {aws_region}")

        rds_client = boto3.Session(profile_name=aws_profile, region_name=aws_region).client('rds')
        sts_client = boto3.Session(profile_name=aws_profile).client('sts')
        iam_client = boto3.Session(profile_name=aws_profile).client('iam')
        response = rds_client.describe_db_instances()
        instances = response['DBInstances']
        target_instance_types = ['db.t2', 'db.m4', 'db.r4']
        if not instances:
            pass
        else:
            # list all rds instances with specified instance types for each profile along with acc id and acc alias
            account_id = sts_client.get_caller_identity()['Account']
            aliases = iam_client.list_account_aliases()['AccountAliases']
            account_alias = aliases[0] if aliases else 'N/A'
            for instance in instances:
                instance_identifier = instance['DBInstanceIdentifier']
                instance_type = instance['DBInstanceClass']
                vpc_id = instance.get('DBSubnetGroup', {}).get('VpcId', 'N/A')
                status = instance['DBInstanceStatus']
                if any(instance_type.startswith(target_type) for target_type in target_instance_types):
                    print(
                        f"AccountID: {account_id}, AccountAlias: {account_alias}, Instance: {instance_identifier}, \n"
                        f"instance_type: {instance_type}, VPC: {vpc_id}, Status: {status}")
