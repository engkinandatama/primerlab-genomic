"""
HTML Report Generator (v0.1.4)

Generates standalone HTML reports with embedded CSS.
No external dependencies required for viewing.
"""

from typing import Dict, Any, Optional
from primerlab.core.models import WorkflowResult


def generate_html_report(result: WorkflowResult) -> str:
    """
    Generate a standalone HTML report.
    
    Args:
        result: WorkflowResult from workflow execution
        
    Returns:
        Complete HTML string
    """
    # Header section
    workflow = result.workflow.upper()
    timestamp = result.metadata.timestamp if result.metadata else "N/A"
    version = result.metadata.version if result.metadata else "N/A"
    
    # Quality score
    quality_html = ""
    if result.qc and result.qc.quality_score is not None:
        score = result.qc.quality_score
        category = result.qc.quality_category or ""
        emoji = result.qc.quality_category_emoji or ""
        
        # Color based on score
        if score >= 85:
            color = "#28a745"
        elif score >= 70:
            color = "#17a2b8"
        elif score >= 50:
            color = "#ffc107"
        else:
            color = "#dc3545"
        
        quality_html = f'''
        <div class="quality-score" style="border-left-color: {color};">
            <div class="score-value" style="color: {color};">{score}/100</div>
            <div class="score-category">{emoji} {category}</div>
        </div>
        '''
    
    # Primers table
    primers_html = ""
    if result.primers:
        rows = []
        for name, primer in result.primers.items():
            tm_class = "good" if 58 <= primer.tm <= 62 else "warn"
            gc_class = "good" if 40 <= primer.gc <= 60 else "warn"
            
            hairpin_val = f"{primer.hairpin_dg:.2f}" if primer.hairpin_dg else "N/A"
            rows.append(f'''
                <tr>
                    <td><strong>{primer.id}</strong></td>
                    <td class="sequence"><code>{primer.sequence}</code></td>
                    <td>{primer.length}</td>
                    <td class="{tm_class}">{primer.tm:.1f}°C</td>
                    <td class="{gc_class}">{primer.gc:.1f}%</td>
                    <td>{hairpin_val}</td>
                </tr>
            ''')
        
        primers_html = f'''
        <table class="primers-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Sequence</th>
                    <th>Length</th>
                    <th>Tm</th>
                    <th>GC%</th>
                    <th>Hairpin ΔG</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        '''
    
    # QC Summary
    qc_html = ""
    if result.qc:
        qc = result.qc
        qc_html = f'''
        <div class="qc-summary">
            <h3>QC Summary</h3>
            <table class="qc-table">
                <tr>
                    <td>Tm Difference</td>
                    <td>{qc.tm_diff:.2f}°C</td>
                    <td>{'✅' if qc.tm_balance_ok else '⚠️'}</td>
                </tr>
                <tr>
                    <td>Hairpin ΔG</td>
                    <td>{qc.hairpin_dg:.2f} kcal/mol</td>
                    <td>{'✅' if qc.hairpin_ok else '⚠️'}</td>
                </tr>
                <tr>
                    <td>Homodimer ΔG</td>
                    <td>{qc.homodimer_dg:.2f} kcal/mol</td>
                    <td>{'✅' if qc.homodimer_ok else '⚠️'}</td>
                </tr>
            </table>
        </div>
        '''
    
    # Rationale section
    rationale_html = ""
    if hasattr(result, 'rationale') and result.rationale:
        r = result.rationale
        selection_reasons = "".join([f"<li>{reason}</li>" for reason in r.get("selection_reasons", [])])
        rejection_items = "".join([
            f"<li>{item['count']} failed: {item['reason']}</li>" 
            for item in r.get("rejection_summary", [])[:5]
        ])
        
        rationale_html = f'''
        <div class="rationale">
            <h3>Why This Primer?</h3>
            <p><strong>Selected as Rank #{r.get("rank", 1)}</strong> from {r.get("total_candidates", 0)} candidates</p>
            <p>({r.get("candidates_passed_qc", 0)} passed all QC checks)</p>
            
            <h4>Selection Reasons:</h4>
            <ul>{selection_reasons}</ul>
            
            <h4>Rejected Candidates:</h4>
            <ul>{rejection_items}</ul>
        </div>
        '''
    
    # Amplicon info
    amplicon_html = ""
    if result.amplicons:
        amp = result.amplicons[0]
        amplicon_html = f'''
        <div class="amplicon-info">
            <h3>Amplicon Details</h3>
            <p><strong>Size:</strong> {amp.length} bp</p>
            <p><strong>Position:</strong> {amp.start} - {amp.end}</p>
        </div>
        '''
    
    # Build complete HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrimerLab Report - {workflow}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .header .meta {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        .quality-score {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .score-value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        .score-category {{
            font-size: 1.2em;
            color: #666;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2, h3 {{
            color: #333;
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .sequence code {{
            background: #f1f3f4;
            padding: 4px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        .good {{
            color: #28a745;
            font-weight: 600;
        }}
        .warn {{
            color: #ffc107;
            font-weight: 600;
        }}
        .rationale, .qc-summary, .amplicon-info {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        ul {{
            margin-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        .footer {{
            text-align: center;
            color: #999;
            font-size: 0.8em;
            margin-top: 30px;
        }}
        .copy-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        .copy-btn:hover {{
            background: #5a6fd6;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧬 PrimerLab Report: {workflow}</h1>
        <div class="meta">
            <p>Generated: {timestamp}</p>
            <p>Version: {version}</p>
        </div>
    </div>
    
    {quality_html}
    
    <div class="card">
        <h2>Best Primer Set</h2>
        {primers_html}
    </div>
    
    {amplicon_html}
    
    {qc_html}
    
    {rationale_html}
    
    <div class="footer">
        <p>Generated by PrimerLab v{version}</p>
    </div>
    
    <script>
        // Copy to clipboard functionality
        function copySequence(seq) {{
            navigator.clipboard.writeText(seq).then(() => {{
                alert('Sequence copied to clipboard!');
            }});
        }}
    </script>
</body>
</html>'''
    
    return html
