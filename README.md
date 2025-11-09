# Rift Metrics

A League of Legends performance analytics platform powered by AI.

## Features
- Player performance analysis
- AI-powered coaching insights
- Champion statistics and matchup analysis
- Advanced performance metrics

## Tech Stack
- **Frontend:** Streamlit
- **AI:** AWS Bedrock (Claude)
- **APIs:** Riot Games API
- **Cloud:** AWS App Runner

## Setup

### Prerequisites
- Python 3.11+
- Riot API Key
- AWS Account with Bedrock access

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/rift-metrics.git
cd rift-metrics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```env
RIOT_API_KEY=your_riot_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0
```

4. Run the app:
```bash
streamlit run main.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `RIOT_API_KEY` | Your Riot Games API key |
| `AWS_ACCESS_KEY_ID` | AWS access key for Bedrock |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_REGION` | AWS region (default: us-west-2) |
| `BEDROCK_MODEL_ID` | Claude model ID |

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Riot Games API
- AWS Bedrock
- Anthropic Claude
