# streamlit_app.py
import streamlit as st
import pandas as pd
import requests
import json
import re
from datetime import datetime

# Page Setup
st.set_page_config(page_title="CKAN Dataset Page Upload & Delete - from Jotform Excel File", layout="centered")
st.title("📦 CKAN Dataset Upload & Delete")
st.info(''' 
    This app uploads or deletes a dataset to/from CKAN, using an excel submissions file generated from Jotform.
    
    Please see the **submissions.xlsx** file as an example of what the fields look like. 
    ''')

# Session States
if "pwdSuccess" not in st.session_state:
    st.session_state.pwdSuccess=False

with st.sidebar:
    # Define your app password (hardcoded for simplicity)
    APP_PASSWORD = "canwin123"

    st.markdown('# 🕵🏻‍♀️ Please Enter CanWIN Password')
    password = st.text_input("Password", type="password", key='pwd')

    st.markdown('##### ')
    if password == APP_PASSWORD:
        st.session_state.pwdSuccess=True
        st.success("Welcome you beautiful Data Legend!! 😎")
        st.markdown(" ")
        st.markdown("# 🔐 CKAN API Authentication")
        ckan_api_key = st.text_input("Enter your CKAN API Key", type="password", key="apiKey", value='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJOUkdpekI1TWFONnJwZk5GV2JRR1pvSUI4REZja3N3S294OE1CZTBPQWNBIiwiaWF0IjoxNzQ1MzQ3OTM1fQ.xLC9YX2DKHRiUE3368TKqvLIKo6zkhhcGDbEeLxP6C4')
        ckan_base_url = st.text_input("Enter CKAN Base URL (e.g., https://data.example.com)",key= "baseURL", value="https://canwin-datahub.ad.umanitoba.ca/data")

    elif password:
        st.error("Incorrect password ❌")

# Tabs
st.markdown(" ")
tab1, lilSpace, tab2 = st.tabs(["⬆️ **Upload Dataset**", " ", "❌ **Delete Dataset**"])

