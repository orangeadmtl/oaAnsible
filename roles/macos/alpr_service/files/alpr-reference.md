# Plate Recognizer

This web site/docker is an Accurate, Fast, Developer-Friendly Automatic License Plate Recognition (ALPR) software that works in all environments, optimized for
your location.

There is an option to predict Vehicle Make, Model, Color & Orientation (mmc).

We can use the library using the online service or locally via a docker image. In the docker case, the only cloud request is to check the license.

## Cost

50$/month (75$/month with mmc), 50,000 Recognitions par mois, Max 8 Calls/Second.

## Local Docker

### Obtain the docker image

```bash
docker pull platerecognizer/alpr
```

### Open firewall

Platerecognizer servers for license validation use the following IPs and ports 80 and 443.

- IP of api.platerecognizer.com: `69.164.223.138`
- IP of app.platerecognizer.com: `172.104.25.230`

TIP: If your firewall also blocks public DNS resolvers, include this option to your run command: `--add-host api.platerecognizer.com:69.164.223.138`

### Run the docker image

```bash
export TOKEN=5d048d052fccb85d5b9a507d485d9b3da0b8e6a7
export LICENSE_KEY=DdmR4ew22Y
docker run --restart="unless-stopped" -t -p 8080:8080 -v license:/license \
  -e TOKEN=${TOKEN}}$ -e LICENSE_KEY=${LICENSE_KEY} \
  platerecognizer/alpr
```

### Resolve using the local docker

```bash
❯ export IMAGE=/Users/eboily/git/Orangead/plate-detector/images/p1.jpg
curl -F "upload=@${IMAGE}" \
     -F regions='ca' \
     -F mmc=true \
     -F 'config={"mode":"fast", "detection_mode":"vehicle"}' \
     http://localhost:8080/v1/plate-reader/
```

### Output Example (without mmc)

```json
{
  "filename": "p1.jpeg",
  "timestamp": "2025-05-30 13:59:09.481824",
  "camera_id": null,
  "results": [
    {
      "box": {
        "xmin": 297,
        "ymin": 311,
        "xmax": 687,
        "ymax": 498
      },
      "plate": "p29vgf",
      "region": {
        "code": "ca-qc",
        "score": 0.796
      },
      "score": 1,
      "candidates": [
        {
          "score": 1,
          "plate": "p29vgf"
        }
      ],
      "dscore": 0.896,
      "vehicle": {
        "score": 0.756,
        "type": "Sedan",
        "box": {
          "xmin": 8,
          "ymin": 2,
          "xmax": 1017,
          "ymax": 762
        }
      }
    }
  ],
  "usage": {
    "calls": 2,
    "max_calls": 2500
  },
  "processing_time": 45.171
}
```

### Notes

When the vehicle is isolated (the image contains only the vehicle, like in `images/tucson_back-isolated.jpg`), the sroces are greatly improved.

# Monitor

This python application connects to the camera and wait for cars to appear. When a car is detected, it takes multiple snapshots of it, identified the best one
(least blurred), isolate the car by cropping its box and save this image in the detection folder. Once the images are saved, they are sent to the plate
detection docker. A JSON file is returned, containing not only the plate number but also the make, model and other characteristics of the car. This JSON is
saved in the same directory as the image.

## Install

This assumes the docker image is up and running.

```bash
uv pip install -r requirements.uv
```

## Launch

```bash
uv run python monitor_cars2.py
```

# Web Poster

This python application runs periodically. It compresses all the JSON files form the detection directory and delete the JSONs. It then upload the zip files to
orangead's cloud. Upon successful upload, it moves the zip time to the archive directory.

# User Interface

## Raw data

Display raw data / download as CSV

# API

## POST data

```
POST /projects/{pid}/cameras/{cid}
```

Body: zip file containing one or more json file(s).

## GET data

```
# return data for all cameras in json format
GET /projects/{pid}/cameras

# return data for one specivic camera in json format
GET /projects/{pid}/cameras/{cid}?&to=2025-06-06T05:00:00.000Z
```

### Query string parameters

#### from

Start time

Example: from=2025-06-06T05:00:00.000Z

#### to

End time

Example: to=2025-06-07T05:00:00.000Z

#### format

Data return format

Options: json (default), csv
