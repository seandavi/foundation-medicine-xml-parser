from uccc.parser import process_fmi_data
import argparse

def main():
    parser = argparse.ArgumentParser(description='Parse FMI data')
    parser.add_argument('results_directory', type=str, help='Results directory', default='/mnt/00_results')
    args = parser.parse_args()
    process_fmi_data(args.results_directory)
    
if __name__ == '__main__':
    main()