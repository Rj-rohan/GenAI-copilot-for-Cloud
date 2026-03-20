"""
cli_commands.py
===============
Maps security/cost issues to specific AWS CLI remediation commands.
Commands are parameterized with actual resource details from findings.
"""

# ── Per-issue CLI fix commands ────────────────────────────────────────────────
# Each entry: issue_message -> { resource_type -> [list of aws cli commands] }
# Placeholders: {name}=resource_name, {id}=resource_id, {region}=region

ISSUE_CLI = {

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
            "",
            "# Verify the change",
            "aws rds describe-db-instances \\",
            "  --db-instance-identifier {name} \\",
            "  --query 'DBInstances[0].PubliclyAccessible'",
        ]
    },

    "Public resource detected": {
        "compute": [
            "# Remove public IP and move behind a load balancer",
            "aws ec2 modify-instance-attribute \\",
            "  --instance-id {id} \\",
            "  --no-source-dest-check",
            "",
            "# Restrict security group inbound rules",
            "aws ec2 revoke-security-group-ingress \\",
            "  --group-id <sg-id> --protocol all --cidr 0.0.0.0/0",
        ],
        "network": [
            "# Convert to internal load balancer (requires recreate)",
            "aws elbv2 describe-load-balancers --names {name}",
            "",
            "# Restrict security group to known IP ranges",
            "aws ec2 revoke-security-group-ingress \\",
            "  --group-id <sg-id> --protocol tcp --port 443 --cidr 0.0.0.0/0",
            "aws ec2 authorize-security-group-ingress \\",
            "  --group-id <sg-id> --protocol tcp --port 443 --cidr <YOUR_OFFICE_IP>/32",
        ],
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
            "",
            "aws rds restore-db-instance-from-db-snapshot \\",
            "  --db-instance-identifier {name}-encrypted \\",
            "  --db-snapshot-identifier {name}-encrypted-snap \\",
            "  --storage-encrypted",
        ],
        "compute": [
            "# Enable EBS encryption by default in this region",
            "aws ec2 enable-ebs-encryption-by-default --region {region}",
            "",
            "# Create encrypted AMI from existing instance",
            "aws ec2 create-image \\",
            "  --instance-id {id} \\",
            "  --name {name}-encrypted-ami \\",
            "  --block-device-mappings '[{\"DeviceName\":\"/dev/sda1\",\"Ebs\":{\"Encrypted\":true}}]'",
        ],
        "*": [
            "# Enable encryption for this resource (generic)",
            "aws ec2 enable-ebs-encryption-by-default --region {region}",
        ],
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
        ],
        "database": [
            "# Enable RDS enhanced monitoring and logs",
            "aws rds modify-db-instance \\",
            "  --db-instance-identifier {name} \\",
            "  --enable-cloudwatch-logs-exports '[\"audit\",\"error\",\"general\",\"slowquery\"]' \\",
            "  --monitoring-interval 60 \\",
            "  --apply-immediately",
        ],
        "*": [
            "# Enable CloudTrail for all regions (account-level)",
            "aws cloudtrail create-trail \\",
            "  --name org-audit-trail \\",
            "  --s3-bucket-name <LOG_BUCKET> \\",
            "  --is-multi-region-trail",
            "aws cloudtrail start-logging --name org-audit-trail",
        ],
    },

    "Idle resource": {
        "compute": [
            "# Stop the idle EC2 instance to save cost",
            "aws ec2 stop-instances --instance-ids {id}",
            "",
            "# Or schedule auto-stop during off-hours using SSM",
            "aws ssm put-parameter \\",
            "  --name /automation/stop-instances \\",
            "  --value '{id}' --type StringList",
        ],
        "database": [
            "# Stop idle RDS instance (saves ~60% cost when stopped)",
            "aws rds stop-db-instance \\",
            "  --db-instance-identifier {name}",
        ],
        "*": [
            "# Review and consider stopping this idle resource",
            "aws ec2 stop-instances --instance-ids {id}",
        ],
    },

    "Unused resource": {
        "compute": [
            "# Terminate unused EC2 instance",
            "aws ec2 terminate-instances --instance-ids {id}",
        ],
        "storage": [
            "# Delete unused S3 bucket (must be empty first)",
            "aws s3 rm s3://{name} --recursive",
            "aws s3api delete-bucket --bucket {name} --region {region}",
        ],
        "database": [
            "# Create final snapshot then delete unused RDS instance",
            "aws rds delete-db-instance \\",
            "  --db-instance-identifier {name} \\",
            "  --final-db-snapshot-identifier {name}-final-snap",
        ],
        "*": [
            "# Delete unused resource after taking a final backup/snapshot",
            "aws ec2 terminate-instances --instance-ids {id}",
        ],
    },

    "Suspicious login activity detected": {
        "*": [
            "# Force password reset for compromised credentials",
            "aws iam update-login-profile \\",
            "  --user-name <IAM_USER> \\",
            "  --password-reset-required",
            "",
            "# Enable MFA enforcement policy",
            "aws iam attach-user-policy \\",
            "  --user-name <IAM_USER> \\",
            "  --policy-arn arn:aws:iam::aws:policy/IAMUserChangePassword",
            "",
            "# Rotate access keys immediately",
            "aws iam list-access-keys --user-name <IAM_USER>",
            "aws iam delete-access-key \\",
            "  --user-name <IAM_USER> \\",
            "  --access-key-id <OLD_KEY_ID>",
            "aws iam create-access-key --user-name <IAM_USER>",
        ]
    },

    "Known vulnerabilities detected": {
        "compute": [
            "# Run SSM patch baseline to apply security patches",
            "aws ssm send-command \\",
            "  --instance-ids {id} \\",
            "  --document-name AWS-RunPatchBaseline \\",
            "  --parameters Operation=Install",
            "",
            "# Check patch compliance state",
            "aws ssm describe-instance-patch-states \\",
            "  --instance-ids {id}",
        ],
        "*": [
            "# Get SecurityHub findings for this resource",
            "aws securityhub get-findings \\",
            "  --filters '{\"ResourceId\":[{\"Value\":\"{id}\",\"Comparison\":\"EQUALS\"}]}'",
            "",
            "# Apply patches via SSM",
            "aws ssm send-command \\",
            "  --instance-ids {id} \\",
            "  --document-name AWS-RunPatchBaseline \\",
            "  --parameters Operation=Install",
        ],
    },

    "SSH port (22) exposed to internet": {
        "*": [
            "# Revoke SSH inbound rule from 0.0.0.0/0",
            "aws ec2 revoke-security-group-ingress \\",
            "  --group-id <SG_ID> \\",
            "  --protocol tcp --port 22 --cidr 0.0.0.0/0",
            "",
            "# Allow SSH only from bastion / VPN IP",
            "aws ec2 authorize-security-group-ingress \\",
            "  --group-id <SG_ID> \\",
            "  --protocol tcp --port 22 --cidr <BASTION_IP>/32",
            "",
            "# Better: use AWS Systems Manager Session Manager (no SSH needed)",
            "aws ssm start-session --target {id}",
        ]
    },

    "RDP port (3389) exposed to internet": {
        "*": [
            "# Revoke RDP inbound rule from 0.0.0.0/0",
            "aws ec2 revoke-security-group-ingress \\",
            "  --group-id <SG_ID> \\",
            "  --protocol tcp --port 3389 --cidr 0.0.0.0/0",
            "",
            "# Allow RDP only from VPN IP range",
            "aws ec2 authorize-security-group-ingress \\",
            "  --group-id <SG_ID> \\",
            "  --protocol tcp --port 3389 --cidr <VPN_IP>/32",
            "",
            "# Enable NLA (Network Level Authentication) via SSM",
            "aws ssm send-command \\",
            "  --instance-ids {id} \\",
            "  --document-name AWS-RunPowerShellScript \\",
            "  --parameters commands='Set-ItemProperty -Path HKLM:\\System\\CurrentControlSet\\Control\\Terminal\\ Server\\WinStations\\RDP-Tcp -Name UserAuthentication -Value 1'",
        ]
    },

    "Stale resource - no activity for 90+ days": {
        "compute": [
            "# Check last activity before decommissioning",
            "aws cloudtrail lookup-events \\",
            "  --lookup-attributes AttributeKey=ResourceName,AttributeValue={id} \\",
            "  --max-results 5",
            "",
            "# Stop first, terminate after confirming no owner",
            "aws ec2 stop-instances --instance-ids {id}",
        ],
        "*": [
            "# Check CloudTrail for last 90 days of activity",
            "aws cloudtrail lookup-events \\",
            "  --lookup-attributes AttributeKey=ResourceName,AttributeValue={id}",
        ],
    },

    "Rightsizing opportunity identified": {
        "compute": [
            "# Get rightsizing recommendation from Cost Explorer",
            "aws ce get-rightsizing-recommendation \\",
            "  --service EC2 \\",
            "  --configuration RecommendationTarget=SAME_INSTANCE_FAMILY",
            "",
            "# Stop instance, change type, restart",
            "aws ec2 stop-instances --instance-ids {id}",
            "aws ec2 modify-instance-attribute \\",
            "  --instance-id {id} \\",
            "  --instance-type '{\"Value\":\"t3.micro\"}'",
            "aws ec2 start-instances --instance-ids {id}",
        ],
        "database": [
            "# Get RDS recommendations from Cost Explorer",
            "aws ce get-rightsizing-recommendation --service RDS",
            "",
            "# Modify DB instance class",
            "aws rds modify-db-instance \\",
            "  --db-instance-identifier {name} \\",
            "  --db-instance-class db.t3.small \\",
            "  --apply-immediately",
        ],
        "*": [
            "aws ce get-rightsizing-recommendation --service EC2",
        ],
    },

    "Active compliance violations detected": {
        "*": [
            "# List all Config rule violations for this resource",
            "aws configservice get-compliance-details-by-resource \\",
            "  --resource-type <RESOURCE_TYPE> \\",
            "  --resource-id {id}",
            "",
            "# Get remediation actions from AWS Config",
            "aws configservice describe-remediation-configurations \\",
            "  --config-rule-names <RULE_NAME>",
            "",
            "# Trigger auto-remediation",
            "aws configservice start-remediation-execution \\",
            "  --config-rule-name <RULE_NAME> \\",
            "  --resource-keys resourceType=<TYPE>,resourceId={id}",
        ]
    },

    "Resource missing required tags": {
        "compute": [
            "# Apply mandatory tags to EC2 instance",
            "aws ec2 create-tags \\",
            "  --resources {id} \\",
            "  --tags Key=env,Value=prod Key=team,Value=<TEAM> Key=project,Value=<PROJECT> Key=owner,Value=<OWNER>",
        ],
        "storage": [
            "# Apply mandatory tags to S3 bucket",
            "aws s3api put-bucket-tagging \\",
            "  --bucket {name} \\",
            "  --tagging 'TagSet=[{Key=env,Value=prod},{Key=team,Value=<TEAM>},{Key=owner,Value=<OWNER>}]'",
        ],
        "database": [
            "# Apply mandatory tags to RDS instance",
            "aws rds add-tags-to-resource \\",
            "  --resource-name arn:aws:rds:{region}:<ACCOUNT_ID>:db:{name} \\",
            "  --tags Key=env,Value=prod Key=team,Value=<TEAM> Key=owner,Value=<OWNER>",
        ],
        "*": [
            "# Apply mandatory tags (replace with actual values)",
            "aws ec2 create-tags \\",
            "  --resources {id} \\",
            "  --tags Key=env,Value=prod Key=team,Value=<TEAM> Key=owner,Value=<OWNER>",
        ],
    },
}


def get_cli_commands(issue_message, resource_type, resource_id, resource_name, region):
    """
    Return a list of AWS CLI command strings for a given issue and resource.
    Falls back to '*' wildcard if no type-specific commands exist.
    """
    issue_map = ISSUE_CLI.get(issue_message, {})
    commands  = issue_map.get(resource_type) or issue_map.get('*', [])

    # Substitute placeholders
    substituted = []
    for cmd in commands:
        cmd = cmd.replace('{id}',     resource_id)
        cmd = cmd.replace('{name}',   resource_name)
        cmd = cmd.replace('{region}', region)
        substituted.append(cmd)

    return substituted


def get_all_cli_fixes(finding):
    """
    Return all CLI fixes for all issues in a finding, grouped by issue.
    finding must have: issues, resource_type, resource_id, resource_name, region
    """
    result = {}
    rtype  = finding.get('resource_type', 'compute')
    rid    = finding.get('resource_id', '')
    rname  = finding.get('resource_name', rid)
    region = finding.get('region', 'us-east-1')

    for issue in finding.get('issues', []):
        cmds = get_cli_commands(issue, rtype, rid, rname, region)
        if cmds:
            result[issue] = cmds

    return result
