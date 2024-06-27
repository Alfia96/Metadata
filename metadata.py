from tabula import read_pdf
from pathlib import Path
import pandas as pd
import time
from datetime import timedelta

start_time = time.monotonic()


metadata_file = "metadata.xlsx"
reports_path = Path("./Reports")
scorpio_call_header = "Scorpio call"
pangolin_lineage_header = "Pangolin_Lineage"

def get_tables(pdf_name: str, insert_tables_dict: dict, error_files: list):
    tables_list_dict = {}

    #Reads the table from pdf file 
    try:
        list_of_tables = read_pdf(pdf_name, pages="all", multiple_tables=True)

        for each_table in list_of_tables:

            table_headers = each_table.columns.values.tolist()
            for each_table_header in table_headers:
                if each_table_header in insert_tables_dict.keys():
                    tables_list_dict[each_table_header] = each_table
    except:
        print(f"Couldn't read from the PDF: {pdf_name}. Skipping to the next.")
        error_files.append(str(pdf_name).rsplit("/")[-1])
        pass

    return tables_list_dict, error_files

def genome_insert(pdf_name, genome_table, metadata_df):
    barcode_id = pdf_name.split(".")[0]
    for index, row in genome_table.iterrows():
        genome_coverage = row['Genome.Coverage'].split(" ")[0]
        sample_value = row['Sample']
        try:
            metadata_df.loc[metadata_df['barcode'] == barcode_id, genome_coverage] = sample_value
        except:
            print(f"The Barcode ID {barcode_id} was not found in the Metadata Excel Sheet for genome insert. Skipping to the next.")
            pass

    return metadata_df

def pangolin_insert(pdf_name, lineage_table, metadata_df):
    barcode_id = pdf_name.split(".")[0]

    pangolin_lineage_value = lineage_table.iloc[0]["lineage"]
    try:
        metadata_df.loc[metadata_df['barcode'] == barcode_id, pangolin_lineage_header] = pangolin_lineage_value
    except:
        print(f"The Barcode ID {barcode_id} was not found in the Metadata Excel Sheet for pangolin lineage. Skipping to the next.")
        pass

    return metadata_df

def scorpio_insert(pdf_name, scorpio_table, metadata_df):
    barcode_id = pdf_name.split(".")[0]

    scorpio_call_value = scorpio_table.iloc[0]["scorpio_call"]
    try:
        metadata_df.loc[metadata_df['barcode'] == barcode_id, scorpio_call_header] = scorpio_call_value
    except:
        print(f"The Barcode ID {barcode_id} was not found in the Metadata Excel Sheet for scorpio insert. Skipping to the next.")
        pass

    return metadata_df
if __name__ == "__main__":

    insert_tables_dict = {
    "Genome.Coverage": genome_insert, 
    "scorpio_call": scorpio_insert,
    "lineage": pangolin_insert
    }

    metadata_df = pd.read_excel(metadata_file)

    barcode_files = reports_path.glob("**/*.pdf")
    error_files = []
    for each_barcode_file in barcode_files:

        pdf_name = str(each_barcode_file).rsplit("/")[-1]

        tables_list_dict, error_files = get_tables(each_barcode_file, insert_tables_dict, error_files)
        
        if not tables_list_dict:
            print(f"No viable tables found in the PDF: {pdf_name}.")
        else:
            for each_table_header, each_table in tables_list_dict.items():
                metadata_df = insert_tables_dict[each_table_header](pdf_name, each_table, metadata_df)

        metadata_df.to_excel(metadata_file, index=False)

    with open('error_pdfs.txt', mode='w', encoding='utf-8') as myfile:
        myfile.write('\n'.join(error_files))
        myfile.write('\n')

end_time = time.monotonic()
print("The time taken to run the code:", timedelta(seconds=end_time - start_time), "seconds")

