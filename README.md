# timeOfDay-exporter
Simple exporter for the time of day. Useful to determine when it's day vs night for astrophotography.

# Setup

Make sure you have required software:
* python
* pip
* git

## Clone Source

I am running on ec2 and simply clone into the ec2-user's home directory.

```shell
git clone https://github.com/jewzaam/timeOfDay-exporter
```

## config.yaml

You can name the file whatever you want, but this document assumes **config.yaml**.

```yaml
location:
  latitude: <your latitude in decimal form>
  longitude: <your longitude in decimal form>
refresh_delay_seconds: 3600 # don't need often, once an hour
```
s
## Python requirements

```shell
pip install -r requirements.txt --user
```

## Linux Service

Install the service by setting up some env vars then copying the systemd template with those vars, start the service, and enable the service.

```shell
export REPO_BASE_DIR=~/timeOfDay-exporter
export PORT=8012
export CONFIG=$REPO_BASE_DIR/config.yaml
export PYTHON=$(which python)

cat $REPO_BASE_DIR/src/systemd/timeOfDay-exporter.service | envsubst > /tmp/timeOfDay-exporter.service
sudo mv /tmp/timeOfDay-exporter.service /etc/systemd/system/timeOfDay-exporter.service

unset REPO_BASE_DIR
unset PORT
unset CONFIG
unset PYTHON

sudo systemctl daemon-reload
sudo systemctl start timeOfDay-exporter.service
sudo systemctl enable timeOfDay-exporter.service
```

# Verify

## Metrics 
Check the metrics are exported on the port you specified.