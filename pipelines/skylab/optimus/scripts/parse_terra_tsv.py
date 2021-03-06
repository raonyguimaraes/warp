import argparse
import pandas as pd
import numpy as np
"""
A script for parsing a tsv file from Terra generated by the HCA data store handoff. Produces 2 tsv files to be uploaded 
to Terra.
Input: 
    A tsv file with data from HCA exported to terra. May include several fastq file sets per row.
Outputs: 
    Modified tsv file with one row for each set of fastq files to be imported to Terra
    Sample set TSV to be uploaded to terra. The samples will be grouped by sample_id.
"""
def create_output_files(input_file,output_file,output_set,output_entity):
    """
    Args:
        input_file: tsv file from HCA
	index: the read index if they are multiple
    """
    df = pd.read_table(input_file)

    r1_fastq = df[df.columns[pd.Series(df.columns).str.startswith('__fastq_read1') & pd.Series(df.columns).str.endswith('drs_uri')]]
    r2_fastq = df[df.columns[pd.Series(df.columns).str.startswith('__fastq_read2') & pd.Series(df.columns).str.endswith('drs_uri')]]
    i1_fastq = df[df.columns[pd.Series(df.columns).str.startswith('__fastq_index') & pd.Series(df.columns).str.endswith('drs_uri')]]
    r1_fastq_uuid = df[df.columns[pd.Series(df.columns).str.startswith('__fastq_read1') & pd.Series(df.columns).str.endswith('__file_uuid')]]
    r2_fastq_uuid = df[df.columns[pd.Series(df.columns).str.startswith('__fastq_read2') & pd.Series(df.columns).str.endswith('__file_uuid')]]
    i1_fastq_uuid = df[df.columns[pd.Series(df.columns).str.startswith('__fastq_index') & pd.Series(df.columns).str.endswith('__file_uuid')]]
    r1_fastq_document_id = df[df.columns[pd.Series(df.columns).str.startswith('__fastq_read1') & pd.Series(df.columns).str.endswith('__file_document_id')]]
    r2_fastq_document_id = df[df.columns[pd.Series(df.columns).str.startswith('__fastq_read2') & pd.Series(df.columns).str.endswith('__file_document_id')]]
    i1_fastq_document_id = df[df.columns[pd.Series(df.columns).str.startswith('__fastq_index') & pd.Series(df.columns).str.endswith('__file_document_id')]]
    
    print( r1_fastq.shape,r1_fastq_uuid.shape,r1_fastq_document_id.shape)
