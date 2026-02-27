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
import re

app = Flask(__name__)

# Nasha Product Taxonomy
PRODUCT_TAXONOMY = """
NASHA PRODUCT CATEGORIES & SUBCATEGORIES:

1. HASH
   - Green Unpressed Hash
   - Orange Unpressed Hash
   - Red Pressed Hash
   - Blue Pressed Hash
   - Onyx Live Pressed Hash

2. COLD CURE ROSIN
   - Cold Cure Live Rosin

3. PACKAGED FLOWER
   - 3.5g
   - 7g
   - 14g

4. VAPE CARTS
   - 0.5g All-In-One
   - 1g All-In-One
   - 510 Vape Cart (future)

5. PREROLLS
   - Altitude Infused Hash Prerolls
   - Submerge Infused Hash Prerolls
   - Live Rosin Infused Prerolls

6. 5-PACK PREROLLS
   - 5 Pack Hash-Infused Multipack
   - 5 Pack Live Rosin-Infused Multipack

7. EDIBLES (future)
"""

# Platform category mappings
PLATFORM_MAPPINGS = {
    'weedmaps': {
        'hash': 'Ice Water Hash, Solventless, Concentrates',
        'rosin': 'Rosin, Solventless, Concentrates',
        'flower': 'Flower',
        'vape-aio': 'Disposable, Vape Pens',
        'vape-510': 'Cartridge, Vape Pens',
        'preroll-infused': 'Infused Pre Roll',
        'preroll-regular': 'Flower'
    },
    'leafly': {
        'hash': {'category': 'Concentrates', 'subcategory': 'Hash'},
        'rosin': {'category': 'Concentrates', 'subcategory': 'Rosin'},
        'flower': {'category': 'Cannabis', 'subcategory': 'Flower'},
        'vape': {'category': 'Vaping', 'subcategory': 'Vape pens'},
        'preroll': {'category': 'Cannabis', 'subcategory': 'Pre-rolls'}
    },
    'squarespace': {
        'hash': 'hash-library',
        'rosin': 'rosin-library',
        'flower': 'flower-library',
        'vape': 'vape-library',
        'preroll': 'infused-preroll-library'
    }
}

# HTML Template (same as before)
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
            <p>AI-powered intelligent data mapping • Handles all Nasha product categories</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <h3>🧠 AI-Powered Intelligence:</h3>
                <ul>
                    <li>Automatically understands your CSV structure</li>
                    <li>Detects all Hash, Rosin, Flower, Vape, and Preroll subcategories</li>
                    <li>Extracts LINEAGE, TASTE, FEELING from descriptions</li>
                    <li>Removes FARM info for Weedmaps/Leafly/IHeartJane</li>
                    <li>Keeps FARM info for Squarespace</li>
                    <li>Works with any column naming convention</li>
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
            
            showStatus('Generating ' + platform + ' CSV...', 'info');
            
            try {
                const response = await fetch('/transform', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Download failed');
                }
                
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
    """AI analyzes the uploaded CSV and categorizes all products"""
    try:
        file = request.files['file']
        
        # Read CSV
        content = file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        
        if len(rows) == 0:
            return jsonify({'error': 'No data found in CSV'}), 400
        
        # Get API key
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'ANTHROPIC_API_KEY not set'}), 500
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Analyze ALL products in batches
        all_analysis = []
        batch_size = 20
        
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            
            analysis_prompt = f"""{PRODUCT_TAXONOMY}

Analyze these {len(batch)} products. For EACH product, determine:
1. Main Category: Hash, Rosin, Flower, Vape, Preroll, or 5-Pack Preroll
2. Subcategory: The specific type from the list above
3. Type: Sativa/Indica/Hybrid (from (S)/(I)/(H) markers in name)

Products:
{json.dumps(batch, indent=2)}

Return ONLY a JSON array with one object per product:
[{{"main_category": "...", "subcategory": "...", "type": "..."}}, ...]

NO markdown, NO explanation."""
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            # Parse response
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                batch_analysis = json.loads(json_match.group())
                all_analysis.extend(batch_analysis)
        
        # Count categories
        category_counts = {}
        for item in all_analysis:
            subcategory = item.get('subcategory', 'Unknown')
            category_counts[subcategory] = category_counts.get(subcategory, 0) + 1
        
        return jsonify({
            'total_products': len(rows),
            'categories': category_counts,
            'success': True
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e), 
            'details': traceback.format_exc()
        }), 500

