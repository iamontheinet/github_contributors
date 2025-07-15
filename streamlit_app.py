from github import Auth
from github import Github
import csv
import os
import streamlit as st
from datetime import datetime, timedelta

# Setup web page
st.set_page_config(
     page_title="GitHub Contributors Influence Analyzer",
     layout="wide"
)

st.markdown("""
    <style type="text/css">
        div[data-testid='stImage'] {
            margin: 1em 0px -1em -1px;
            padding: 0px 0px 0px 1.2em;
            font-size: 10px;
            border-left: 5px solid rgb(230, 234, 241);
            # background-color: #249edc;
            height: 100px;
        }
        blockquote {
            margin: -1em 0px 1em -1px;
            padding: 10px 0px 0px 1.2em;
            font-size: 10px;
            border-left: 5px solid rgb(230, 234, 241);
            # background-color: #249edc;
            height: 50px;
        }
        a.name {
            color: #29b5e8;
            text-decoration: none;
            font-size: 20px;
        }
        a.other {
            color: #ffffff;
            text-decoration: none;
            font-style: italic;
            font-size: 15px;
        }
        p {
            color: rgb(129, 164, 182);
        }
        input {
            background-color: #115675 !important;
        }
        .st-b6 {
            color: #000000;
        }
        h6.stats {
            width: 200px;
        }    
    </style>
""", unsafe_allow_html=True)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
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

GIT_AUTH = Auth.Token(GITHUB_TOKEN)
GIT = Github(auth=GIT_AUTH)