with tab1:
    # Start Workflow!                 
    def start_upload_workflow():
        read_file()

    def read_file():
        st.subheader("📂 File Upload")
        st.markdown("###### Upload an Excel file with metadata to create a CKAN dataset page.")

        def change_file():
            st.session_state.upload_processed = False


        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"], on_change=change_file)
        if uploaded_file and ("upload_processed" not in st.session_state or st.session_state.upload_processed==False):
            try:
                df = pd.read_excel(uploaded_file)
                # Normalize column names: strip whitespace and lowercase
                normalized_cols = [col.strip() for col in df.columns]
                df.columns=normalized_cols

                #Now file has been processed
                st.session_state.upload_processed = True

                st.success("File uploaded successfully!")
                st.dataframe(df.head())  # Preview first few rows
            except Exception as e:
                st.error(f"Error reading file: {e}")

            if not df.empty:
                
                #Check if there is a Dataset Type *, I removed from the form in later versions to make it easier for researchers. 
                if 'Dataset Type *' in df.columns:
                    st.session_state['res']=False
                    create_dataset_dict(df, normalized_cols)
                else:
                    if not st.session_state.get('res'):
                        enter_resource_type()

                    if st.session_state.get('res'):
                        create_dataset_dict(df, normalized_cols)
                        
    def enter_resource_type():
        st.markdown(" ")
        st.subheader("✍🏼 Additional Metadata Input")

        # Let the user enter ResourceType manually
        st.text_input("Enter Resource Type (e.g., mooring data)", key="res")

    def grab_keywords(df, index, normalized_cols):

        # Partial string to search for
        search_term = 'keywords'

        # Find matching columns (case-insensitive)
        matching_cols = [col for col in normalized_cols if search_term.lower() in col.lower()]
        columnName=matching_cols[0]

        #Grab the keywords
        all_keywords=df[columnName]
        all_keywords_strings=str(all_keywords[index])
        keywords=all_keywords_strings.split(',')
        
        list_of_keyword_dicts=[]
        for k in keywords:
            keyword_dict={"display_name":k, "name":k}
            list_of_keyword_dicts.append(keyword_dict)

        return list_of_keyword_dicts

    def extract_author_blocks(text, anchor):
        """
        Extracts multiple author blocks from a metadata string.
        Each block starts with 'Name *:' and ends before the next 'Name *:' or end of string.
        """
        if not isinstance(text, str):
            return []

        # Find all true block starts: 'Name *:' followed by a value
        matches = list(re.finditer(rf'(?<!Type of )({re.escape(anchor)}\s*[^:,]+)', text))

        blocks = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            block = text[start:end].strip()
            blocks.append(block)

        return blocks

    def extract_metadata_value(text, start_marker, end_marker=None):
        try:
            start_idx = text.find(start_marker)
            if start_idx == -1:
                return ""
            start_idx += len(start_marker)

            if end_marker:
                end_idx = text.find(end_marker, start_idx)
                if end_idx == -1:
                    value = text[start_idx:]
                else:
                    value = text[start_idx:end_idx]
            else:
                value = text[start_idx:]

            # Clean up newlines and extra spaces
            return value.replace('\n', ' ').replace('\r', ' ').strip()
        except Exception:
            return ""

    def clean_dict_values(d):
        return {k: v.replace('\n', ' ').replace('\r', ' ').strip() if isinstance(v, str) else v for k, v in d.items()}

    def grab_authors(df, index, normalized_cols):

        # Partial string to search for
        search_term = 'author'

        # Find matching columns (case-insensitive)
        matching_cols = [col for col in normalized_cols if search_term.lower() in col.lower()]
        columnName=matching_cols[0]

        # Grab the author info
        all_authors=df[columnName]
        raw_string=str(all_authors[index])

        author_blocks = extract_author_blocks(raw_string, anchor="Name *:")
        
        author_dict_list = []
        for block in author_blocks:
            author_dict = {
                "author": extract_metadata_value(block, "Name *: ", ", Type of Name *"),
                "nameType": extract_metadata_value(block, "Type of Name *: ", ", Email *"),
                "creatorEmail": extract_metadata_value(block, "Email *: ", ", Affiliation *"),
                "creatorAffiliation": extract_metadata_value(block, "Affiliation *: ", ", ORCID ID:"),
                "creatorNameIdentifier": extract_metadata_value(block, "ORCID ID: ")
            }
            author_dict_list.append(clean_dict_values(author_dict))

        return author_dict_list

    def grab_contributors(df, index, normalized_cols):

        # Partial string to search for
        search_term = 'contributor'

        # Find matching columns (case-insensitive)
        matching_cols = [col for col in normalized_cols if search_term.lower() in col.lower()]
        columnName=matching_cols[0]

        # Grab the contributor info
        all_contributors=df[columnName]
        raw_string=str(all_contributors[index])

        contributor_blocks = extract_author_blocks(raw_string, anchor="Name:")
        contributor_dict_list=[]
        for block in contributor_blocks:
            contributor_dict = {
                "contributorName": extract_metadata_value(block, "Name: ", ", Role"),
                "contributorType": extract_metadata_value(block, "Role: ", ", Email"),
                "email": extract_metadata_value(block, "Email: ", ", Affiliation"),
                "affiliation": extract_metadata_value(block, "Affiliation: ", ", ORCID ID:"),
                "nameIdentifier": extract_metadata_value(block, "ORCID ID: ")
            }
            contributor_dict_list.append(clean_dict_values(contributor_dict))

        return contributor_dict_list

    def grab_data_curator_info(df, index, normalized_cols):

        # Partial string to search for
        search_term = 'curator'

        # Find matching columns (case-insensitive)
        matching_cols = [col for col in normalized_cols if search_term.lower() in col.lower()]
        columnName=matching_cols[0]

        # Grab the data curator info
        all_dc=df[columnName]
        s=str(all_dc[index])
        start = 'Project Data Curator  *: '
        end = ', Data Curator Email *:'
        dc_name= (s[s.find(start)+len(start):s.rfind(end)])
        #-------------------------------
        start = 'Data Curator Email *: '
        end = ', Data Curator Affiliation:'
        dc_email=(s[s.find(start)+len(start):s.rfind(end)])
        #-------------------------------
        dc_aff=s.partition('Data Curator Affiliation: ')[-1]

        return dc_name,dc_email,dc_aff

    def grab_dataset_name(df, row, normalized_cols):

        # Partial string to search for
        search_term = 'dataset name'

        # Find matching columns (case-insensitive)
        matching_cols = [col for col in normalized_cols if search_term.lower() in col.lower()]
        columnName=matching_cols[0]

        #Get the name (this will be the URL)
        title=row[columnName]
        name=title.replace(" ", "_")
        name=name.lower()

        return title, name

    def normalize_date(date_str):
        """
        Convert dates like 'Sep 16, 2025' to '2025-09-16'.
        Returns empty string if parsing fails.
        """
        if not isinstance(date_str, str):
            return ""
        try:
            dt = datetime.strptime(date_str.strip(), "%b %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            # Try other formats if needed
            try:
                dt = pd.to_datetime(date_str)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                return ""

    def create_dataset_dict(df, normalized_cols):
       
       #Loop through all rows in the dataframe to grab the metadata 
        for index, row in df.iterrows():
            list_of_keyword_dicts=grab_keywords(df, index, normalized_cols)
            author_dict_list=grab_authors(df, index, normalized_cols)
            contributor_dict_list= grab_contributors(df, index, normalized_cols)
            dc_name,dc_email,dc_aff=grab_data_curator_info(df, index, normalized_cols)
            title,name=grab_dataset_name(df, row, normalized_cols)

            #Let's sort out resource_Type
            if st.session_state['res']==False: #There is no Dataset Type * in the excel file (not in the jotform)
                resource_type=row['Dataset Type *']
            else:
                resource_type=st.session_state['res']

            # Put the details of the dataset we're going to create into a dict--------------------------------------------------------------------------------------
            dataset_dict = {
            #Hardcoded.............................
            "descriptionType": "Abstract",
            "RelatedIdentifierType": "URL",
            "RelationType": "IsSupplementTo",
            "dateType": "Updated",
            "IdentifierType": "DOI",
            "Publisher": "CanWIN",
            "datasetPublisher": "CanWIN",
            "contributorType": "DataCurator",
            "rightsURI":"https://spdx.org/licenses/CC-BY-4.0.html",
            "rightsIdentifier":"CC-BY-4.0",

            #"resourceType": "Online Resource" is the only hard coded field for these two
            "supplementalResources": [{"RelatedIdentifier": "http://hdl.handle.net/20.500.11794/103946", "ResourceTypeGeneral": "Dissertation", "name": "Biodiversity, distribution and biomass of zooplankton and ichthyoplankton in the Hudson Bay system", "relatedIdentifierType": "URL", "relationship": "Describes", "resourceType": "Online Resource", "seriesName": ""}],
            "publications": [{"RelatedIdentifier": "", "ResourceTypeGeneral": "", "name": "", "relatedIdentifierType": "", "relationType": "", "resourceType": "Online Resource"}],

            #Required fields
            "name":name,
            "title": title,
            "type": "dataset",
            "private":True,
            "notes": row['Dataset Summary *'],
            "resourceTypeGeneral": 'Dataset',

            "ResourceType":resource_type,

            "tags":list_of_keyword_dicts,
            "status": row['Dataset Status *'],
            "Version": row['Version *'],
            "frequency":row['Maintenance and Update Frequency *'],
            
            "Date": normalize_date(row['Dataset Last Revision Date *']),
            "metadata_created": normalize_date(row['Metadata Creation Date *']),
            "startDate": normalize_date(row['Dataset Collection Start Date *']),
            "endDate": normalize_date(row['Dataset Collection End Date']),

            "creatorName":author_dict_list,
            "contributors":contributor_dict_list,
            "contributorName": dc_name,
            "dataCuratorEmail": dc_email,
            "dataCuratorAffiliation":"Centre for Earth Observation Science - University of Manitoba",

            "startDateType": "Collected",
            "endDateType": "Other",

            "licenceType": "Open",
            "Rights": "Creative Commons Attribution 4.0 International",
            "rightsIdentifierScheme":"SPDX",
            "accessTerms": "CanWIN datasets are licensed individually, however most are licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) Public License. Details for the licence applied can be found using the Licence URL link provided with each dataset. \r\nBy using data and information provided on this site you accept the terms and conditions of the License. Unless otherwise specified, the license grants the rights to the public to use and share the data and results derived therefrom as long as the proper acknowledgment is given to the data licensor (citation), that any alteration to the data is clearly indicated, and that a link to the original data and the license is made available.",
            "useTerms": "By accessing this data you agree to [CanWIN's Terms of Use](/data/publication/canwin-data-statement/resource/5b942a87-ef4e-466e-8319-f588844e89c0).",
            "awards": [{"awardTitle": " ", "awardURI": "", "funderIdentifierType": "", "funderName": ""}],
            #"awards": [{"awardTitle": "BaySys funding", "awardURI": "", "funderIdentifierType": "", "funderName": "NSERC, Manitoba Hydro, ArcticNet, Ouranos, Hydro Quebec, the Canada Excellence Research Chair (CERC) and the Canada Research Chairs (CRC) programs.", "funderSchemeURI": ""}],

            #Facility
            "owner_org":"6e137c7a-cdb7-4cff-a82c-f5ef0124e943"
            }


            upload_metadata(dataset_dict, index, name)

    def upload_metadata(dataset_dict, index, name):

            if ckan_api_key:
                headers = {
                    "Authorization": ckan_api_key,
                    "Content-Type": "application/json"
                }

                endpoint_p=f"{ckan_base_url}/api/3/action/package_create"
                req_p= requests.post(endpoint_p, json=dataset_dict, headers=headers)
                jsonResponse = req_p.json()

                if index==0:
                    st.markdown(" ")
                    st.subheader("📞 CKAN Response")
                if jsonResponse.get("success") is True:
                    st.success(f"🥳 Success!! Dataset **{name}** has been uploaded")
                    st.json(jsonResponse)  # Nicely formatted JSON viewer
                else:
                    st.error("❌ CKAN request failed")
                    st.write(jsonResponse)  # Optional: show raw response for debugging
            else:
                st.error("Please enter Authorization information")


    # Entry point
    if st.session_state.pwdSuccess ==True and st.session_state.get("apiKey") and st.session_state.get("baseURL"):
        start_upload_workflow()


with tab2:
    if st.session_state.pwdSuccess ==True and st.session_state.get("apiKey") and st.session_state.get("baseURL"):
        st.header("🗑️ Delete Dataset")

        dataset_id = st.text_input("Enter Dataset ID")
        ckan_api_key = st.text_input("Enter your CKAN API Key", type="password", value='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJOUkdpekI1TWFONnJwZk5GV2JRR1pvSUI4REZja3N3S294OE1CZTBPQWNBIiwiaWF0IjoxNzQ1MzQ3OTM1fQ.xLC9YX2DKHRiUE3368TKqvLIKo6zkhhcGDbEeLxP6C4', key='api2')
        ckan_base_url = st.text_input("Enter CKAN Base URL", value="https://canwin-datahub.ad.umanitoba.ca/data", key='baseUrl2')

        if st.button("Delete Dataset"):
            if not dataset_id or not ckan_api_key:
                st.error("Please provide both Dataset ID and API Key")
            else:
                headers = {
                    "Authorization": ckan_api_key,
                    "Content-Type": "application/json"
                }
                endpoint = f"{ckan_base_url}/api/3/action/package_delete"
                response = requests.post(endpoint, headers=headers, json={"id": dataset_id})
                jsonResponse = response.json()

                if jsonResponse.get("success") is True:
                    st.markdown(" ")
                    st.success(f"✅ Dataset {dataset_id} deleted successfully!")
                    st.json(jsonResponse)
                else:
                    st.markdown(" ")
                    st.error("❌ Failed to delete dataset.")
                    st.write(jsonResponse)


        