#!/usr/bin/env bash
# One-time: move brissonstagram.net DNS hosting from Squarespace to Route53.
#
# Why: the bare apex (brissonstagram.net) must point at the CloudFront redirect
# distribution (E1G3T4UWPFZ5XN / d1lpzqzhcqnpqo.cloudfront.net), and CloudFront
# has no static IPs. Squarespace DNS has no ALIAS/ANAME record type, so the apex
# cannot be pointed there. Route53 ALIAS records can.
#
# What it does (idempotent, safe to re-run):
#   1. creates the Route53 hosted zone if it doesn't exist
#   2. replicates the only record the Squarespace zone had: www CNAME -> the
#      Zappa API Gateway edge distribution (d3u87crvujqkzu.cloudfront.net)
#   3. adds apex A + AAAA ALIAS -> the redirect distribution
#   4. prints the 4 nameservers to paste into Squarespace
#      (Domains -> brissonstagram.net -> DNS -> Nameservers -> Use custom nameservers)
set -euo pipefail

ZONE_ID=$(aws route53 list-hosted-zones-by-name --dns-name brissonstagram.net \
  --query "HostedZones[?Name=='brissonstagram.net.'].Id | [0]" --output text)
if [ -z "$ZONE_ID" ] || [ "$ZONE_ID" = "None" ]; then
  ZONE_ID=$(aws route53 create-hosted-zone --name brissonstagram.net \
    --caller-reference "brissonstagram-$(date +%s)" \
    --hosted-zone-config Comment="brissonstagram.net (moved from Squarespace DNS 2026-10)" \
    --query HostedZone.Id --output text)
fi
ZONE_ID=${ZONE_ID##*/}
echo "hosted zone: $ZONE_ID"

aws route53 change-resource-record-sets --hosted-zone-id "$ZONE_ID" --change-batch '{
  "Changes": [
    {"Action": "UPSERT", "ResourceRecordSet": {
      "Name": "www.brissonstagram.net", "Type": "CNAME", "TTL": 300,
      "ResourceRecords": [{"Value": "d3u87crvujqkzu.cloudfront.net"}]}},
    {"Action": "UPSERT", "ResourceRecordSet": {
      "Name": "brissonstagram.net", "Type": "A",
      "AliasTarget": {"HostedZoneId": "Z2FDTNDATAQYW2",
                      "DNSName": "d1lpzqzhcqnpqo.cloudfront.net",
                      "EvaluateTargetHealth": false}}},
    {"Action": "UPSERT", "ResourceRecordSet": {
      "Name": "brissonstagram.net", "Type": "AAAA",
      "AliasTarget": {"HostedZoneId": "Z2FDTNDATAQYW2",
                      "DNSName": "d1lpzqzhcqnpqo.cloudfront.net",
                      "EvaluateTargetHealth": false}}}
  ]}' --query ChangeInfo.Status --output text

echo
echo "Paste these 4 nameservers into Squarespace (custom nameservers):"
aws route53 get-hosted-zone --id "$ZONE_ID" --query DelegationSet.NameServers --output text | tr '\t' '\n'
