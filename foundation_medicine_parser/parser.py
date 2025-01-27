import dataclasses
import xml.etree.ElementTree as ET
import polars as pl
from dateutil import parser
import xlsxwriter
import pathlib
from rich.progress import track

namespace = {'ns': 'http://foundationmedicine.com/compbio/variant-report-external'}

def get_xml_root_from_file(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root

def get_report_id(root):
    return root.find('.//ReportId').text

def short_variants(root):
    variants = []
    for variant in root.findall('.//ns:short-variant', namespace):
        variant_dict = {
            "report_id": get_report_id(root),
            "allele_fraction": float(variant.get('allele-fraction',0.0)),
            "cds_effect": variant.get('cds-effect'),
            "depth": int(variant.get('depth',0)),
            "equivocal": variant.get('equivocal'),
            "functional_effect": variant.get('functional-effect'),
            "gene": variant.get('gene'),
            "percent_reads": float(variant.get('percent-reads',0.0)),
            "position": variant.get('position',''),
            "protein_effect": variant.get('protein-effect'),
            "status": variant.get('status'),
            "strand": variant.get('strand'),
            "transcript": variant.get('transcript'),
        }
        variants.append(variant_dict)
        
    variants_df = pl.DataFrame(variants, schema=pl.Schema({
        "report_id": pl.Utf8,
        "allele_fraction": pl.Float64,
        "cds_effect": pl.Utf8,
        "depth": pl.Int64,
        "equivocal": pl.Utf8,
        "functional_effect": pl.Utf8,
        "gene": pl.Utf8,
        "percent_reads": pl.Float64,
        "position": pl.Utf8,
        "protein_effect": pl.Utf8,
        "status": pl.Utf8,
        "strand": pl.Utf8,
        "transcript": pl.Utf8,
        "sample": pl.Utf8
    }))
    
    return variants_df
def copy_number_alterations(root):
    cnas = []
    for cna in root.findall('.//ns:copy-number-alteration', namespace):
        cna_dict = {
            "report_id": get_report_id(root),
            "gene": cna.get('gene'),
            "type": cna.get('type'),
            "copy_number": float(cna.get('copy-number')),
            "ratio": float(cna.get('ratio')),
            "number_of_exons": cna.get('number-of-exons'),
            "position": cna.get('position'),
            "equivocal": cna.get('equivocal')
        }
        cnas.append(cna_dict)
    
    cnas_df = pl.DataFrame(cnas, schema=pl.Schema({
        "report_id": pl.Utf8,
        "gene": pl.Utf8,
        "type": pl.Utf8,
        "copy_number": pl.Float64,
        "ratio": pl.Float64,
        "number_of_exons": pl.Utf8,
        "position": pl.Utf8,
        "equivocal": pl.Utf8,
        "sample": pl.Utf8
    }))

    return cnas_df


def rearrangements(root):
    rearrangements = []
    for rearrangement in root.findall('.//ns:rearrangement', namespace):
        rearrangement_dict = {
            "report_id": get_report_id(root),
            "targeted_gene": rearrangement.get('targeted-gene'),
            "description": rearrangement.get('description'),
            "other_gene": rearrangement.get('other-gene'),
            "position_1": rearrangement.get('pos1'),
            "position_2": rearrangement.get('pos2'),
            "status": rearrangement.get('status'),
            "supporting_read_pairs": int(rearrangement.get('supporting-read-pairs')),
            "equivocal": rearrangement.get('equivocal')
        }
        rearrangements.append(rearrangement_dict)

    rearrangements_df = pl.DataFrame(rearrangements, schema=pl.Schema({
        "report_id": pl.Utf8,
        "targeted_gene": pl.Utf8,
        "description": pl.Utf8,
        "other_gene": pl.Utf8,
        "position_1": pl.Utf8,
        "position_2": pl.Utf8,
        "status": pl.Utf8,
        "supporting_read_pairs": pl.Int64,
        "equivocal": pl.Utf8
    }))
    
    return rearrangements_df

def biomarkers(root):
    biomarkers = []
    biomarkers_tag = root.find('.//ns:biomarkers', namespace)
    for biomarker in biomarkers_tag:
        biomarker_dict = {
            "report_id": get_report_id(root),
            "biomarker": biomarker.tag.split('}')[-1] if '}' in biomarker.tag else biomarker.tag,
            "status": biomarker.get('status', None),
            "score": float(biomarker.get('score')) if biomarker.get('score') else None,
            "unit": biomarker.get('unit', None),
        }
        biomarkers.append(biomarker_dict)
        
    biomarkers_df = pl.DataFrame(biomarkers, schema=pl.Schema({
        "report_id": pl.Utf8,
        "biomarker": pl.Utf8,
        "status": pl.Utf8,
        "score": pl.Float64,
        "unit": pl.Utf8
    }))
        
    return biomarkers_df

def assay_and_patient_data(root):
    pmi_tag = root.find('.//PMI')
    
    name_mapping = {
        "ReportId": "report_id",
        "MRN": "mrn",
        "DOB": "dob",
        "FullName": "full_name",
        "FirstName": "first_name",
        "LastName": "last_name",
        "SubmittedDiagnosis": "submitted_diagnosis",
        "Gender": "gender",
        "OrderingMD": "ordering_md",
        "OrderingMDId": "ordering_md_id",
        "Pathologist": "pathologist",
        "MedFacilName": "medical_facility_name",
        "MedFacilID": "medical_facility_id",
        "SpecSite": "specimen_site",
        "CountryOfOrigin": "country_of_origin",
        "CollDate": "collection_date",
        "ReceivedDate": "received_date",
    }
    
    res = {}
    for (tag, name) in name_mapping.items():
        try:
            res[name] = pmi_tag.find('./'+tag).text
        except AttributeError:
            res[name] = None

    # Parse dates
    for date_field in ['dob', 'collection_date', 'received_date']:
        if date_field in res and res[date_field]:
            res[date_field] = parser.parse(res[date_field])     
        
    report_data_tag = root.find('.//ns:variant-report', namespace)
    report_data = {
        "disease": report_data_tag.get('disease'),
        "disease_ontology": report_data_tag.get('disease-ontology'),
        "gender": report_data_tag.get('gender'),
        "pathology_diagnosis": report_data_tag.get('pathology-diagnosis'),
        "purity_estimate": float(report_data_tag.get('purity-assessment')) if report_data_tag.get('purity-assessment') else None,
        "specimen": report_data_tag.get('specimen'),
        "study": report_data_tag.get('study'),
        "test_request": report_data_tag.get('test-request'),
        "test_type": report_data_tag.get('test-type'),
    }
    res.update(report_data)
    res2 = pl.DataFrame(res, schema=pl.Schema({
        "report_id": pl.Utf8,
        "mrn": pl.Utf8,
        "dob": pl.Date,
        "collection_date": pl.Date,
        "received_date": pl.Date,
        "first_name": pl.Utf8,
        "last_name": pl.Utf8,
        "full_name": pl.Utf8,
        "submitted_diagnosis": pl.Utf8,
        "gender": pl.Utf8,
        "ordering_md": pl.Utf8,
        "ordering_md_id": pl.Utf8,
        "pathologist": pl.Utf8,
        "medical_facility_name": pl.Utf8,
        "medical_facility_id": pl.Utf8,
        "specimen_site": pl.Utf8,
        "country_of_origin": pl.Utf8,
        "disease": pl.Utf8,
        "disease_ontology": pl.Utf8,
        "pathology_diagnosis": pl.Utf8,
        "purity_estimate": pl.Float64,
        "specimen": pl.Utf8,
        "study": pl.Utf8,
        "test_request": pl.Utf8,
        "test_type": pl.Utf8,
    }))
    
    return res2
    

@dataclasses.dataclass
class ReportFrameContainer:
    short_variants: pl.DataFrame
    copy_number_alterations: pl.DataFrame
    rearrangements: pl.DataFrame
    biomarkers: pl.DataFrame
    assay_and_patient_data: pl.DataFrame
    
def generate_report_frames(report_files):
    report_frames = []
    
    for report_file in track(report_files):
        root = get_xml_root_from_file(report_file)
        short_variants_df = short_variants(root)
        copy_number_alterations_df = copy_number_alterations(root)
        rearrangements_df = rearrangements(root)
        biomarkers_df = biomarkers(root)
        assay_and_patient_data_df = assay_and_patient_data(root)
        
        report_frame_container = ReportFrameContainer(
            short_variants=short_variants_df,
            copy_number_alterations=copy_number_alterations_df,
            rearrangements=rearrangements_df,
            biomarkers=biomarkers_df,
            assay_and_patient_data=assay_and_patient_data_df
        )
        report_frames.append(report_frame_container)
        
    return report_frames

def write_report_frames_to_excel(report_frames, output_file):
    
    output_directory = output_file.parent
    output_directory.mkdir(parents=True, exist_ok=True)
    
    with xlsxwriter.Workbook(output_file) as writer:
        
        assay_and_patient_data_dfs = [getattr(rep, 'assay_and_patient_data') for rep in report_frames]
        assay_and_patient_data_df = pl.concat(assay_and_patient_data_dfs)
        assay_and_patient_data_df.write_excel(writer, worksheet='assay_and_patient_data')
        
        for field in dataclasses.fields(report_frames[0]):
            if field.name == 'assay_and_patient_data':
                continue
            l = [getattr(rep, field.name) for rep in report_frames]
            df = pl.concat(l)
            df_final = df.join(assay_and_patient_data_df, on='report_id')
            df_final.write_excel(writer, worksheet=field.name)
    
    return str(output_file)
            
def write_report_frames_to_csv(report_frames, output_directory):
    
    output_directory.mkdir(parents=True, exist_ok=True)
    
    assay_and_patient_data_dfs = [getattr(rep, 'assay_and_patient_data') for rep in report_frames]
    assay_and_patient_data_df = pl.concat(assay_and_patient_data_dfs)
    assay_and_patient_data_df.write_csv(output_directory / 'assay_and_patient_data.csv')
    
    for field in dataclasses.fields(report_frames[0]):
        if field.name == 'assay_and_patient_data':
            continue
        l = [getattr(rep, field.name) for rep in report_frames]
        df = pl.concat(l)
        df_final = df.join(assay_and_patient_data_df, on='report_id')
        df_final.write_csv(output_directory / (field.name + '.csv'))
        
    output_files = [str(output_directory / (field.name + '.csv')) for field in dataclasses.fields(report_frames[0])]
    return output_files


def process_fmi_data(input_directory, output_directory) -> dict:
    results_path = pathlib.Path(input_directory)
    output_path = pathlib.Path(output_directory)
    report_files = list(results_path.glob('*.xml'))
    report_frames = generate_report_frames(report_files)
    csv_files = write_report_frames_to_csv(report_frames, output_path)
    excel_file = write_report_frames_to_excel(report_frames, output_path / 'fmi_report.xlsx')
    return {"csv_files": csv_files, "excel_file": excel_file, "report_count": len(report_files)}