@app.route('/transform', methods=['POST'])
def transform():
    """Transform CSV to platform format using AI"""
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
        
        # Define exact platform column structures
        platform_columns = {
            'weedmaps': [
                'name', 'categories', 'description', 'avatar_image', 'product_id',
                'external_id', 'sku', 'gallery_images', 'featured', 'tags',
                'thc_percentage', 'thc_milligrams', 'cbd_percentage', 'cbd_milligrams',
                'genetics', 'strain', 'items_per_pack', 'msrp', 'weight'
            ],
            'leafly': [
                'Leafly Product ID', 'Name', 'SKU', 'Description', 'Category',
                'Subcategory', 'Strain', 'THC Content', 'THC Unit', 'CBD Content',
                'CBD Unit', 'Country Availability', 'State/Province Availability',
                'External Link URL', 'Image One URL', 'Image Two URL',
                'Image Three URL', 'Image Four URL', 'Image Five URL'
            ],
            'iheartjane': [
                ' ', 'Strain', 'Brand Category',
                'Does this Product Come in Standard Pack Sizes of 0.5g (500mg) or 1g (1000mg)?',
                'Pack Size Next Steps', 'Enter Non-Standard Pack Size Here [g]',
                'Lineage', 'Product Name (Internal Use)', 'Product Description',
                'IMAGE LINK ONLY (PLEASE ATTACH IMAGES TO EMAIL IF YOU DON\'T HAVE A LINK)',
                'Jane Use: Click here when product is added', '', ''
            ],
            'squarespace': [
                'Product ID [Non Editable]', 'Variant ID [Non Editable]',
                'Product Type [Non Editable]', 'Product Page', 'Product URL',
                'Title', 'Description', 'SKU', 'Option Name 1', 'Option Value 1',
                'Option Name 2', 'Option Value 2', 'Option Name 3', 'Option Value 3',
                'Option Name 4', 'Option Value 4', 'Option Name 5', 'Option Value 5',
                'Option Name 6', 'Option Value 6', 'Price', 'Sale Price', 'On Sale',
                'Stock', 'Categories', 'Tags', 'Weight', 'Length', 'Width',
                'Height', 'Visible', 'Hosted Image URLs'
            ]
        }
        
        # Process in batches
        transformed_rows = []
        batch_size = 10
        
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            
            transform_prompt = f"""{PRODUCT_TAXONOMY}

Transform these {len(batch)} products to {platform} format.

EXACT COLUMNS REQUIRED (in this order):
{json.dumps(platform_columns[platform], indent=2)}

CRITICAL RULES:
1. Extract (S)=Sativa, (I)=Indica, (H)=Hybrid from product name
2. Parse descriptions to extract and organize:
   - LINEAGE (genetic cross)
   - TASTE (flavor profile)
   - FEELING (effects)
   - FARM (farm name)
   - PLACE GROWN (location)
   - Full marketing description (paragraph about the strain/product)
3. For Weedmaps/Leafly/I Heart Jane: Description = LINEAGE + TASTE + FEELING + Full marketing description (REMOVE only FARM and PLACE GROWN lines)
   Example: Keep "LINEAGE: OG x Skunk #1\\nTASTE: Earthy pine, citrus\\nFEELING: Relaxed, focused\\n\\nOGxSkunk1 is a Indica hybrid cannabis strain..." but remove "FARM: Clear Water Farms" and "PLACE GROWN: Humboldt, CA"
4. For Squarespace: Description = LINEAGE + TASTE + FEELING + FARM + PLACE GROWN + Full marketing description (KEEP EVERYTHING)
5. Clean strain name = remove product type keywords, keep only strain name
   - For Squarespace Title: Extract ONLY the strain name, remove ALL product type info, weight, farm name
   - Examples: "Jelly Donutz #117 Green Unpressed Hash (S)" → Title: "Jelly Donutz #117"
              "Banana OG x GMO Cold Cure Live Rosin" → Title: "Banana OG x GMO"
              "Moroccan Peaches Live Rosin All-In-One Vape 1g" → Title: "Moroccan Peaches"
6. WEIGHT EXTRACTION RULES (CRITICAL):
   - If "5 Pack" or "5-Pack" in name → weight is ALWAYS "2.5g" (total for 5-pack)
   - Otherwise extract weight from name (0.5g, 1g, 3.5g, 7g, 14g, etc.)
7. Map main category to platform categories using these mappings:
   {json.dumps(PLATFORM_MAPPINGS, indent=2)}
8. FOR SQUARESPACE ONLY - Generate Product URL:
   - Take clean strain name (e.g., "Acai Mints")
   - Add farm name if available (e.g., "Whitethorn Valley")
   - Convert to lowercase, replace spaces with hyphens, remove special characters
   - Example: "Acai Mints" + "Whitethorn Valley" → "acai-mints-whitethorn-valley"
   - Example: "Banana OG x GMO" + "Clear Water Farms" → "banana-og-x-gmo-clear-water-farms"
   - For prerolls with batch numbers: "submerge-batch-28" or "altitude-batch-20"

FIELD MAPPING INSTRUCTIONS FOR {platform.upper()}:

{"WEEDMAPS:" if platform == 'weedmaps' else ""}
{"- name: Full product name" if platform == 'weedmaps' else ""}
{"- categories: Mapped category (e.g., 'Ice Water Hash, Solventless, Concentrates')" if platform == 'weedmaps' else ""}
{"- description: Description without FARM/PLACE" if platform == 'weedmaps' else ""}
{"- avatar_image: Photo link" if platform == 'weedmaps' else ""}
{"- product_id: (leave empty)" if platform == 'weedmaps' else ""}
{"- external_id: Batch number" if platform == 'weedmaps' else ""}
{"- sku: (leave empty)" if platform == 'weedmaps' else ""}
{"- gallery_images: Photo link" if platform == 'weedmaps' else ""}
{"- featured: FALSE" if platform == 'weedmaps' else ""}
{"- tags: From FEELING field (comma-separated)" if platform == 'weedmaps' else ""}
{"- thc_percentage: THC value without %" if platform == 'weedmaps' else ""}
{"- thc_milligrams: (leave empty)" if platform == 'weedmaps' else ""}
{"- cbd_percentage: (leave empty)" if platform == 'weedmaps' else ""}
{"- cbd_milligrams: (leave empty)" if platform == 'weedmaps' else ""}
{"- genetics: Sativa/Indica/Hybrid" if platform == 'weedmaps' else ""}
{"- strain: Clean strain name" if platform == 'weedmaps' else ""}
{"- items_per_pack: 5 for 5-packs, 1 otherwise" if platform == 'weedmaps' else ""}
{"- msrp: (leave empty)" if platform == 'weedmaps' else ""}
{"- weight: Extracted weight (0.5g, 1g, 2.5g, 3.5g, etc.)" if platform == 'weedmaps' else ""}

{"LEAFLY:" if platform == 'leafly' else ""}
{"- All 19 columns must be present" if platform == 'leafly' else ""}
{"- Empty fields: Leafly Product ID, CBD Content, CBD Unit, External Link URL, Image Two/Three/Four/Five URL" if platform == 'leafly' else ""}
{"- THC Unit: PERCENTAGE" if platform == 'leafly' else ""}
{"- Country Availability: US" if platform == 'leafly' else ""}
{"- State/Province Availability: CA" if platform == 'leafly' else ""}

{"I HEART JANE:" if platform == 'iheartjane' else ""}
{"- First column ' ': Nasha" if platform == 'iheartjane' else ""}
{"- Product Name (Internal Use): Nasha | Strain | Category | Weight | Type" if platform == 'iheartjane' else ""}
{"- Standard Pack Sizes: YES for 0.5g/1g, NO otherwise" if platform == 'iheartjane' else ""}
{"- Last two columns '': leave empty" if platform == 'iheartjane' else ""}

{"SQUARESPACE:" if platform == 'squarespace' else ""}
{"- All 32 columns must be present" if platform == 'squarespace' else ""}
{"- Product Type [Non Editable]: PHYSICAL" if platform == 'squarespace' else ""}
{"- Product Page: Based on category (hash-library, rosin-library, flower-library, vape-library, infused-preroll-library)" if platform == 'squarespace' else ""}
{"- Product URL: Generate as: strain-name-farm-name (lowercase, hyphens, URL-safe). Example: 'Acai Mints' + 'Whitethorn Valley' = 'acai-mints-whitethorn-valley'" if platform == 'squarespace' else ""}
{"- Title: Clean strain name ONLY (no product type, no farm). Example: 'Acai Mints', 'Banana OG x GMO'" if platform == 'squarespace' else ""}
{"- Description: HTML format with <p> and <br> tags. Include FARM and PLACE GROWN. Format: <p class=\"\">LINEAGE: ...<br>TASTE: ...<br>FEELING: ...<br>FARM: ...<br>PLACE GROWN: ...</p><p class=\"\">Full marketing paragraph...</p>" if platform == 'squarespace' else ""}
{"- Categories: / + first letter of strain name (lowercase). Example: 'Acai Mints' = '/a', 'Banana OG' = '/b'. Use '/category' for names starting with numbers/symbols" if platform == 'squarespace' else ""}
{"- Tags: Farm name only" if platform == 'squarespace' else ""}
{"- Price/Sale Price: 0.00" if platform == 'squarespace' else ""}
{"- On Sale: No" if platform == 'squarespace' else ""}
{"- Stock: Unlimited" if platform == 'squarespace' else ""}
{"- Visible: Yes" if platform == 'squarespace' else ""}
{"- Weight/Length/Width/Height: 0.0" if platform == 'squarespace' else ""}
{"- All empty fields: leave as empty string" if platform == 'squarespace' else ""}

Products to transform:
{json.dumps(batch, indent=2)}

Return ONLY a JSON array of objects. Each object MUST have ALL {len(platform_columns[platform])} columns in the exact order listed above. Use empty string "" for empty fields. NO markdown, NO explanation."""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=5000,
                messages=[{"role": "user", "content": transform_prompt}]
            )
            
            # Parse response
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                batch_transformed = json.loads(json_match.group())
                
                # Ensure all required columns are present for each row
                for row in batch_transformed:
                    for col in platform_columns[platform]:
                        if col not in row:
                            row[col] = ''  # Add missing column with empty value
                    
                    # Ensure columns are in correct order
                    ordered_row = {col: row.get(col, '') for col in platform_columns[platform]}
                    transformed_rows.append(ordered_row)
            else:
                # Try parsing whole response
                batch_transformed = json.loads(response_text)
                if isinstance(batch_transformed, list):
                    transformed_rows.extend(batch_transformed)
                else:
                    transformed_rows.append(batch_transformed)
        
        # Generate CSV with exact column order
        if not transformed_rows:
            return jsonify({'error': 'No data transformed'}), 500
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=platform_columns[platform])
        writer.writeheader()
        writer.writerows(transformed_rows)
        
        # Return file
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'Nasha_{platform}.csv'
        )
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'details': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
