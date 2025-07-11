from github import Auth
from github import Github
import csv
import os
import streamlit as st

# Setup web page
st.set_page_config(
     page_title="GitHub Contributors",
     layout="wide"
)

st.markdown("""
    <style type="text/css">
        blockquote {
            margin: 1em 0px 1em -1px;
            padding: 0px 0px 0px 1.2em;
            font-size: 10px;
            border-left: 5px solid rgb(230, 234, 241);
            # background-color: #249edc;
            height: 50px;
        }
        blockquote p {
            font-size: 25px;
            color: #ffffff;
        }
        a.published {
            color: #249edc !important;
            text-decoration: none;
        }
        a.final {
            color: #ffffff !important;
            text-decoration: none;
        }
        a.hidden {
            color: red !important;
            text-decoration: none;
        }
        a.draft {
            color: #ffffff !important;
            text-decoration: none;
            font-style: italic;
        }
        a.updated {
            # color: #000000 !important;
            text-decoration: none;
        }
        p {
            color: rgb(129, 164, 182);
        }
        div[data-testid='stExpanderDetails'] p {
            color: #ffffff;
        }
        input {
            background-color: #115675 !important;
        }
        .st-b6 {
            color: #000000;
        }
    </style>
""", unsafe_allow_html=True)

GITHUB_TOKEN = os.getenv('G_TOKEN')
DATA_FILE = 'contributors.csv'
BY_CONTRIBUTIONS = {
    '> 1': 1,
    '> 100': 100,
    '> 1K': 1000,
    '> 10K': 10000}
RESULTS_TO_DISPLAY = {
    'Top 10': 10,
    'Top 50': 50,
    'Top 100': 100} 

# Streamlit cache to store contributors data
# This will prevent fetching the same data multiple times
# and will cache the results for 1 hour
@st.cache_data(ttl=3600, show_spinner=False)
def get_contributors(repo):
    print(f"Fetching {repo} contributors...")

    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    repo = g.get_repo(repo)
    contributors = repo.get_contributors()
    
    print(f"Writing contributors to {DATA_FILE}...")

    with open(DATA_FILE, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        for contributor in contributors:
            csv_writer.writerow([contributor.login, contributor.contributions])

def display_contributors(by_contributions, results_to_display):
    print(f"Displaying contributors...")

    results_to_display = RESULTS_TO_DISPLAY[results_to_display]
    by_contributions = BY_CONTRIBUTIONS[by_contributions]

    col1, col2, col3, col4, col5 = st.columns(5, gap='small')
    p_container = st.container()
    col_index = 0
    i = 1

    with open(DATA_FILE) as csvfile:
        contributors_list = list(csv.reader(csvfile))
        data = []
        for contributor in contributors_list[:results_to_display]:
            login = contributor[0]
            contributions = contributor[1]

            if int(contributions) < by_contributions:
                continue

            with p_container:
                col = col1 if col_index == 0 else col2 if col_index == 1 else col3 if col_index == 2 else col4 if col_index == 3 else col5

                col.write("<div style='border:1px solid #29b5e8'>", unsafe_allow_html=True)
                contributor_link = f"<a class='published' href='https://github.com/{login}' target='_blank'>{login}</a>"
                contributor_repositories_link = f"<a class='published' href='https://github.com/{login}?tab=repositories' target='_blank'>Repositories</a>"
                contributor_projects_link = f"<a class='published' href='https://github.com/{login}?tab=projects' target='_blank'>Projects</a>"
                contributor_followers_link = f"<a class='published' href='https://github.com/{login}?tab=followers' target='_blank'>Followers</a>"

                col.markdown(f" > {contributor_link}", unsafe_allow_html=True)
                col.markdown(f"<h6>Contributions: {contributions}</h6>", unsafe_allow_html=True)
                col.markdown(f"<h6>{contributor_repositories_link} | {contributor_projects_link} | {contributor_followers_link}</h6>", unsafe_allow_html=True)
                col.write("</div>", unsafe_allow_html=True)
                
                if (i % 5) == 0:
                    col1, col2, col3, col4, col5 = st.columns(5, gap='small')
                    p_container = st.container()
                    col_index = 0
                else:
                    col_index += 1
                i += 1

with st.container():
    st.header(f"GitHub Contributors")
    st.caption(f"App developed by [Dash](https://www.linkedin.com/in/dash-desai/)")
    st.markdown("___")

    col1, col2, col3 = st.columns([3.2,1.5,1.8])
    with col1:
        repo = st.text_input("Enter GitHub repository name. For example: apache/spark", key="search_input")
    with col2:
        by_contributions = st.radio(
            "Filter by contributions greater than",
            key="by_contributions",
            horizontal=True,
            options=BY_CONTRIBUTIONS.keys(),
            index=1
        )
    with col3:
        results_to_display = st.radio(
            "Results to display",
            key="results_to_display",
            horizontal=True,
            options=RESULTS_TO_DISPLAY.keys(),
            index=0
        )

if repo:
    get_contributors(repo)
    display_contributors(by_contributions, results_to_display)
    print(f"Done!")


