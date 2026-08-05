from pathlib import Path
import random

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from config.read_config import read_yaml

def prepare_request(bbox_coords, from_date='2021-01-01T00:00:00Z', to_date='2025-12-31T00:00:00Z'):
    evalscript = """
    //VERSION=3
    function setup() {
        return {
        input: ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12"],
        output: {
            bands: 13,
            sampleType: "FLOAT32"
        }
        };
    }

    function evaluatePixel(sample) {
        return [
        sample.B01,
        sample.B02,
        sample.B03,
        sample.B04,
        sample.B05,
        sample.B06,
        sample.B07,
        sample.B08,
        sample.B8A,
        sample.B09,
        sample.B10,
        sample.B11,
        sample.B12,
        ]
    }
    """

    request = {
        "input": {
            "bounds": {
                "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
                "bbox": bbox_coords,
            },
            "data": [
                {
                    "type": "sentinel-2-l1c",
                    "dataFilter": {
                        "timeRange": {
                            "from": from_date,
                            "to": to_date,
                        }, 
                        "maxCloudCoverage": 10
                    },
                }
            ],
        },
        "output": {
            "width": 512, 
            "height": 512, 
            "responses": [
                {
                    "identifier": "default",
                    "format": {
                        "type": "image/tiff"
                    }
                }
        ]},
        "evalscript": evalscript,
    }

    return request

def random_coords():
    lat_range = [37, 43]        # near south KS border with OK to near north NE border with SD
    lng_range = [-104, -89]     # near west NE border with WY to near central IL

    lat = random.uniform(lat_range[0], lat_range[1])
    lng = random.uniform(lng_range[0], lng_range[1])
    
    return lat, lng


def make_bbox(lat, lng, km=2):
    d = km / 111    # km to degrees
    return [lng-d, lat-d, lng+d, lat+d]


def main(num_frames=500, output_dir='data/'):
    creds = read_yaml('config/copernicus_credentials.yaml')

    client_id = creds['client_id']
    client_secret = creds['client_secret']

    i = 0
    while i < num_frames:
        # Get frames from random location
        lat, lng = random_coords()
        bbox = make_bbox(lat, lng)

        request = prepare_request(bbox)

        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)

        token = oauth.fetch_token(
            token_url="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            client_secret=client_secret,
            include_client_id=True,
        )

        url = "https://sh.dataspace.copernicus.eu/api/v1/process"
        response = oauth.post(url, json=request)

        # Check if response is valid
        if response.headers["Content-Type"] != "image/tiff":
            print(response.text)
            raise RuntimeError("No valid Sentinel-2 data for this request.")

        # Save response data
        output_dir = Path(output_dir)
        filename = output_dir / f"frame_{lng}_{lat}.tif"

        with open(filename, "wb") as f:
            f.write(response.content)
            # TODO get metadata for each tif

        print(f"Data retrieved from {lat}, {lng}")
        i+=1

if __name__ == "__main__":
    main()