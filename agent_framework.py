#!/usr/bin/env python3
"""
Multi-Agent Framework with Google Agent2Agent Protocol
Orchestrates collector agents, critic agent, and sorter agent communication
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import sys

class MessageType(Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    DATA_TRANSFER = "data_transfer"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    QUALITY_REPORT = "quality_report"

class AgentRole(Enum):
    COORDINATOR = "coordinator"
    COLLECTOR = "collector"
    CRITIC = "critic"
    SORTER = "sorter"

@dataclass
class A2AMessage:
    """Agent2Agent message format following Google ADK specification"""
    message_id: str
    sender_agent: str
    receiver_agent: str
    message_type: MessageType
    timestamp: str
    payload: Dict[str, Any]
    conversation_id: str = ""
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        return json.dumps(data, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'A2AMessage':
        """Create message from JSON string"""
        data = json.loads(json_str)
        data['message_type'] = MessageType(data['message_type'])
        return cls(**data)

class BaseAgent:
    """Base agent class implementing A2A protocol"""
    
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        self.message_queue = asyncio.Queue()
        self.running = False
        
    async def send_message(self, receiver: str, msg_type: MessageType, 
                          payload: Dict[str, Any], conversation_id: str = "") -> str:
        """Send A2A message to another agent"""
        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            sender_agent=self.agent_id,
            receiver_agent=receiver,
            message_type=msg_type,
            timestamp=datetime.now().isoformat(),
            payload=payload,
            conversation_id=conversation_id
        )
        
        # In production, this would use actual inter-agent communication
        # For demo, we'll use the coordinator to route messages
        print(f"📤 {self.agent_id} → {receiver}: {msg_type.value}")
        return message.message_id
    
    async def receive_message(self, message: A2AMessage) -> None:
        """Receive A2A message from another agent"""
        await self.message_queue.put(message)
    
    async def process_messages(self):
        """Process incoming messages"""
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self.handle_message(message)
            except asyncio.TimeoutError:
                continue
    
    async def handle_message(self, message: A2AMessage):
        """Handle received message - to be implemented by subclasses"""
        print(f"📥 {self.agent_id} received {message.message_type.value} from {message.sender_agent}")

class CoordinatorAgent(BaseAgent):
    """Main coordinator that orchestrates the multi-agent pipeline"""
    
    def __init__(self):
        super().__init__("coordinator", AgentRole.COORDINATOR)
        self.agents = {}
        self.pipeline_status = {
            'current_phase': 'initialization',
            'completed_agents': [],
            'failed_agents': [],
            'data_quality_score': None
        }
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the coordinator"""
        self.agents[agent.agent_id] = agent
        print(f"🔗 Registered agent: {agent.agent_id} ({agent.role.value})")
    
    async def start_pipeline(self):
        """Start the multi-agent data collection and analysis pipeline"""
        print("\n🚀 Starting Multi-Agent Anti-Scam Pipeline")
        print("=" * 50)
        
        self.running = True
        conversation_id = str(uuid.uuid4())
        
        # Phase 1: Data Collection
        await self.run_data_collection_phase(conversation_id)
        
        # Phase 2: Data Standardization  
        await self.run_standardization_phase(conversation_id)
        
        # Phase 3: Quality Review
        await self.run_quality_review_phase(conversation_id)
        
        # Phase 4: Final Sorting and Output
        await self.run_sorting_phase(conversation_id)
        
        # Generate final report
        await self.generate_final_report()
        
        self.running = False
    
    async def run_data_collection_phase(self, conversation_id: str):
        """Phase 1: Run all collector agents"""
        print(f"\n📊 Phase 1: Data Collection")
        print("-" * 30)
        
        self.pipeline_status['current_phase'] = 'data_collection'
        
        # Run collector agents
        collector_tasks = [
            ('government_services_scraper', 'gov_services_scraper.py'),
            ('nsw_hospitals_agent', 'nsw_hospitals_agent.py'), 
            ('scamwatch_threat_agent', 'scamwatch_threat_agent.py'),
            # ('acnc_data_agent', 'acnc_data_agent.py')  # Optional if charity data needed
        ]
        
        for agent_name, script_file in collector_tasks:
            print(f"  🤖 Starting {agent_name}...")
            
            # Send task request message
            await self.send_message(
                agent_name, 
                MessageType.TASK_REQUEST,
                {
                    'task': 'collect_data',
                    'script': script_file,
                    'phase': 'data_collection'
                },
                conversation_id
            )
            
            # Execute the collector script
            success = await self.execute_collector_script(script_file)
            
            if success:
                self.pipeline_status['completed_agents'].append(agent_name)
                print(f"    ✅ {agent_name} completed")
            else:
                self.pipeline_status['failed_agents'].append(agent_name)
                print(f"    ❌ {agent_name} failed")
    
    async def execute_collector_script(self, script_file: str) -> bool:
        """Execute a collector agent script"""
        try:
            # Check if script exists
            script_path = Path(script_file)
            if not script_path.exists():
                print(f"    ⚠️  Script {script_file} not found")
                return False
            
            # Run the script with timeout
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 min timeout
            
            if process.returncode == 0:
                return True
            else:
                print(f"    ❌ Script failed: {stderr.decode()}")
                return False
                
        except asyncio.TimeoutError:
            print(f"    ⏰ Script {script_file} timed out")
            return False
        except Exception as e:
            print(f"    ❌ Error running {script_file}: {e}")
            return False
    
    async def run_standardization_phase(self, conversation_id: str):
        """Phase 2: Standardize data format"""
        print(f"\n🔄 Phase 2: Data Standardization")
        print("-" * 30)
        
        self.pipeline_status['current_phase'] = 'standardization'
        
        # Send standardization task
        await self.send_message(
            'data_standardizer',
            MessageType.TASK_REQUEST,
            {
                'task': 'standardize_data',
                'input_files': ['government_services.csv', 'nsw_hospitals.csv', 'scamwatch_threats.csv'],
                'output_file': 'standardized_contacts.csv'
            },
            conversation_id
        )
        
        # Execute standardization
        success = await self.execute_collector_script('data_standardizer.py')
        
        if success:
            print(f"  ✅ Data standardization completed")
        else:
            print(f"  ❌ Data standardization failed")
    
    async def run_quality_review_phase(self, conversation_id: str):
        """Phase 3: Quality review by Critic Agent"""
        print(f"\n🔍 Phase 3: Quality Review")
        print("-" * 30)
        
        self.pipeline_status['current_phase'] = 'quality_review'
        
        # Send quality review request to critic
        await self.send_message(
            'critic_agent',
            MessageType.TASK_REQUEST,
            {
                'task': 'quality_review',
                'input_file': 'standardized_contacts.csv',
                'output_file': 'critic_report.json'
            },
            conversation_id
        )
        
        # Execute critic agent
        success = await self.execute_collector_script('critic_agent.py')
        
        if success:
            # Load quality score
            try:
                with open('critic_report.json', 'r') as f:
                    report = json.load(f)
                    quality_score = report['quality_assessment']['overall_quality_score']
                    quality_grade = report['quality_assessment']['quality_grade']
                    self.pipeline_status['data_quality_score'] = quality_score
                
                print(f"  ✅ Quality review completed - Grade: {quality_grade} ({quality_score:.2f})")
            except Exception as e:
                print(f"  ⚠️  Quality review completed but couldn't parse results: {e}")
        else:
            print(f"  ❌ Quality review failed")
    
    async def run_sorting_phase(self, conversation_id: str):
        """Phase 4: Final data sorting and categorization"""
        print(f"\n📋 Phase 4: Data Sorting")
        print("-" * 30)
        
        self.pipeline_status['current_phase'] = 'sorting'
        
        # Send sorting request
        await self.send_message(
            'sorter_agent',
            MessageType.TASK_REQUEST,
            {
                'task': 'sort_and_categorize',
                'input_file': 'standardized_contacts.csv',
                'quality_report': 'critic_report.json'
            },
            conversation_id
        )
        
        print(f"  ✅ Sorting phase ready (sorter agent implementation needed)")
    
    async def generate_final_report(self):
        """Generate final pipeline report"""
        print(f"\n📄 Pipeline Summary Report")
        print("=" * 50)
        
        report = {
            'pipeline_execution': {
                'timestamp': datetime.now().isoformat(),
                'final_phase': self.pipeline_status['current_phase'],
                'completed_agents': self.pipeline_status['completed_agents'],
                'failed_agents': self.pipeline_status['failed_agents'],
                'success_rate': len(self.pipeline_status['completed_agents']) / 
                              (len(self.pipeline_status['completed_agents']) + len(self.pipeline_status['failed_agents']))
                              if (len(self.pipeline_status['completed_agents']) + len(self.pipeline_status['failed_agents'])) > 0 else 0
            },
            'data_quality': {
                'overall_score': self.pipeline_status['data_quality_score'],
                'grade': 'A' if self.pipeline_status['data_quality_score'] and self.pipeline_status['data_quality_score'] >= 0.9 else 'B'
            },
            'output_files': [
                'standardized_contacts.csv',
                'critic_report.json', 
                'validation_report.json'
            ]
        }
        
        # Save report
        with open('pipeline_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ Completed Agents: {len(report['pipeline_execution']['completed_agents'])}")
        print(f"❌ Failed Agents: {len(report['pipeline_execution']['failed_agents'])}")
        print(f"📊 Success Rate: {report['pipeline_execution']['success_rate']:.1%}")
        if report['data_quality']['overall_score']:
            print(f"🎯 Data Quality: {report['data_quality']['grade']} ({report['data_quality']['overall_score']:.2f})")
        
        print(f"\n📄 Pipeline report saved to: pipeline_report.json")

class CollectorAgentProxy(BaseAgent):
    """Proxy for collector agents (existing scripts)"""
    
    def __init__(self, agent_id: str, script_file: str):
        super().__init__(agent_id, AgentRole.COLLECTOR)
        self.script_file = script_file

class CriticAgentProxy(BaseAgent):
    """Proxy for the critic agent"""
    
    def __init__(self):
        super().__init__("critic_agent", AgentRole.CRITIC)

class SorterAgent(BaseAgent):
    """Sorter agent for final data categorization"""
    
    def __init__(self):
        super().__init__("sorter_agent", AgentRole.SORTER)
    
    async def sort_and_categorize(self, input_file: str, quality_report_file: str):
        """Sort and categorize the final dataset"""
        print("  🗂️  Sorting contacts by category and risk level...")
        
        # Load standardized data
        import pandas as pd
        df = pd.read_csv(input_file)
        
        # Load quality report
        with open(quality_report_file, 'r') as f:
            quality_report = json.load(f)
        
        # Sort by organization type and confidence
        sorted_df = df.sort_values(['organization_type', 'confidence_score'], ascending=[True, False])
        
        # Create categorized outputs
        categories = {
            'government_contacts.csv': sorted_df[sorted_df['organization_type'] == 'government'],
            'hospital_contacts.csv': sorted_df[sorted_df['organization_type'] == 'hospital'],
            'threat_indicators.csv': sorted_df[sorted_df['organization_type'] == 'threat'],
            'charity_contacts.csv': sorted_df[sorted_df['organization_type'] == 'charity']
        }
        
        for filename, data in categories.items():
            if len(data) > 0:
                data.to_csv(filename, index=False)
                print(f"    📄 Created {filename} ({len(data)} records)")
        
        print(f"  ✅ Data sorting completed")

async def main():
    """Main function to run the multi-agent pipeline"""
    # Create coordinator
    coordinator = CoordinatorAgent()
    
    # Register agent proxies
    coordinator.register_agent(CollectorAgentProxy("government_services_scraper", "gov_services_scraper.py"))
    coordinator.register_agent(CollectorAgentProxy("nsw_hospitals_agent", "nsw_hospitals_agent.py"))
    coordinator.register_agent(CollectorAgentProxy("scamwatch_threat_agent", "scamwatch_threat_agent.py"))
    coordinator.register_agent(CriticAgentProxy())
    coordinator.register_agent(SorterAgent())
    
    # Start the pipeline
    await coordinator.start_pipeline()

def run_pipeline():
    """Synchronous wrapper to run the async pipeline"""
    asyncio.run(main())

if __name__ == "__main__":
    run_pipeline()