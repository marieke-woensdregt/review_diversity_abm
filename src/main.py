import argparse
import configparser

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read("config.conf")
    PROJECT_NAME = config["Config"]["PROJECT_NAME"]
    BUCKET_NAME = config["Config"]["BUCKET_NAME"]

    parser = argparse.ArgumentParser()
    parser.add_argument('--my-parameter', help='test parameter', default='myid123')
    args = parser.parse_args()

    print('Code within Docker Container launched successfully on Google Compute Engine')
    print('MY PARAMETER: ', args.my_parameter)

