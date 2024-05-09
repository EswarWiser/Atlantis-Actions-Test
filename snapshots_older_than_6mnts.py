import boto3
from datetime import datetime, timedelta
from tabulate import tabulate


def get_aws_profiles():
    session = boto3.Session()
    return session.available_profiles


def get_enabled_regions(profile):
    session = boto3.Session(profile_name=profile)
    client = session.client('ec2')
    return [region['RegionName'] for region in client.describe_regions()['Regions']]


def list_rds_snapshots(profile, region, six_months_ago):
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client('rds')

    snapshots = client.describe_db_snapshots()
    snapshot_list = []

    print(f"Fetching all snapshots for profile: {profile}, region: {region}")

    for snapshot in snapshots['DBSnapshots']:
        snapshot_time = snapshot.get('SnapshotCreateTime')
        if snapshot_time and snapshot_time.replace(tzinfo=None) < six_months_ago:
            instance_identifier = snapshot.get('DBInstanceIdentifier', 'N/A')
            snapshot_info = {
                'Account ID': session.client('sts').get_caller_identity()['Account'],
                'Account Name': profile,
                'Region': region,
                'Snapshot ID': snapshot['DBSnapshotIdentifier'],
                'Snapshot Type': snapshot.get('SnapshotType', 'N/A'),
                'Associated RDS Instance': instance_identifier,
                'Snapshot Start Time': snapshot_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            snapshot_list.append(snapshot_info)

    return snapshot_list


def main():
    # Calculate the date six months ago
    six_months_ago = datetime.now() - timedelta(days=180)
    six_months_ago = six_months_ago.replace(tzinfo=None)  # Make it offset-naive

    # Fetch all AWS profiles excluding two specified profiles
    excluded_profiles = ['wiser', 'saml', 'default']
    all_profiles = get_aws_profiles()
    remaining_profiles = [profile for profile in all_profiles if profile not in excluded_profiles]

    all_snapshots_list = []

    # Loop through each remaining profile
    for profile in remaining_profiles:
        print(f"Fetching enabled regions for profile: {profile}")
        regions = get_enabled_regions(profile)

        # Loop through each region and list RDS snapshots for manual and automated separately
        for region in regions:
            print(f"\nListing RDS snapshots for profile: {profile}, region: {region}")

            all_snapshots = list_rds_snapshots(profile, region, six_months_ago=six_months_ago)

            if all_snapshots:
                all_snapshots_list.extend(all_snapshots)

    if all_snapshots_list:
        print(tabulate(all_snapshots_list, headers='keys', tablefmt='pretty'))
    else:
        print("No Snapshots Found")


if __name__ == "__main__":
    main()
