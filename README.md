# GitHub Contributors Influence Analyzer

A comprehensive Streamlit application that analyzes GitHub repository contributors and calculates their influence score based on multiple factors.

## Features

### 🎯 Optimized Influence Score Calculation
- **Base Contributions** (up to 300 points): Total commits/contributions to the repository
- **Recent Activity** (up to 200 points): Contributions in the last 6 months (shows current engagement)
- **Code Impact** (up to 50 points): Volume of code changes (lines added/deleted)
- **Community Involvement** (up to 100 points): Issues and pull requests created
- **Consistency Bonus** (up to 50 points): Ratio of recent to total activity

#### Score Interpretation

- 🔴 **400+**: Highly influential (core maintainers, heavy contributors)
- 🟠 **250-399**: Very influential (regular contributors with significant impact)
- 🟡 **150-249**: Moderately influential (consistent contributors)
- 🟢 **50-149**: Growing influence (active participants)
- ⚪ **0-49**: Limited influence (occasional contributors)

## Requirements

- Python 3.7+
- GitHub Personal Access Token
- Internet connection for API access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd github_contributors
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your GitHub token:
```bash
export GITHUB_TOKEN="your_github_token_here"
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

2. Open your browser to `http://localhost:8501`

3. Enter a repository name in the format `owner/repo` (e.g., `apache/spark`)

4. Adjust filters:
   - **Filter by contributions**: Show only contributors with more than X contributions
   - **Results to display**: Limit the number of results shown

## API Rate Limiting

The app uses caching to minimize API calls, but for repositories with many contributors, you may hit GitHub's rate limits. The app includes error handling for such cases.

## Contributing

Feel free to submit issues and enhancement requests!
