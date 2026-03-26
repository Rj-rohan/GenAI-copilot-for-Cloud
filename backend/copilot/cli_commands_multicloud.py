"""
cli_commands_multicloud.py
===========================
Multi-cloud CLI remediation commands for AWS, Azure, and GCP.
"""

# ── Cloud Provider CLI Mappings ───────────────────────────────────────────────

CLI_COMMANDS = {
    'aws': {
        "Public storage bucket detected": {
            "*": [
                "# Block all public access to the bucket",
                "aws s3api put-public-access-block \\",
                "  --bucket {name} \\",
                "  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true",
                "",
                "# Set bucket ACL to private",
                "aws s3api put-bucket-acl --bucket {name} --acl private",
            ]
        },
        "Public database exposed": {
            "database": [
                "# Disable public accessibility on RDS instance",
                "aws rds modify-db-instance \\",
                "  --db-instance-identifier {name} \\",
                "  --no-publicly-accessible \\",
                "  --apply-immediately",
            ]
        },
        "Public resource detected": {
            "compute": [
                "# Restrict security group inbound rules",
                "aws ec2 revoke-security-group-ingress \\",
                "  --group-id <SG_ID> --protocol all --cidr 0.0.0.0/0",
            ]
        },
        "Encryption disabled": {
            "storage": [
                "# Enable default AES-256 encryption on S3 bucket",
                "aws s3api put-bucket-encryption \\",
                "  --bucket {name} \\",
                "  --server-side-encryption-configuration",
                '  \'{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}\'',
            ],
            "database": [
                "# Create encrypted snapshot, restore to new encrypted instance",
                "aws rds create-db-snapshot \\",
                "  --db-instance-identifier {name} \\",
                "  --db-snapshot-identifier {name}-encrypted-snap",
            ],
            "compute": [
                "# Enable EBS encryption by default",
                "aws ec2 enable-ebs-encryption-by-default --region {region}",
            ]
        },
        "Logging not enabled": {
            "storage": [
                "# Enable S3 server access logging",
                "aws s3api put-bucket-logging \\",
                "  --bucket {name} \\",
                "  --bucket-logging-status",
                '  \'{"LoggingEnabled":{"TargetBucket":"<LOG_BUCKET>","TargetPrefix":"{name}/access-logs/"}}\'',
            ],
            "compute": [
                "# Enable CloudWatch agent for instance logging",
                "aws ssm send-command \\",
                "  --instance-ids {id} \\",
                "  --document-name AWS-ConfigureAWSPackage \\",
                "  --parameters action=Install,name=AmazonCloudWatchAgent",
            ]
        },
        "Idle resource": {
            "compute": [
                "# Stop the idle EC2 instance",
                "aws ec2 stop-instances --instance-ids {id}",
            ],
            "database": [
                "# Stop idle RDS instance",
                "aws rds stop-db-instance --db-instance-identifier {name}",
            ]
        },
        "Unused resource": {
            "compute": [
                "# Terminate unused EC2 instance",
                "aws ec2 terminate-instances --instance-ids {id}",
            ],
            "storage": [
                "# Delete unused S3 bucket",
                "aws s3 rm s3://{name} --recursive",
                "aws s3api delete-bucket --bucket {name} --region {region}",
            ]
        },
        "SSH port (22) exposed to internet": {
            "*": [
                "# Revoke SSH inbound rule from 0.0.0.0/0",
                "aws ec2 revoke-security-group-ingress \\",
                "  --group-id <SG_ID> \\",
                "  --protocol tcp --port 22 --cidr 0.0.0.0/0",
            ]
        },
        "RDP port (3389) exposed to internet": {
            "*": [
                "# Revoke RDP inbound rule from 0.0.0.0/0",
                "aws ec2 revoke-security-group-ingress \\",
                "  --group-id <SG_ID> \\",
                "  --protocol tcp --port 3389 --cidr 0.0.0.0/0",
            ]
        },
        "Resource missing required tags": {
            "compute": [
                "# Apply mandatory tags to EC2 instance",
                "aws ec2 create-tags \\",
                "  --resources {id} \\",
                "  --tags Key=env,Value=prod Key=team,Value=<TEAM> Key=owner,Value=<OWNER>",
            ]
        }
    },
    
    'azure': {
        "Public storage bucket detected": {
            "*": [
                "# Disable public blob access on storage account",
                "az storage account update \\",
                "  --name {name} \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --allow-blob-public-access false",
                "",
                "# Set container access to private",
                "az storage container set-permission \\",
                "  --name <CONTAINER> \\",
                "  --account-name {name} \\",
                "  --public-access off",
            ]
        },
        "Public database exposed": {
            "database": [
                "# Disable public network access on Azure SQL",
                "az sql server update \\",
                "  --name {name} \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --enable-public-network false",
                "",
                "# Add firewall rule for specific IPs only",
                "az sql server firewall-rule create \\",
                "  --name AllowOfficeIP \\",
                "  --server {name} \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --start-ip-address <OFFICE_IP> \\",
                "  --end-ip-address <OFFICE_IP>",
            ]
        },
        "Public resource detected": {
            "compute": [
                "# Remove public IP from VM",
                "az network nic ip-config update \\",
                "  --name ipconfig1 \\",
                "  --nic-name {name}-nic \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --remove PublicIpAddress",
                "",
                "# Restrict NSG inbound rules",
                "az network nsg rule delete \\",
                "  --nsg-name {name}-nsg \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --name AllowAllInbound",
            ]
        },
        "Encryption disabled": {
            "storage": [
                "# Enable encryption at rest for storage account",
                "az storage account update \\",
                "  --name {name} \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --encryption-services blob file",
            ],
            "database": [
                "# Enable Transparent Data Encryption (TDE)",
                "az sql db tde set \\",
                "  --database {name} \\",
                "  --server <SERVER_NAME> \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --status Enabled",
            ],
            "compute": [
                "# Enable disk encryption on VM",
                "az vm encryption enable \\",
                "  --name {name} \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --disk-encryption-keyvault <KEYVAULT_NAME>",
            ]
        },
        "Logging not enabled": {
            "storage": [
                "# Enable storage analytics logging",
                "az storage logging update \\",
                "  --account-name {name} \\",
                "  --services b \\",
                "  --log rwd \\",
                "  --retention 90",
            ],
            "compute": [
                "# Enable Azure Monitor agent",
                "az vm extension set \\",
                "  --name AzureMonitorLinuxAgent \\",
                "  --publisher Microsoft.Azure.Monitor \\",
                "  --vm-name {name} \\",
                "  --resource-group <RESOURCE_GROUP>",
            ]
        },
        "Idle resource": {
            "compute": [
                "# Deallocate idle VM to save cost",
                "az vm deallocate \\",
                "  --name {name} \\",
                "  --resource-group <RESOURCE_GROUP>",
            ],
            "database": [
                "# Pause Azure SQL Database",
                "az sql db pause \\",
                "  --name {name} \\",
                "  --server <SERVER_NAME> \\",
                "  --resource-group <RESOURCE_GROUP>",
            ]
        },
        "Unused resource": {
            "compute": [
                "# Delete unused VM",
                "az vm delete \\",
                "  --name {name} \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --yes",
            ],
            "storage": [
                "# Delete unused storage account",
                "az storage account delete \\",
                "  --name {name} \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --yes",
            ]
        },
        "SSH port (22) exposed to internet": {
            "*": [
                "# Remove NSG rule allowing SSH from internet",
                "az network nsg rule delete \\",
                "  --nsg-name <NSG_NAME> \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --name AllowSSH",
                "",
                "# Add restricted SSH rule",
                "az network nsg rule create \\",
                "  --nsg-name <NSG_NAME> \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --name AllowSSHFromOffice \\",
                "  --priority 100 \\",
                "  --source-address-prefixes <OFFICE_IP> \\",
                "  --destination-port-ranges 22 \\",
                "  --access Allow \\",
                "  --protocol Tcp",
            ]
        },
        "RDP port (3389) exposed to internet": {
            "*": [
                "# Remove NSG rule allowing RDP from internet",
                "az network nsg rule delete \\",
                "  --nsg-name <NSG_NAME> \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --name AllowRDP",
            ]
        },
        "Resource missing required tags": {
            "compute": [
                "# Apply mandatory tags to VM",
                "az vm update \\",
                "  --name {name} \\",
                "  --resource-group <RESOURCE_GROUP> \\",
                "  --set tags.env=prod tags.team=<TEAM> tags.owner=<OWNER>",
            ]
        }
    },
    
    'gcp': {
        "Public storage bucket detected": {
            "*": [
                "# Remove public access from GCS bucket",
                "gsutil iam ch -d allUsers:objectViewer gs://{name}",
                "gsutil iam ch -d allAuthenticatedUsers:objectViewer gs://{name}",
                "",
                "# Set uniform bucket-level access",
                "gsutil uniformbucketlevelaccess set on gs://{name}",
            ]
        },
        "Public database exposed": {
            "database": [
                "# Remove public IP from Cloud SQL instance",
                "gcloud sql instances patch {name} \\",
                "  --no-assign-ip",
                "",
                "# Add authorized network (specific IP only)",
                "gcloud sql instances patch {name} \\",
                "  --authorized-networks=<OFFICE_IP>/32",
            ]
        },
        "Public resource detected": {
            "compute": [
                "# Remove external IP from Compute Engine instance",
                "gcloud compute instances delete-access-config {name} \\",
                "  --access-config-name='external-nat' \\",
                "  --zone={region}",
                "",
                "# Update firewall rule to restrict access",
                "gcloud compute firewall-rules update <RULE_NAME> \\",
                "  --source-ranges=<OFFICE_IP>/32",
            ]
        },
        "Encryption disabled": {
            "storage": [
                "# Enable default encryption (already enabled by default in GCS)",
                "# Use customer-managed encryption keys (CMEK)",
                "gsutil kms encryption -k projects/<PROJECT>/locations/global/keyRings/<KEYRING>/cryptoKeys/<KEY> gs://{name}",
            ],
            "database": [
                "# Enable CMEK for Cloud SQL",
                "gcloud sql instances patch {name} \\",
                "  --disk-encryption-key=projects/<PROJECT>/locations/<REGION>/keyRings/<KEYRING>/cryptoKeys/<KEY>",
            ],
            "compute": [
                "# Create disk with CMEK encryption",
                "gcloud compute disks create {name}-encrypted \\",
                "  --size=100GB \\",
                "  --kms-key=projects/<PROJECT>/locations/<REGION>/keyRings/<KEYRING>/cryptoKeys/<KEY> \\",
                "  --zone={region}",
            ]
        },
        "Logging not enabled": {
            "storage": [
                "# Enable Cloud Storage access logs",
                "gsutil logging set on -b gs://<LOG_BUCKET> -o {name}/ gs://{name}",
            ],
            "compute": [
                "# Enable Cloud Logging agent",
                "gcloud compute instances add-metadata {name} \\",
                "  --zone={region} \\",
                "  --metadata=enable-oslogin=TRUE",
            ]
        },
        "Idle resource": {
            "compute": [
                "# Stop idle Compute Engine instance",
                "gcloud compute instances stop {name} --zone={region}",
            ],
            "database": [
                "# Stop Cloud SQL instance",
                "gcloud sql instances patch {name} --activation-policy=NEVER",
            ]
        },
        "Unused resource": {
            "compute": [
                "# Delete unused Compute Engine instance",
                "gcloud compute instances delete {name} \\",
                "  --zone={region} \\",
                "  --quiet",
            ],
            "storage": [
                "# Delete unused GCS bucket",
                "gsutil rm -r gs://{name}",
            ]
        },
        "SSH port (22) exposed to internet": {
            "*": [
                "# Update firewall rule to restrict SSH",
                "gcloud compute firewall-rules update <RULE_NAME> \\",
                "  --source-ranges=<OFFICE_IP>/32 \\",
                "  --allow=tcp:22",
                "",
                "# Or use IAP for SSH (no firewall rule needed)",
                "gcloud compute ssh {name} --zone={region} --tunnel-through-iap",
            ]
        },
        "RDP port (3389) exposed to internet": {
            "*": [
                "# Update firewall rule to restrict RDP",
                "gcloud compute firewall-rules update <RULE_NAME> \\",
                "  --source-ranges=<OFFICE_IP>/32 \\",
                "  --allow=tcp:3389",
            ]
        },
        "Resource missing required tags": {
            "compute": [
                "# Apply labels to Compute Engine instance",
                "gcloud compute instances add-labels {name} \\",
                "  --zone={region} \\",
                "  --labels=env=prod,team=<TEAM>,owner=<OWNER>",
            ]
        }
    }
}


def get_cli_commands(issue_message, resource_type, resource_id, resource_name, region, provider='aws'):
    """
    Return CLI commands for a given issue, resource, and cloud provider.
    """
    provider_commands = CLI_COMMANDS.get(provider, {})
    issue_map = provider_commands.get(issue_message, {})
    commands = issue_map.get(resource_type) or issue_map.get('*', [])
    
    # Substitute placeholders
    substituted = []
    for cmd in commands:
        cmd = cmd.replace('{id}', resource_id)
        cmd = cmd.replace('{name}', resource_name)
        cmd = cmd.replace('{region}', region)
        substituted.append(cmd)
    
    return substituted


def get_all_cli_fixes(finding, provider='aws'):
    """
    Return all CLI fixes for all issues in a finding, grouped by issue.
    """
    result = {}
    rtype = finding.get('resource_type', 'compute')
    rid = finding.get('resource_id', '')
    rname = finding.get('resource_name', rid)
    region = finding.get('region', 'us-east-1')
    
    for issue in finding.get('issues', []):
        cmds = get_cli_commands(issue, rtype, rid, rname, region, provider)
        if cmds:
            result[issue] = cmds
    
    return result