# Cache the results for 1 hour
@st.cache_data(ttl=3600, show_spinner=False)
def get_contributors(repo):
    print(f"Fetching {repo} contributors...")

    repo = GIT.get_repo(repo)
    contributors = repo.get_contributors()
    
    print(f"Writing contributors to {DATA_FILE}...")

    with open(DATA_FILE, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        for contributor in contributors:
            csv_writer.writerow([contributor.login, contributor.contributions])

def get_influence_color(score):
    if score >= 400:
        return "#ff4444"  # Red for high influence
    elif score >= 250:
        return "#ff8800"  # Orange for medium-high influence
    elif score >= 150:
        return "#ffaa00"  # Yellow for medium influence
    elif score >= 50:
        return "#88cc00"  # Light green for low-medium influence
    else:
        return "#cccccc"  # Gray for low influence
    
# Cache the results for 1 hour
@st.cache_data(ttl=3600, show_spinner=False)
def calculate_influence_score(repo, contributor, total_contributions):
    print(f"Calculating influence score for {contributor} in {repo}...")

    # Base Contributions: (up to 300 points): Total commits/contributions to the repository
    # Recent Activity: (up to 200 points): Contributions in the last 6 months (shows current engagement)
    # Code Impact: (up to 50 points): Volume of code changes (lines added/deleted)
    # Community Involvement: (up to 100 points): Issues created, pull requests, and discussions
    # Consistency Bonus: (up to 50 points): Ratio of recent to total activity

    repo_obj = GIT.get_repo(repo)

    # Calculate recent activity (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    recent_commits = list(repo_obj.get_commits(author=contributor, since=six_months_ago))
    recent_contributions = len(recent_commits)
    
    # Base score from total contributions
    base_score = min(total_contributions, 1000) * 0.3  # Cap at 300 points
    
    # Recent activity bonus (shows current engagement)
    recent_bonus = min(recent_contributions, 100) * 2  # Up to 200 points

    # Calculate lines of code impact from recent commits
    lines_added = 0
    lines_deleted = 0
    if recent_commits:
        for commit in recent_commits[:20]:  # Limit to avoid rate limiting
            try:
                stats = commit.stats
                lines_added += stats.additions
                lines_deleted += stats.deletions
            except:
                continue

    # Code impact bonus (lines added/deleted)
    code_impact = min((lines_added + lines_deleted) / 100, 50)  # Up to 50 points

    # Check if contributor is a collaborator/maintainer
    is_collaborator = False
    try:
        # Try to check collaborator status - this may fail due to permissions
        is_collaborator = repo_obj.has_in_collaborators(contributor)
    except Exception as e:
        # For public repositories, we can't check collaborator status
        # Use contribution count as a proxy for influence instead
        is_collaborator = total_contributions > 100
        print(f"Using contribution-based estimation for {contributor} (>100 contributions: {is_collaborator}) to assess collaborator status")

    # Collaborator/maintainer bonus (or high contributor bonus if we can't determine status)
    if is_collaborator:
        collaborator_bonus = 100
    elif total_contributions > 100:  # High contributor, likely has influence
        collaborator_bonus = 50  # Partial bonus
    else:
        collaborator_bonus = 0
    
    # Get issue/PR involvement (approximate)
    issue_pr_count = 0
    try:
        # Try to get issues and PRs created by this contributor
        # Use a timeout-like approach by limiting the search
        issues = list(repo_obj.get_issues(creator=contributor, state='all'))[:5]
        prs = list(repo_obj.get_pulls(creator=contributor, state='all'))[:5]
        issue_pr_count = len(issues) + len(prs)
    except Exception as e:
        # If we can't fetch issues/PRs, try to estimate based on activity
        print(f"Using activity-based estimation for {contributor} to calculate number of issues and pull requests opened")
        try:
            # Alternative: estimate based on recent commit activity
            if recent_contributions > 5:
                issue_pr_count = min(recent_contributions // 4, 8)  # More conservative estimate
            elif total_contributions > 50:
                issue_pr_count = min(total_contributions // 20, 5)  # Estimate based on total contributions
            else:
                issue_pr_count = 0
        except:
            issue_pr_count = 0

    # Issue/PR involvement bonus
    involvement_bonus = min(issue_pr_count * 10, 100)  # Up to 100 points
    
    # Activity consistency bonus (recent vs total ratio)
    if total_contributions > 0:
        consistency_bonus = min((recent_contributions / total_contributions) * 50, 50)
    else:
        consistency_bonus = 0
    
    total_score = (base_score + recent_bonus + code_impact + 
                  collaborator_bonus + involvement_bonus + consistency_bonus)

    return [round(total_score, 1), recent_contributions, lines_added, lines_deleted, issue_pr_count]

def display_contributors(repo, by_contributions, results_to_display):
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
                contributor_url = f"https://github.com/{login}"
                contributor_img = f"{'https://avatars.githubusercontent.com/' + login}"
                contributor_link = f"<a class='name' href='{contributor_url}' target='_blank'>{login}</a>"

                col.image(contributor_img, width=100)
                col.markdown(f" > {contributor_link}", unsafe_allow_html=True)
                col.markdown(f"<h6>📊 Contributions: {contributions}</h6>", unsafe_allow_html=True)

                # contributor_repositories_link = f"<a class='other' href='https://github.com/{login}?tab=repositories' target='_blank'>Repositories</a>"
                # contributor_projects_link = f"<a class='other' href='https://github.com/{login}?tab=projects' target='_blank'>Projects</a>"
                # contributor_followers_link = f"<a class='other' href='https://github.com/{login}?tab=followers' target='_blank'>Followers</a>"
                # col.markdown(f"<h6>{contributor_repositories_link} | {contributor_projects_link} | {contributor_followers_link}</h6>", unsafe_allow_html=True)

                if col.button("Calculate Influence Score", key=f"calc_{login}"):
                    influence_score,recent_contributions, lines_added, lines_deleted, issue_pr_count = calculate_influence_score(repo, login, int(contributions))
                    influence_color = get_influence_color(influence_score)
                    col.markdown(f"<h6 class='stats' style='color:{influence_color};'>🎯 Influence Score: {influence_score}</h6>", help="🔴 400+: Highly influential\n🟠 250-399: Very influential\n🟡 150-249: Moderately influential\n🟢 50-149: Growing influence\n⚪ 0-49: Limited influence", unsafe_allow_html=True)
                    col.markdown(f"<h6 class='stats'>🔥 Recent Activity (6mo): {recent_contributions}</h6>", help="Number of contributions in the last 6 months", unsafe_allow_html=True)
                    col.markdown(f"<h6 class='stats'>📝 Code Impact: +{lines_added} -{lines_deleted}</h6>", help="Estimated volume of code changes (lines added/deleted)", unsafe_allow_html=True)
                    col.markdown(f"<h6 class='stats'>💬 Issues/PRs: {issue_pr_count}</h6>", help="Estimated number of issues and pull requests opened based on total contributions", unsafe_allow_html=True)

                col.write("</div>", unsafe_allow_html=True)
                
                if (i % 5) == 0:
                    col1, col2, col3, col4, col5 = st.columns(5, gap='small')
                    p_container = st.container()
                    col_index = 0
                else:
                    col_index += 1
                i += 1

with st.container():
    st.header(f"GitHub Contributors Influence Analyzer")
    st.caption(f"App developed by [Dash](https://www.linkedin.com/in/dash-desai/)")
    st.markdown("___")

    col1, col2, col3 = st.columns([3.2,1.5,1.8])
    with col1:
        repo = st.text_input("Enter GitHub repository name", key="search_input", placeholder="apache/spark", help="Enter the repository name in the format 'owner/repo'.")
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
    display_contributors(repo, by_contributions, results_to_display)
    print(f"Done!")


