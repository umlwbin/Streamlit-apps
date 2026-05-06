# %%
import requests
import json
import pandas as pd
from IPython.display import display, Markdown
def printmd(string):
    display(Markdown(string))

# %%
input_dir='/Users/yaniquecampbell/Desktop/ckan_api_upload/'
#ADD CURATOR AUTHORIZATION HERE
headers={'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJOUkdpekI1TWFONnJwZk5GV2JRR1pvSUI4REZja3N3S294OE1CZTBPQWNBIiwiaWF0IjoxNzQ1MzQ3OTM1fQ.xLC9YX2DKHRiUE3368TKqvLIKo6zkhhcGDbEeLxP6C4'}


def read_file():
    #File with submissions
    excel_file=input_dir+'submissions.xlsx'

    #Read the submissions excel file
    df=pd.read_excel(excel_file, index_col=0)
    df = df.reset_index()
    df = df.fillna('')
    
    #Get the excel file headers
    cols= df.columns

    #Next function
    create_dataset_dict(df)


# %%
def grab_keywords(df, index):
    #Grab the keywords
    all_keywords=df['Keywords *']
    all_keywords_strings=str(all_keywords[index])
    keywords=all_keywords_strings.split(',')
    
    list_of_keyword_dicts=[]
    for k in keywords:
        keyword_dict={"display_name":k, "name":k}
        list_of_keyword_dicts.append(keyword_dict)

    #display(list_of_keyword_dicts)
    return list_of_keyword_dicts


# %%
def grab_authors(df, index):
    # Grab the author info
    author_dict_list=[]
    all_authors=df['Dataset Author(s)']
    s=str(all_authors[index])
    start = 'Name *: '
    end = ', Type of Name *'
    author_name= (s[s.find(start)+len(start):s.rfind(end)])
    #-------------------------------
    start = 'Type of Name *: '
    end = ', Email *'
    author_type=(s[s.find(start)+len(start):s.rfind(end)])
    #-------------------------------
    start = 'Email *: '
    end = ', Affiliation *'
    author_email=(s[s.find(start)+len(start):s.rfind(end)])
    #-------------------------------
    start = 'Affiliation *: '
    end = ', ORCID ID:'
    author_aff=(s[s.find(start)+len(start):s.rfind(end)])
    #-------------------------------
    author_orcid=s.partition('ORCID ID: ')[-1]

    author_dict={"author":author_name, "nameType":author_type, 
                "creatorEmail":author_email, "creatorAffiliation":author_aff, "creatorNameIdentifier":author_orcid}
    author_dict_list.append(author_dict)

    return author_dict_list


# %%
def grab_contributors(df, index):

    # Grab the contributor info
    contributor_dict_list=[]
    all_contributors=df['Contributor(s)']
    s=str(all_contributors[index])
    start = 'Name: '
    end = ', Role:'
    contributor_name= (s[s.find(start)+len(start):s.rfind(end)])
    #-------------------------------
    start = 'Role: '
    end = ', Email'
    contributor_type=(s[s.find(start)+len(start):s.rfind(end)])
    #-------------------------------
    start = 'Email: '
    end = ', Affiliation'
    contributor_email=(s[s.find(start)+len(start):s.rfind(end)])
    #-------------------------------
    start = 'Affiliation: '
    end = ', ORCID ID:'
    contributor_aff=(s[s.find(start)+len(start):s.rfind(end)])
    #-------------------------------
    contributor_orcid=s.partition('ORCID ID: ')[-1]

    contributor_dict={"contributorName":contributor_name, "contributorType":contributor_type, 
                "email":contributor_email, "affiliation":contributor_aff, "nameIdentifier":contributor_orcid}
    contributor_dict_list.append(contributor_dict)  

    return contributor_dict_list  


# %%
def grab_data_curator_info(df, index):
    # Grab the data curator info
    all_dc=df['Data Curator']
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
    

# %%
def grab_dataset_name(row):
    #Get the name (this will be the URL)
    title=row['Dataset Name *']
    name=title.replace(" ", "_")
    name=name.lower()

    return title, name

# %%
def create_dataset_dict(df):
    #Loop through all rows in the dataframe to grab the metadata 
    for index, row in df.iterrows():
        if index>0:
            break

        list_of_keyword_dicts=grab_keywords(df, index)
        author_dict_list = grab_authors(df, index)
        contributor_dict_list= grab_contributors(df, index)
        dc_name,dc_email,dc_aff=grab_data_curator_info(df, index)
        title,name=grab_dataset_name(row)

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
        "ResourceType":row['Dataset Type *'],
        "tags":list_of_keyword_dicts,
        "status": row['Dataset Status *'],
        "Version": row['Version *'],
        "frequency":row['Maintenance and Update Frequency *'],
        "Date": str(row['Dataset Last Revision Date *']),
        "metadata_created": str(row['Metadata Creation Date *']),

        "creatorName":author_dict_list,
        "contributors":contributor_dict_list,
        "contributorName": dc_name,
        "dataCuratorEmail": dc_email,
        "dataCuratorAffiliation":dc_aff,
        "startDate": str(row['Dataset Collection Start Date *']),
        "startDateType": "Collected",
        "endDate": str(row['Dataset Collection End Date']), 
        "endDateType": "Other",

        "licenceType": "Open",
        "Rights": "Creative Commons Attribution 4.0 International",
        "rightsIdentifierScheme":"SPDX",
        "accessTerms": "CanWIN datasets are licensed individually, however most are licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) Public License. Details for the licence applied can be found using the Licence URL link provided with each dataset. \r\nBy using data and information provided on this site you accept the terms and conditions of the License. Unless otherwise specified, the license grants the rights to the public to use and share the data and results derived therefrom as long as the proper acknowledgment is given to the data licensor (citation), that any alteration to the data is clearly indicated, and that a link to the original data and the license is made available.",
        "useTerms": "By accessing this data you agree to [CanWIN's Terms of Use](/data/publication/canwin-data-statement/resource/5b942a87-ef4e-466e-8319-f588844e89c0).",
    #   "awards": [{"awardTitle": " ", "awardURI": "", "funderIdentifierType": "", "funderName": ""}],
        "awards": [{"awardTitle": "BaySys funding", "awardURI": "", "funderIdentifierType": "", "funderName": "NSERC, Manitoba Hydro, ArcticNet, Ouranos, Hydro Quebec, the Canada Excellence Research Chair (CERC) and the Canada Research Chairs (CRC) programs.", "funderSchemeURI": ""}],

        #Facility
        "owner_org":"6e137c7a-cdb7-4cff-a82c-f5ef0124e943"
        }

    upload_metadata(dataset_dict)

# %%
def upload_metadata(dataset_dict):
    endpoint_p="https://canwin-datahub.ad.umanitoba.ca/data/api/3/action/package_create"
    req_p= requests.post(endpoint_p, json=dataset_dict, headers=headers)
    #jsonResponse = req_p.json()
    #print(json.dumps(jsonResponse, indent=4))

# %%
def main():
    read_file()

main()


