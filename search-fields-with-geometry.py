import sys
import argparse
import yaml
import json

from field_id.api_client import APIClient, APIConfiguration

def main(argv):

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--inputfile", required=True, help="Search input, a path to GeoJSON geometry or feature")
    #argParser.add_argument("-o", "--outputfile", required=False, help="Output path; defaults to STDOUT")
    argParser.add_argument("-c", "--configfile", required=True, help="Path to config YAML file containing credentials")

    args = argParser.parse_args()
    print("args=%s" % args)

    input_fn = args.inputfile
    #output_fn = args.outputfile
    config_fn = args.configfile

    conf = read_yaml(config_fn)
    input_json = read_json(input_fn)
   
    api_config = APIConfiguration()
    api_config.client_id = conf['client_id']
    api_config.client_secret = conf['client_secret']
    if 'token_url' in conf:
        api_config.token_url = conf['token_url']

    api_client = APIClient(config=api_config)
    response = api_client.field_search(payload=input_json)
    results = response.json()
    
    print("--- Response ---")
    #print(results)
    print(json.dumps(results, indent=2))
    print("---")

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def read_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
   main(sys.argv[1:])