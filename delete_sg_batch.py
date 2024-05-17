import csv
import boto3
import concurrent.futures

def delete_sg_batch(sg_ids, session):
    ec2 = session.client('ec2')
    for sg_id in sg_ids:
        try:
            ec2.delete_security_group(GroupId=sg_id)
            print(f"sg {sg_id} deleted")
        except Exception as e:
            print(f"Error deleting sg {sg_id}: {e}")

def main():
    batch_size = 2

    with open('sample_sgs.csv', newline='') as sg_file:
        reader = csv.reader(sg_file)
        next(reader)
        for row in reader:
            aws_profile = row[0].strip()
            region = row[1].strip()
            sg_ids = row[2].split(',')
            session = boto3.Session(profile_name=aws_profile, region_name=region)        
            sg_batches = [sg_ids[i:i + batch_size] for i in range(0, len(sg_ids), batch_size)]

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(delete_sg_batch, batch, session) for batch in sg_batches]
                for future in concurrent.futures.as_completed(futures):
                    pass

if __name__ == "__main__":
    main()

    