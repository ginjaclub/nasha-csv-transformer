# Nasha Smart CSV Transformer - AI Powered

An intelligent CSV transformation tool that uses Claude AI to automatically understand and map your product data to different platform formats.

## Features

- 🤖 **AI-Powered Intelligence**: Automatically understands CSV structure
- 🎯 **Smart Category Detection**: Detects product types from context
- 📊 **Intelligent Data Extraction**: Parses descriptions and structured data
- 🔄 **Multi-Platform Export**: Weedmaps, I Heart Jane, Leafly, Squarespace
- ⚡ **No Manual Mapping**: Works with any column naming convention

## Deployment Options

### Option 1: Deploy to Render (Recommended - FREE)

1. **Create a Render account**: https://render.com (free tier available)

2. **Create a new Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repo (or upload these files to GitHub first)
   - Or use "Deploy from Git" and paste the repo URL

3. **Configure the service**:
   - Name: `nasha-csv-transformer`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Add Environment Variable**:
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key (get from https://console.anthropic.com)

5. **Deploy**: Click "Create Web Service"
   - Your app will be live at: `https://nasha-csv-transformer.onrender.com`

### Option 2: Deploy to Railway

1. **Create Railway account**: https://railway.app

2. **New Project**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repo or upload files

3. **Add Environment Variable**:
   - Go to Variables tab
   - Add `ANTHROPIC_API_KEY` with your API key

4. **Deploy**: Railway auto-deploys
   - Your app will be at: `https://your-app.railway.app`

### Option 3: Deploy to Heroku

1. **Install Heroku CLI**: https://devcenter.heroku.com/articles/heroku-cli

2. **Login and create app**:
   ```bash
   heroku login
   heroku create nasha-csv-transformer
   ```

3. **Set environment variable**:
   ```bash
   heroku config:set ANTHROPIC_API_KEY=your_api_key_here
   ```

4. **Deploy**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

5. **Open app**:
   ```bash
   heroku open
   ```

### Option 4: Run Locally (For Testing)

1. **Install Python 3.8+**: https://python.org

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set API key**:
   ```bash
   # Mac/Linux:
   export ANTHROPIC_API_KEY=your_api_key_here
   
   # Windows:
   set ANTHROPIC_API_KEY=your_api_key_here
   ```

4. **Run the app**:
   ```bash
   python app.py
   ```

5. **Open browser**: http://localhost:5000

## Getting Your Anthropic API Key

1. Go to: https://console.anthropic.com
2. Sign up or log in
3. Go to "API Keys" section
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-...`)
6. Use this key in your deployment environment variables

## How to Use

1. **Upload your master CSV** - Any Nasha product CSV with any column names
2. **AI analyzes** - Claude AI reads your data structure and understands it
3. **Review detection** - See how AI categorized your products
4. **Download** - Click platform buttons to get transformed CSVs

## File Structure

```
nasha-csv-transformer/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Cost

- **Hosting**: FREE on Render/Railway free tier
- **API Calls**: ~$0.01-0.05 per CSV transformation (Anthropic Claude API)
  - Example: 50 products = ~$0.03
  - Monthly estimate: 100 transformations = ~$3

## Support

Issues? Contact the developer or check:
- Anthropic API Docs: https://docs.anthropic.com
- Flask Docs: https://flask.palletsprojects.com
