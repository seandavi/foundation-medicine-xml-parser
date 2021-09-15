# Initially downloaded after conversation with Matt Rioth/Jim Costello
#
# url for download: https://www.dropbox.com/s/ftwkozmk373t45s/fmi_report_data.py?dl=0
#
# Downloaded 2021-09-15

import xml.etree.ElementTree as et
from glob import glob
import pandas as pd
from os import path
import os
import datetime

'''
This script connects to the cc1 share drive with the SOM, 
parses and summarizes returned mutation information from the FMI patient reports 
in one Excel file, and outputs csvs for further analysis  
'''

cwd = os.getcwd()

fmi_dir = '/Volumes/cc1/FMI_reports/'

xml = fmi_dir + '/*.xml'
files = [path.basename(x) for x in glob(xml)]

global todays_date
now = datetime.datetime.now()
todays_date = now.strftime("%Y-%m-%d")

def report_variable_to_frame(root):
    
    report_detail = []
    report_dict = {}   
    
    for result in root.iter('{http://foundationmedicine.com/compbio/variant-report-external}variant-report'):
        result_dict = result.attrib
        report_detail.append(result_dict)
    for i in enumerate(report_detail):
        report_dict[i[0]] = (i[1])
    
        patient_report_detail = pd.DataFrame.from_dict(report_dict, orient='index', 
                    columns = ['test-request', 'specimen', 'disease', 'disease-ontology', 'gender', 'pathology-diagnosis', 'tissue-of-origin', 'purity-assessment'])
    
    treq = ttype = recd = seqd = fullname = mrn = dob = ''
    colld = biop = ordmd = medfnm = medfid = spec = ''
    diag = dis = disOnt = pathd = orig = pure = qual = ''
    
    for repId in root.iter('ReportId'):
        treq = repId.text
    for test in root.iter('TestType'):
        ttype = test.text
    for receipt in root.iter('ReceivedDate'):
        recd = receipt.text
        dt = datetime.datetime.strptime(recd, "%Y-%m-%d")
        seqd = dt.strftime("%m-%d-%Y") 
    for colldate in root.iter('CollDate'):
        colld = colldate.text
        dt = datetime.datetime.strptime(colld, "%Y-%m-%d")
        biop = dt.strftime("%m-%d-%Y")
    for doctor in root.iter('OrderingMD'):
        ordmd = doctor.text
    for ptntname in root.iter('FullName'):
        fullname = ptntname.text
    for mrnumber in root.iter('MRN'):
        mrn = mrnumber.text
    for birthdate in root.iter('DOB'):
    	dob = birthdate.text
    for inst in root.iter('MedFacilName'):
        facnm = inst.text
    for facil in root.iter('MedFacilID'):
        facid = facil.text
    for site in root.iter('SpecSite'):
        spec = site.text
    for submDiag in root.iter('SubmittedDiagnosis'):
        diag = submDiag.text
    for qc in root.iter('{http://foundationmedicine.com/compbio/variant-report-external}quality-control'):
        qual = qc.attrib
        qcstat = qual.get('status', 0)
     
    dd = {'ReportId': [treq], 'TestType': [ttype], 'Disease': [dis], 'DiseaseOntology': [disOnt], 'PathologyDiagnosis': [pathd],
          'SubmittedDiagnosis': [diag], 'OrderingMD': [ordmd], 'Patient': [fullname], 'MRN': [mrn], 'DOB': [dob], 'SpecimenSite': [spec], 'TissueOfOrigin': [orig], 
          'DateSequenced': [seqd], 'DateCollected': [biop], 'Facility': [facnm], 'FacilityId': [facid], 'Purity': [pure], 'QualityControl': [qcstat]}    
    
    patient_report_frame = pd.DataFrame.from_dict(dd, orient='columns')                                                                              
    merged_fields = patient_report_frame.merge(patient_report_detail, how='outer', left_on='ReportId', right_on='test-request') 
    merged_fields['Disease'] = merged_fields['disease']
    merged_fields['DiseaseOntology'] = merged_fields['disease-ontology']
    merged_fields['PathologyDiagnosis'] = merged_fields['pathology-diagnosis']
    merged_fields['TissueOfOrigin'] = merged_fields['tissue-of-origin']
    merged_fields['Purity'] = merged_fields['purity-assessment']
    output = merged_fields[['ReportId', 'TestType', 'Disease', 'DiseaseOntology', 'PathologyDiagnosis', 'SubmittedDiagnosis', 'OrderingMD', 'Patient', 'MRN', 'DOB', 'SpecimenSite', 'TissueOfOrigin', 'DateSequenced', 'DateCollected', 'Facility', 'FacilityId', 'Purity', 'QualityControl']]
    
    return output

