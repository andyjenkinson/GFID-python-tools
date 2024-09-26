import sys
import argparse
import yaml
import json
import re

from field_id.api_client import APIClient, APIConfiguration

def main(argv):

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-o", "--outputfile", required=False, help="Output path; defaults to STDOUT")
    argParser.add_argument("-c", "--configfile", required=True, help="Path to config YAML file containing credentials")
    group = argParser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--inputfile", help="Path to a comma or line-separated list of Global FieldIDs")
    group.add_argument("-f", "--gfid", help="Comma-separated list of Global FieldIDs")

    args = argParser.parse_args()
    print("args=%s" % args)

    input_fn = args.inputfile
    gfid_string = args.gfid
    output_fn = args.outputfile
    config_fn = args.configfile

    conf = read_yaml(config_fn)
    if input_fn:
        gfid_string = open(input_fn, 'r').read().strip()
        gfid_string = re.sub("[\s,]+", ',', gfid_string)
    gfids = gfid_string.split(',')

    output_fh = None
    if output_fn:
        output_fh = open(output_fn, 'w')
   
    api_config = APIConfiguration.from_dict(conf)

    query_params = {
        'field_relationships.field_id': gfid_string,
    }

    api_client = APIClient(config=api_config)
    response = api_client.get_boundaries(args=query_params, limit=len(gfids))
    results = response.json()

    if (output_fh):
        print("--- Printing response to %s ---" % output_fn)
        print(json.dumps(results, indent=2), file=output_fh)
    else:
        print("--- Response ---")
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