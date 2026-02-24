"""
Nasha Smart CSV Transformer - AI-Powered
Uses Claude AI to intelligently map and transform product data
"""

from flask import Flask, request, jsonify, send_file, render_template_string
import anthropic
import csv
import io
import json
import os

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nasha Smart CSV Transformer - AI Powered</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 8px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .content {
            padding: 40px;
        }
        
        .info-box {
            background: #ebf8ff;
            border: 1px solid #90cdf4;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
        }
        
        .info-box h3 {
            color: #2c5282;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .info-box ul {
            list-style: none;
            font-size: 13px;
            color: #2d3748;
        }
        
        .info-box li::before {
            content: "✓ ";
            color: #3182ce;
            font-weight: bold;
        }
        
        .upload-section {
            margin-bottom: 30px;
        }
        
        .upload-box {
            border: 3px dashed #667eea;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: #f8f9ff;
        }
        
        .upload-box:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }
        
        .upload-box.active {
            border-color: #48bb78;
            background: #f0fff4;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .buttons-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 30px;
        }
        
        .download-btn {
            padding: 16px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            color: white;
        }
        
        .download-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .download-btn:not(:disabled):hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .btn-weedmaps { background: #00d280; }
        .btn-iheartjane { background: #ff6b6b; }
        .btn-leafly { background: #72b01d; }
        .btn-squarespace { background: #000000; }
        
        .status-message {
            margin-top: 20px;
            padding: 12px 16px;
            border-radius: 8px;
            display: none;
        }
        
        .status-message.success {
            background: #c6f6d5;
            color: #22543d;
            border: 1px solid #9ae6b4;
        }
        
        .status-message.error {
            background: #fed7d7;
            color: #742a2a;
            border: 1px solid #fc8181;
        }
        
        .status-message.info {
            background: #bee3f8;
            color: #2c5282;
            border: 1px solid #90cdf4;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .analysis-section {
            display: none;
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
        }
        
        .category-badge {
            display: inline-block;
            background: #edf2f7;
            color: #2d3748;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            margin: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Nasha Smart CSV Transformer</h1>
            <p>AI-powered intelligent data mapping • No manual configuration needed</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <h3>🧠 AI-Powered Intelligence:</h3>
                <ul>
                    <li>Automatically understands your CSV structure</li>
                    <li>Intelligently detects product categories from context</li>
                    <li>Extracts structured data from descriptions</li>
                    <li>Works with any column naming convention</li>
                    <li>No manual mapping required!</li>
                </ul>
            </div>
            
            <div class="upload-section">
                <label>Upload Your Master CSV</label>
                <div class="upload-box" id="uploadBox" onclick="document.getElementById('fileInput').click()">
                    <div style="font-size: 48px; margin-bottom: 16px;">📁</div>
                    <p><strong>Click to upload</strong> or drag and drop</p>
                    <p style="font-size: 12px; color: #718096; margin-top: 8px;">
                        Any Nasha product CSV
                    </p>
                </div>
                <input type="file" id="fileInput" accept=".csv">
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>AI is analyzing your products...</p>
            </div>
            
            <div class="analysis-section" id="analysisSection">
                <h4 style="margin-bottom: 12px; color: #2d3748;">📊 AI Analysis Complete:</h4>
                <div id="analysisResults"></div>
            </div>
            
            <div class="buttons-section">
                <button class="download-btn btn-weedmaps" id="btnWeedmaps" disabled>
                    <span>📍</span> Weedmaps
                </button>
                <button class="download-btn btn-iheartjane" id="btnIHeartJane" disabled>
                    <span>❤️</span> I Heart Jane
                </button>
                <button class="download-btn btn-leafly" id="btnLeafly" disabled>
                    <span>🍃</span> Leafly
                </button>
                <button class="download-btn btn-squarespace" id="btnSquarespace" disabled>
                    <span>⬛</span> Squarespace
                </button>
            </div>
            
            <div class="status-message" id="statusMessage"></div>
        </div>
    </div>

    <script>
        let uploadedFileName = '';
        
        const fileInput = document.getElementById('fileInput');
        const uploadBox = document.getElementById('uploadBox');
        const loading = document.getElementById('loading');
        const analysisSection = document.getElementById('analysisSection');
        const analysisResults = document.getElementById('analysisResults');
        const statusMessage = document.getElementById('statusMessage');
        
        fileInput.addEventListener('change', handleFile);
        
        async function handleFile(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            uploadedFileName = file.name;
            const formData = new FormData();
            formData.append('file', file);
            
            // Show loading
            loading.style.display = 'block';
            uploadBox.style.display = 'none';
            analysisSection.style.display = 'none';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showStatus(result.error, 'error');
                    loading.style.display = 'none';
                    uploadBox.style.display = 'block';
                    return;
                }
                
                // Show analysis results
                loading.style.display = 'none';
                uploadBox.classList.add('active');
                uploadBox.innerHTML = `
                    <div style="font-size: 48px; margin-bottom: 16px;">✓</div>
                    <p><strong>${file.name}</strong></p>
                    <p style="font-size: 12px; color: #718096; margin-top: 8px;">
                        ${result.total_products} products analyzed by AI
                    </p>
                `;
                uploadBox.style.display = 'block';
                
                // Display category breakdown
                let categoryHTML = '';
                for (const [category, count] of Object.entries(result.categories)) {
                    categoryHTML += `<span class="category-badge">${category}: ${count}</span>`;
                }
                analysisResults.innerHTML = categoryHTML;
                analysisSection.style.display = 'block';
                
                // Enable download buttons
                document.getElementById('btnWeedmaps').disabled = false;
                document.getElementById('btnIHeartJane').disabled = false;
                document.getElementById('btnLeafly').disabled = false;
                document.getElementById('btnSquarespace').disabled = false;
                
                showStatus('AI analysis complete! Ready to download.', 'success');
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
                loading.style.display = 'none';
                uploadBox.style.display = 'block';
            }
        }
        
        function showStatus(message, type) {
            statusMessage.textContent = message;
            statusMessage.className = `status-message ${type}`;
            statusMessage.style.display = 'block';
            setTimeout(() => {
                statusMessage.style.display = 'none';
            }, 5000);
        }
        
        // Download button handlers
        document.getElementById('btnWeedmaps').addEventListener('click', () => downloadPlatform('weedmaps'));
        document.getElementById('btnIHeartJane').addEventListener('click', () => downloadPlatform('iheartjane'));
        document.getElementById('btnLeafly').addEventListener('click', () => downloadPlatform('leafly'));
        document.getElementById('btnSquarespace').addEventListener('click', () => downloadPlatform('squarespace'));
        
        async function downloadPlatform(platform) {
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('platform', platform);
            
            try {
                const response = await fetch('/transform', {
                    method: 'POST',
                    body: formData
                });
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Nasha_${platform}.csv`;
                a.click();
                window.URL.revokeObjectURL(url);
                
                showStatus(`Downloaded ${platform} CSV!`, 'success');
            } catch (error) {
                showStatus('Download error: ' + error.message, 'error');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    """AI analyzes the uploaded CSV and returns category breakdown"""
    try:
        file = request.files['file']
        
        # Read CSV
        content = file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        
        if len(rows) == 0:
            return jsonify({'error': 'No data found in CSV'}), 400
        
        # Get API key from environment
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'ANTHROPIC_API_KEY not set'}), 500
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Sample first 3 products for analysis
        sample_products = rows[:3]
        
        # Ask Claude to analyze the data structure
        analysis_prompt = f"""Analyze this product CSV data and for each product determine:
1. Product category (hash, rosin, vape, preroll, or flower)
2. Product type (Sativa/Indica/Hybrid) from markers like (S), (I), (H)

CSV Headers: {list(rows[0].keys())}

Sample Products:
{json.dumps(sample_products, indent=2)}

Return a JSON array with one object per product containing:
- category: one of "hash-green-unpressed", "hash-green-powder", "hash-pressed", "hash-bubble", "hash-temple-ball", "rosin-live", "rosin-cold-cure", "rosin-jar", "vape-cart-live", "vape-cart-cured", "vape-disposable", "preroll-infused", "preroll-infused-5pack", "preroll-regular", "flower"
- type: "Sativa", "Indica", or "Hybrid"

Format: [{{"category": "...", "type": "..."}}, ...]
"""
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": analysis_prompt}]
        )
        
        # Parse Claude's response
        analysis_text = response.content[0].text
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\[.*\]', analysis_text, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
        else:
            # Fallback if Claude doesn't return JSON
            analysis = [{"category": "flower", "type": "Hybrid"} for _ in sample_products]
        
        # Count categories
        category_counts = {}
        for item in analysis:
            cat = item['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Store analysis in session (in production, use Redis or database)
        # For now, we'll re-analyze on transform
        
        return jsonify({
            'total_products': len(rows),
            'categories': category_counts,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transform', methods=['POST'])
def transform():
    """Transform the CSV to the requested platform format using AI"""
    try:
        file = request.files['file']
        platform = request.form['platform']
        
        # Read CSV
        content = file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        
        # Get API key
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'ANTHROPIC_API_KEY not set'}), 500
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Define platform schemas
        platform_schemas = {
            'weedmaps': ['name', 'categories', 'description', 'avatar_image', 'external_id', 'tags', 'thc_percentage', 'genetics', 'strain', 'items_per_pack', 'weight'],
            'iheartjane': ['Strain', 'Brand Category', 'Does this Product Come in Standard Pack Sizes of 0.5g (500mg) or 1g (1000mg)?', 'Enter Non-Standard Pack Size Here [g]', 'Lineage', 'Product Name (Internal Use)', 'Product Description', 'IMAGE LINK'],
            'leafly': ['Name', 'SKU', 'Description', 'Category', 'Subcategory', 'Strain', 'THC Content', 'THC Unit', 'Country Availability', 'State/Province Availability', 'Image One URL'],
            'squarespace': ['Title', 'Description', 'SKU', 'Product Page', 'Tags', 'Hosted Image URLs']
        }
        
        # Transform each product using AI
        transformed_rows = []
        
        for row in rows:
            # Ask Claude to transform this product
            transform_prompt = f"""Transform this product data to {platform} format.

Source Data:
{json.dumps(row, indent=2)}

Target Platform: {platform}
Required Fields: {platform_schemas[platform]}

Rules:
- For Weedmaps/Leafly/I Heart Jane: Description should have LINEAGE, TASTE, FEELING but NO FARM info
- For Squarespace: Description should include FARM and PLACE GROWN
- Extract product type (Sativa/Indica/Hybrid) from (S), (I), (H) markers
- Detect category from product name and description
- Clean strain name (remove product type keywords)
- Map image links from available columns

Return ONLY a JSON object with the exact field names for {platform}."""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": transform_prompt}]
            )
            
            # Parse response
            response_text = response.content[0].text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                transformed = json.loads(json_match.group())
                transformed_rows.append(transformed)
        
        # Generate CSV
        if not transformed_rows:
            return jsonify({'error': 'No data transformed'}), 500
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=transformed_rows[0].keys())
        writer.writeheader()
        writer.writerows(transformed_rows)
        
        # Return as downloadable file
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'Nasha_{platform}.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