def short_variables_to_frame(root):
    variant_results = []
    variant_dict = {}
    for result in root.iter('{http://foundationmedicine.com/compbio/variant-report-external}short-variant'):
        row_result = result.attrib
        variant_results.append(row_result)
    for i in enumerate(variant_results):
        variant_dict[i[0]] = (i[1])
    variant_report = pd.DataFrame.from_dict(variant_dict, orient='index', 
                columns = ['gene', 'position', 'cds-effect', 'protein-effect', 'transcript', 'allele-fraction', 'depth', 'functional-effect', 'status', 'strand', 'equivocal'])
    for prop in root.iter('ReportId'):
        variant_report['Patient'] = prop.text

    variant_frame = variant_report.rename( columns={'Patient': 'ReportId',
                                                           'gene': 'Gene', 
                                                           'position': 'Position', 
                                                           'protein-effect': 'ProteinEffect',
                                                           'functional-effect': 'FunctionalEffect', 
                                                           'cds-effect': 'CdsEffect',
                                                           'transcript': 'Transcript',
                                                           'allele-fraction': 'AlleleFraction',
                                                           'depth': 'Depth', 
                                                           'status': 'Status',
                                                           'strand': 'Strand',
                                                           'equivocal': 'Equivocal'})
                                                           

        
    return variant_frame

def cna_requests_frame(root):
    
    cna_results = []
    cna_dict = {}

    for result in root.iter('{http://foundationmedicine.com/compbio/variant-report-external}copy-number-alteration'):
        row_result = result.attrib
        cna_results.append(row_result)
    for i in enumerate(cna_results):
        cna_dict[i[0]] = (i[1])
        
    cna_report = pd.DataFrame.from_dict(cna_dict, orient='index', columns = ['copy-number', 'equivocal', 'gene', 'ratio', 'status', 'type', 'number-of-exons', 'position'])
    for prop in root.iter('ReportId'):
        cna_report['Patient'] = prop.text
    
    cna_frame = cna_report.rename(columns={'Patient': 'ReportId',
                                                   'gene': 'Gene',
                                                   'type': 'Type',
                                                   'copy-number': 'CopyNumber', 
                                                   'status': 'Status',
                                                   'ratio': 'Ratio',
                                                   'number-of-exons': 'NumberOfExons',
                                                   'position': 'Position',
                                                   'equivocal': 'Equivocal'})
    return cna_frame
                             
def fusion_requests(root):
    
    fun_results = []
    fun_dict = {}
    
    for result in root.iter('{http://foundationmedicine.com/compbio/variant-report-external}rearrangement'):
        row_result = result.attrib
        fun_results.append(row_result)
    for i in enumerate(fun_results):
        fun_dict[i[0]] = (i[1])
    fun_report = pd.DataFrame.from_dict(fun_dict, orient='index', columns = ['description', 'type', 'in-frame', 'targeted-gene', 'other-gene', 
                                                                             'pos1', 'pos2', 'status', 'in-frame', 'supporting-read-pairs', 'equivocal'])
    for prop in root.iter('ReportId'):
        fun_report['Patient'] = prop.text
    
    fzn_frame = fun_report.rename( columns={'Patient': 'ReportId',
                                                   'targeted-gene': 'TargetedGene',
                                                   'description': 'Description',
                                                   'other-gene': 'OtherGene', 
                                                   'pos1': 'Pos1', 
                                                   'pos2': 'Pos2',
                                                   'type': 'Type',
                                                   'in-frame': 'InFrame',
                                                   'status': 'Status',
                                                   'supporting-read-pairs': 'SupportingReadPairs',
                                                   'equivocal': 'Equivocal'})
        
    return fzn_frame

# remove anonymous DenMel patients
anon_mel = ['TRF195670', 'TRF195671', 'TRF195674', 'TRF195675', 'TRF195678', 
            'TRF195679', 'TRF195681', 'TRF195682', 'TRF195683', 'TRF195686', 
            'TRF195687', 'TRF195688', 'TRF195692', 'TRF195696', 'TRF195868', 
            'TRF195869', 'TRF195887', 'TRF244635']

anon_mel_xml = [elem + '.xml' for elem in anon_mel]
clean_files = [elem for elem in files if elem not in anon_mel_xml]
files = clean_files

patientframe = pd.DataFrame()
variantframe = pd.DataFrame()
copyframe = pd.DataFrame()
funframe = pd.DataFrame()

for file in files:
    
    tree = et.parse(fmi_dir + file)
    root = tree.getroot()
    
    df = report_variable_to_frame(root)
    sv = short_variables_to_frame(root)
    cf = cna_requests_frame(root)
    fu = fusion_requests(root)
    
    funframe = funframe.append(fu)
    patientframe = patientframe.append(df)
    variantframe = variantframe.append(sv)
    copyframe = copyframe.append(cf)


run_date = (cwd + '/' + todays_date + '/')
if not os.path.exists(run_date):
    os.mkdir(run_date)
    
funframe.to_csv(run_date + 'Rearrangement_' + todays_date + '.csv',  index=False)
copyframe.to_csv(run_date + 'Copy_Number_Alteration_' + todays_date + '.csv',  index=False)
variantframe.to_csv(run_date + 'Short_Variant_' + todays_date + '.csv',  index=False)
patientframe.to_csv(run_date + 'Test_Data_' + todays_date + '.tsv',  sep='\t', index=False)

with pd.ExcelWriter(run_date + 'FMI_tables_' + todays_date + '.xlsx') as writer:

    patientframe.to_excel(writer, sheet_name='FMI_Test_Data', index=False)
    variantframe.to_excel(writer, sheet_name='FMI_Short_Variant', index=False)
    copyframe.to_excel(writer, sheet_name='FMI_Copy_Number_Alteration', index=False)
    funframe.to_excel(writer, sheet_name='FMI_Rearrangement', index=False)
