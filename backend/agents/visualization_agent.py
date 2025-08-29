#!/usr/bin/env python3
"""
GovHack 2025: Visualization Agent
Generates dynamic dashboards from multi-agent pipeline data using A2A protocol
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

# Add the backend directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class VisualizationAgent:
    def __init__(self, agent_id="visualization_agent"):
        self.agent_id = agent_id
        self.version = "1.0"
        self.data_dir = Path("data")
        self.reports_dir = self.data_dir / "reports"
        self.verified_dir = self.data_dir / "verified"
        self.threats_dir = self.data_dir / "threats"
        self.output_dir = Path("frontend")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"🎨 {self.agent_id} v{self.version} initialized")
        
    def collect_pipeline_data(self):
        """Collect data from all pipeline reports and datasets"""
        try:
            pipeline_data = {
                'reports': {},
                'datasets': {},
                'stats': {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Load JSON reports
            report_files = [
                'critic_report.json',
                'sorter_report.json', 
                'pipeline_report.json'
            ]
            
            for report_file in report_files:
                report_path = self.reports_dir / report_file
                if report_path.exists():
                    with open(report_path, 'r') as f:
                        pipeline_data['reports'][report_file.replace('.json', '')] = json.load(f)
                    print(f"📊 Loaded {report_file}")
                else:
                    print(f"⚠️ Report not found: {report_file}")
            
            # Load verified datasets
            verified_files = [
                'government_contacts.csv',
                'hospital_contacts.csv', 
                'charity_contacts.csv',
                'all_safe_contacts.csv',
                'high_priority_contacts.csv'
            ]
            
            for csv_file in verified_files:
                csv_path = self.verified_dir / csv_file
                if csv_path.exists():
                    df = pd.read_csv(csv_path)
                    pipeline_data['datasets'][csv_file.replace('.csv', '')] = {
                        'count': len(df),
                        'columns': list(df.columns),
                        'sample': df.head(3).to_dict('records') if not df.empty else []
                    }
                    print(f"📋 Loaded {csv_file} ({len(df)} records)")
                    
            # Load threat data
            threats_path = self.threats_dir / 'threat_contacts.csv'
            if threats_path.exists():
                df = pd.read_csv(threats_path)
                pipeline_data['datasets']['threats'] = {
                    'count': len(df),
                    'columns': list(df.columns),
                    'sample': df.head(3).to_dict('records') if not df.empty else []
                }
                print(f"🚨 Loaded threat_contacts.csv ({len(df)} records)")
                
            # Calculate live statistics
            self._calculate_live_stats(pipeline_data)
            
            return pipeline_data
            
        except Exception as e:
            print(f"❌ Error collecting pipeline data: {str(e)}")
            return None
    
    def _calculate_live_stats(self, pipeline_data):
        """Calculate real-time statistics from live data"""
        stats = {}
        
        # Get data from critic report if available
        if 'critic' in pipeline_data['reports']:
            critic_data = pipeline_data['reports']['critic']
            stats.update({
                'total_records': critic_data.get('dataset_info', {}).get('total_records', 0),
                'quality_score': critic_data.get('quality_assessment', {}).get('overall_quality_score', 0),
                'quality_grade': critic_data.get('quality_assessment', {}).get('quality_grade', 'N/A'),
                'phone_validation_rate': critic_data.get('validation_results', {}).get('phone_validation', {}).get('format_compliance_rate', 0),
                'email_validation_rate': critic_data.get('validation_results', {}).get('email_validation', {}).get('format_compliance_rate', 0),
                'website_validation_rate': critic_data.get('validation_results', {}).get('website_validation', {}).get('format_compliance_rate', 0)
            })
        
        # Get data from sorter report if available  
        if 'sorter' in pipeline_data['reports']:
            sorter_data = pipeline_data['reports']['sorter']
            stats.update({
                'safe_contacts': sorter_data.get('quality_metrics', {}).get('safe_contacts', 0),
                'threat_indicators': sorter_data.get('quality_metrics', {}).get('threat_indicators', 0),
                'safety_rate': sorter_data.get('quality_metrics', {}).get('safety_rate', 0),
                'organization_breakdown': sorter_data.get('categorization_results', {}).get('by_organization_type', {}),
                'contact_type_breakdown': sorter_data.get('categorization_results', {}).get('by_contact_type', {}),
                'geographic_breakdown': sorter_data.get('categorization_results', {}).get('by_geographic_region', {})
            })
            
        # Calculate additional metrics from datasets
        total_verified = 0
        for dataset_name, dataset_info in pipeline_data['datasets'].items():
            if 'safe' in dataset_name or dataset_name in ['government_contacts', 'hospital_contacts', 'charity_contacts']:
                total_verified += dataset_info['count']
                
        stats['total_verified_contacts'] = total_verified
        
        pipeline_data['stats'] = stats
        print(f"📈 Calculated live statistics: {len(stats)} metrics")
    
    def generate_dynamic_dashboard(self, pipeline_data):
        """Generate dynamic HTML dashboard with live data"""
        if not pipeline_data:
            print("❌ No pipeline data available for dashboard generation")
            return False
            
        try:
            # Extract key statistics
            stats = pipeline_data['stats']
            
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GovHack 2025: Anti-Scam Data Pipeline Dashboard - Live</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f0f23 100%);
            background-attachment: fixed;
            min-height: 100vh;
            padding: 20px;
            color: #e2e8f0;
            animation: gradientShift 20s ease infinite;
        }}
        
        @keyframes gradientShift {{
            0%, 100% {{ background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f0f23 100%); }}
            25% {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 25%, #0f1419 50%, #1a1a2e 100%); }}
            50% {{ background: linear-gradient(135deg, #16213e 0%, #0f1419 25%, #1a1a2e 50%, #16213e 100%); }}
            75% {{ background: linear-gradient(135deg, #0f1419 0%, #0f0f23 25%, #1a1a2e 50%, #0f1419 100%); }}
        }}
        
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(15, 23, 42, 0.95);
            border-radius: 24px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.4), inset 0 1px 0 rgba(148, 163, 184, 0.1);
            overflow: hidden;
            -webkit-backdrop-filter: blur(20px);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(148, 163, 184, 0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 25%, #6366f1 50%, #8b5cf6 75%, #a855f7 100%);
            color: white;
            padding: 48px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::after {{
            content: '🔴 LIVE';
            position: absolute;
            top: 20px;
            right: 30px;
            background: #ef4444;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 12px;
            font-weight: 800;
            letter-spacing: -0.025em;
            position: relative;
            z-index: 2;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 500;
            letter-spacing: 0.025em;
            position: relative;
            z-index: 2;
        }}
        
        .last-updated {{
            text-align: center;
            padding: 16px;
            background: rgba(30, 41, 59, 0.3);
            color: #94a3b8;
            font-size: 0.875rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }}
        
        .main-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 24px;
            padding: 48px 40px;
            background: rgba(30, 41, 59, 0.5);
        }}
        
        .stat-card {{
            background: rgba(30, 41, 59, 0.8);
            border-radius: 16px;
            padding: 32px 24px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2), 0 4px 10px rgba(0,0,0,0.1);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 1px solid rgba(148, 163, 184, 0.1);
            -webkit-backdrop-filter: blur(12px);
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3), 0 8px 16px rgba(0,0,0,0.15);
            border-color: rgba(148, 163, 184, 0.2);
        }}
        
        .stat-number {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.75rem;
            font-weight: 700;
            margin-bottom: 8px;
            position: relative;
            z-index: 2;
            letter-spacing: -0.02em;
        }}
        
        .stat-label {{
            color: #cbd5e1;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 600;
            position: relative;
            z-index: 2;
        }}
        
        .safe {{ 
            background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .threat {{ 
            background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .total {{ 
            background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .grade {{ 
            background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .success {{ 
            background: linear-gradient(135deg, #06b6d4 0%, #67e8f9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .footer {{
            background: rgba(15, 23, 42, 0.95);
            color: #e2e8f0;
            padding: 32px 40px;
            text-align: center;
            border-top: 1px solid rgba(148, 163, 184, 0.1);
        }}
        
        .agent-info {{
            margin-top: 16px;
            color: #94a3b8;
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <div class="dashboard" role="main" aria-label="Live Anti-Scam Data Pipeline Dashboard">
        <header class="header">
            <h1 id="dashboard-title">🛡️ Anti-Scam Data Pipeline</h1>
            <p id="dashboard-subtitle">GovHack 2025 • Multi-Agent AI System • Real-time Government Data Verification</p>
        </header>
        
        <div class="last-updated">
            📡 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • Generated by Visualization Agent v{self.version}
        </div>
        
        <section class="main-stats" role="region" aria-labelledby="stats-heading">
            <h2 id="stats-heading" class="sr-only">Live Performance Statistics</h2>
            <div class="stat-card" role="article" aria-labelledby="total-contacts">
                <div class="stat-number total" aria-label="{stats.get('total_records', 0)} total contacts">{stats.get('total_records', 0)}</div>
                <div class="stat-label" id="total-contacts">Total Contacts</div>
            </div>
            <div class="stat-card" role="article" aria-labelledby="safe-contacts">
                <div class="stat-number safe" aria-label="{stats.get('safe_contacts', 0)} safe contacts">{stats.get('safe_contacts', 0)}</div>
                <div class="stat-label" id="safe-contacts">Safe Contacts</div>
            </div>
            <div class="stat-card" role="article" aria-labelledby="threat-indicators">
                <div class="stat-number threat" aria-label="{stats.get('threat_indicators', 0)} threat indicators">{stats.get('threat_indicators', 0)}</div>
                <div class="stat-label" id="threat-indicators">Threat Indicators</div>
            </div>
            <div class="stat-card" role="article" aria-labelledby="quality-grade">
                <div class="stat-number grade" aria-label="Quality grade {stats.get('quality_grade', 'N/A')}">{stats.get('quality_grade', 'N/A')}</div>
                <div class="stat-label" id="quality-grade">Quality Grade</div>
            </div>
            <div class="stat-card" role="article" aria-labelledby="safety-rate">
                <div class="stat-number success" aria-label="{stats.get('safety_rate', 0):.1f}% safety rate">{stats.get('safety_rate', 0):.1f}%</div>
                <div class="stat-label" id="safety-rate">Safety Rate</div>
            </div>
            <div class="stat-card" role="article" aria-labelledby="quality-score">
                <div class="stat-number success" aria-label="{stats.get('quality_score', 0)*100:.1f}% quality score">{stats.get('quality_score', 0)*100:.1f}%</div>
                <div class="stat-label" id="quality-score">Quality Score</div>
            </div>
        </section>
        
        <footer class="footer" role="contentinfo">
            <div aria-label="GovHack 2025 project information">
                <strong>🏆 GovHack 2025 Winner</strong> • Built with Google Agent2Agent (A2A) Protocol
            </div>
            <div class="agent-info">
                🤖 Generated by {self.agent_id} v{self.version} • Multi-Agent Pipeline Integration
            </div>
        </footer>
    </div>
</body>
</html>"""
            
            # Write to live dashboard file
            output_path = self.output_dir / "live_dashboard.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print(f"✅ Generated live dashboard: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating dashboard: {str(e)}")
            return False
    
    def send_a2a_message(self, receiver, message_type, payload):
        """Send A2A protocol message to other agents"""
        message = {
            'sender': self.agent_id,
            'receiver': receiver,
            'message_type': message_type,
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"📤 A2A Message: {self.agent_id} -> {receiver} ({message_type})")
        return message
    
    def run(self):
        """Main execution method"""
        print(f"🎨 Starting {self.agent_id} execution...")
        
        # Send startup message via A2A protocol
        startup_msg = self.send_a2a_message(
            receiver='coordinator',
            message_type='agent_status',
            payload={'status': 'starting', 'task': 'visualization_generation'}
        )
        
        try:
            # Collect live data from pipeline
            print("📊 Collecting live pipeline data...")
            pipeline_data = self.collect_pipeline_data()
            
            if pipeline_data:
                # Generate dynamic dashboard
                print("🎨 Generating dynamic dashboard...")
                success = self.generate_dynamic_dashboard(pipeline_data)
                
                if success:
                    # Send completion message
                    completion_msg = self.send_a2a_message(
                        receiver='coordinator',
                        message_type='task_complete',
                        payload={
                            'status': 'completed',
                            'task': 'visualization_generation',
                            'output_file': 'frontend/live_dashboard.html',
                            'stats_summary': pipeline_data['stats']
                        }
                    )
                    print("✅ Visualization agent completed successfully!")
                    return True
                else:
                    # Send error message
                    error_msg = self.send_a2a_message(
                        receiver='coordinator', 
                        message_type='task_error',
                        payload={'status': 'failed', 'error': 'Dashboard generation failed'}
                    )
                    print("❌ Dashboard generation failed!")
                    return False
            else:
                print("❌ No pipeline data available")
                return False
                
        except Exception as e:
            print(f"❌ Visualization agent error: {str(e)}")
            error_msg = self.send_a2a_message(
                receiver='coordinator',
                message_type='task_error', 
                payload={'status': 'failed', 'error': str(e)}
            )
            return False

def main():
    """Main entry point for the visualization agent"""
    agent = VisualizationAgent()
    
    print("🎨 GovHack 2025: Visualization Agent")
    print("=" * 50)
    print("Generating live dashboard from multi-agent pipeline data...")
    
    success = agent.run()
    
    if success:
        print(f"✅ Visualization complete! View at: frontend/live_dashboard.html")
    else:
        print("❌ Visualization failed!")
    
    return success

if __name__ == "__main__":
    main()