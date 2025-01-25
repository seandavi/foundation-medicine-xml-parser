from foundation_medicine_parser.parser import process_fmi_data
import argparse

def main():
    parser = argparse.ArgumentParser(description='Parse FMI data')
    parser.add_argument('--input_directory', type=str, help='Input directory', required=True)
    parser.add_argument('--output_directory', type=str, help='Output directory', required=True)
    args = parser.parse_args()
    process_fmi_data(args.input_directory, args.output_directory)
    
if __name__ == '__main__':
    main()