#TBD: move this to a function and call on each row of df change. Note: change index 0 to get other participants
    # for each fastq read, create a lane
    n_lanes = r1_fastq.shape[1] - r1_fastq.isnull().sum(axis=1) #number of fastq reads
    n_participants = r1_fastq.shape[0] #number of participants
    column_names = ['entity:participant_lane_id', 'input_id', 'input_name','input_id_metadata_field','input_name_metadata_field', 'r1_fastq','r2_fastq', 'i1_fastq', 'r1_fastq_uuid', 'r2_fastq_uuid', 'i1_fastq_uuid']
    participant_df = pd.DataFrame(columns = column_names)
    for j in range(n_participants):
        a  = []
        n_lane = int(n_lanes[j])
        print(n_lane)
        for i in range(int(n_lane)):
            a.append("participant_"+str(j)+"_lane_"+str(i)+"_"+str(df.sequencing_process__provenance__document_id[j])+"_id")
        lane_id = pd.DataFrame({"entity:participant_lane_id":a})
        lane_fastq_r1 = pd.DataFrame({"fastq1":r1_fastq.iloc[j].to_numpy()[:n_lane]})
        lane_fastq_r2 = pd.DataFrame({"fastq2":r2_fastq.iloc[j].to_numpy()[:n_lane]})
        lane_fastq_i1 = pd.DataFrame({"fastqi":i1_fastq.iloc[j].to_numpy()[:n_lane]})
        lane_fastq_r1_uuid = pd.DataFrame({"fastq1_uuid":r1_fastq_uuid.iloc[j].to_numpy()[:n_lane]})
        lane_fastq_r2_uuid = pd.DataFrame({"fastq2_uuid":r2_fastq_uuid.iloc[j].to_numpy()[:n_lane]})
        lane_fastq_i1_uuid = pd.DataFrame({"fastqi_uuid":i1_fastq_uuid.iloc[j].to_numpy()[:n_lane]})
        lane_r1_fastq_document_id = pd.DataFrame({"fastq1_document_id":r1_fastq_document_id.iloc[j].to_numpy()[:n_lane]})
        lane_r2_fastq_document_id = pd.DataFrame({"fastq2_document_id":r2_fastq_document_id.iloc[j].to_numpy()[:n_lane]})
        lane_i1_fastq_document_id = pd.DataFrame({"fastqi1_document_id":i1_fastq_document_id.iloc[j].to_numpy()[:n_lane]})
    
        
        
        input_id = pd.DataFrame({"input_id":np.repeat(df.sequencing_process__provenance__document_id[j],n_lanes[j])})
        input_id_metadata_field = pd.DataFrame({"input_id_metadata_field":np.repeat("sequencing_process.provenance.document_id",n_lanes[j])})
        input_name = pd.DataFrame({"input_name":np.repeat(df.sequencing_input__biomaterial_core__biomaterial_id[j],n_lanes[j])})
        input_name_metadata_field = pd.DataFrame({"input_name_metadata_field":np.repeat("sequencing_input.biomaterial_core.biomaterial_id",n_lanes[j])})
    
        column_names = ['entity:participant_lane_id', 'input_id', 'input_name','input_id_metadata_field','input_name_metadata_field', 
                        'r1_fastq','r2_fastq', 'i1_fastq','r1_fastq_uuid','r2_fastq_uuid', 'i1_fastq_uuid',
                       'r1_fastq_document_id','r2_fastq_document_id','i1_fastq_document_id']
    
        lane_df = pd.concat([lane_id,
                        input_id,
                        input_name,
                        input_id_metadata_field,
                        input_name_metadata_field,
                        lane_fastq_r1,
                        lane_fastq_r2,
                        lane_fastq_i1,
                        lane_fastq_r1_uuid,
                        lane_fastq_r2_uuid,
                        lane_fastq_i1_uuid,
                        lane_r1_fastq_document_id,
                        lane_r2_fastq_document_id,
                        lane_i1_fastq_document_id
                       ],
                   axis=1)
        lane_df.columns = column_names
        participant_df = participant_df.append(lane_df)
        print(participant_df.shape)      
    participant_lane_df = participant_df.dropna()
    participant_df.to_csv(output_file,sep="\t",index=None)
    #print(out_df.shape,out_df.columns,out_df.r2_fastq)
    particpant_set_df = participant_df[['input_id','entity:participant_lane_id']]
    particpant_set_df.columns = ['membership:participant_lane_set_id', 'participant_lane']
    particpant_set_df.to_csv(output_set,sep="\t",index=None)
    temp = df[['sequencing_process__provenance__document_id','sequencing_input__biomaterial_core__biomaterial_id','project__provenance__document_id']]
    temp.columns = ['entity:participant_lane_set_id','input_name','project__provenance__document_id']
    temp.to_csv(output_entity,sep="\t",index=None)
def main():
    description = """This script converts the tsv file from HCA to data table to be used in terra.
"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--participant_file",
        dest="input_file",
        required=True,
        help="A tsv file with data from HCA exported to terra"
    )
    parser.add_argument(
        "--output_file",
        dest="output_file",
        required=True,
        help="Modfied tsv file to be imported to terra"
    )
    parser.add_argument(
        "--output_set",
        dest="output_set",
        required=True,
        help="Sample set TSV to be uploaded to terra"
    )
    parser.add_argument(
        "--output_entity",
        dest="output_entity",
        required=True,
        help="Additional columns for the sample set TSV to be uploaded to terra"
    )
    args = parser.parse_args()
    #print(args.output_file)
    create_output_files(args.input_file, args.output_file, args.output_set,args.output_entity)
if __name__ == "__main__":
    main()
