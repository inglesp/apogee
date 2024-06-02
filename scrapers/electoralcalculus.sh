#!/bin/bash

N=$1
DROPLET_NAME=electoralcalculus-$N
FINGERPRINT=b8:bf:af:62:b5:c1:ad:ce:3d:15:7c:02:68:1c:04:65
DIR=data/raw/electoralcalculus/$(date '+%Y-%m-%d')

echo "$DROPLET_NAME"

IPADDR=$(doctl compute droplet create \
        --region lon1 \
        --image django-20-04 \
        --size s-1vcpu-1gb \
        --ssh-keys $FINGERPRINT \
        --wait \
        --format PublicIPv4 \
        --no-header \
        "$DROPLET_NAME")

echo "$IPADDR"

sleep 180

scp -o "StrictHostKeyChecking no" scrapers/electoralcalculus.py root@"$IPADDR":

ssh root@"$IPADDR" <<EOF
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install httpx
python3 -u electoralcalculus.py $N
EOF

mkdir -p "$DIR"

scp root@"$IPADDR":"$DIR"/* "$DIR"

doctl compute droplet delete --force "$DROPLET_NAME"
