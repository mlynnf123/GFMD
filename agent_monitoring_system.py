#!/usr/bin/env python3
"""
Agent Monitoring System - Replaces LangSmith
Comprehensive monitoring of agent interactions, performance, and collaboration
"""

import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from google.cloud import monitoring_v3
from google.cloud import logging as gcloud_logging
import logging

@dataclass
class AgentInteraction:
    """Represents a single agent interaction"""
    interaction_id: str
    session_id: str
    agent_id: str
    agent_role: str
    interaction_type: str  # research, qualification, email, coordination
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None

@dataclass
class AgentCollaboration:
    """Represents collaboration between agents"""
    collaboration_id: str
    session_id: str
    initiator_agent: str
    target_agent: str
    collaboration_type: str  # request, response, negotiate, delegate
    message_data: Dict[str, Any]
    timestamp: datetime
    success: bool = True

@dataclass
class MonitoringSession:
    """Represents a complete monitoring session"""
    session_id: str
    session_type: str  # prospect_processing, batch_processing, daily_automation
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_ms: Optional[float] = None
    interactions: List[AgentInteraction] = field(default_factory=list)
    collaborations: List[AgentCollaboration] = field(default_factory=list)
    prospects_processed: int = 0
    emails_sent: int = 0
    success: bool = True
    summary: Dict[str, Any] = field(default_factory=dict)

class AgentMonitoringSystem:
    """Comprehensive monitoring system for agent interactions"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.active_sessions: Dict[str, MonitoringSession] = {}
        self.completed_sessions: Dict[str, MonitoringSession] = {}
        
        # Setup Cloud Monitoring
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.project_path = f"projects/{project_id}"
        
        # Setup logging
        self.logger = logging.getLogger('agent-monitoring')
        self.logger.setLevel(logging.INFO)
        
        # Metrics tracking
        self.metrics = {
            "total_sessions": 0,
            "total_interactions": 0,
            "total_collaborations": 0,
            "average_processing_time": 0,
            "success_rate": 0,
            "agents_performance": {}
        }
    
    def start_session(self, session_type: str) -> str:
        """Start a new monitoring session"""
        session_id = str(uuid.uuid4())
        session = MonitoringSession(
            session_id=session_id,
            session_type=session_type,
            start_time=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        self.metrics["total_sessions"] += 1
        
        self.logger.info(f"Started monitoring session: {session_id} ({session_type})")
        
        # Send metric to Cloud Monitoring
        self._send_metric("session_started", 1, {"session_type": session_type})
        
        return session_id
    
    def end_session(self, session_id: str, results: Dict[str, Any] = None):
        """End a monitoring session"""
        if session_id not in self.active_sessions:
            self.logger.warning(f"Session {session_id} not found in active sessions")
            return
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.now()
        session.total_duration_ms = (session.end_time - session.start_time).total_seconds() * 1000
        
        if results:
            session.prospects_processed = results.get("prospects_processed", 0)
            session.emails_sent = results.get("emails_sent", 0)
            session.success = results.get("errors", []) == []
            session.summary = results
        
        # Move to completed sessions
        self.completed_sessions[session_id] = session
        del self.active_sessions[session_id]
        
        self.logger.info(f"Ended monitoring session: {session_id}")
        
        # Send metrics
        self._send_metric("session_completed", 1, {"session_type": session.session_type})
        self._send_metric("session_duration_ms", session.total_duration_ms, {"session_type": session.session_type})
        
        # Update performance metrics
        self._update_performance_metrics()
    
    def log_agent_interaction(
        self,
        session_id: str,
        agent_id: str,
        agent_role: str,
        interaction_type: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any] = None,
        start_time: datetime = None,
        end_time: datetime = None,
        success: bool = True,
        error_message: str = None
    ) -> str:
        """Log an agent interaction"""
        
        interaction_id = str(uuid.uuid4())
        
        if start_time is None:
            start_time = datetime.now()
        if end_time is None:
            end_time = datetime.now()
        
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        interaction = AgentInteraction(
            interaction_id=interaction_id,
            session_id=session_id,
            agent_id=agent_id,
            agent_role=agent_role,
            interaction_type=interaction_type,
            input_data=input_data,
            output_data=output_data or {},
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
        
        # Add to session if it exists
        if session_id in self.active_sessions:
            self.active_sessions[session_id].interactions.append(interaction)
        elif session_id in self.completed_sessions:
            self.completed_sessions[session_id].interactions.append(interaction)
        
        self.metrics["total_interactions"] += 1
        
        # Log interaction
        self.logger.info(f"Agent interaction: {agent_id} ({interaction_type}) - {duration_ms:.2f}ms")
        
        # Send metrics
        self._send_metric("agent_interaction", 1, {
            "agent_role": agent_role,
            "interaction_type": interaction_type,
            "success": str(success)
        })
        
        self._send_metric("agent_interaction_duration_ms", duration_ms, {
            "agent_role": agent_role,
            "interaction_type": interaction_type
        })
        
        return interaction_id
    
    def log_agent_collaboration(
        self,
        session_id: str,
        initiator_agent: str,
        target_agent: str,
        collaboration_type: str,
        message_data: Dict[str, Any],
        success: bool = True
    ) -> str:
        """Log agent-to-agent collaboration"""
        
        collaboration_id = str(uuid.uuid4())
        
        collaboration = AgentCollaboration(
            collaboration_id=collaboration_id,
            session_id=session_id,
            initiator_agent=initiator_agent,
            target_agent=target_agent,
            collaboration_type=collaboration_type,
            message_data=message_data,
            timestamp=datetime.now(),
            success=success
        )
        
        # Add to session if it exists
        if session_id in self.active_sessions:
            self.active_sessions[session_id].collaborations.append(collaboration)
        elif session_id in self.completed_sessions:
            self.completed_sessions[session_id].collaborations.append(collaboration)
        
        self.metrics["total_collaborations"] += 1
        
        self.logger.info(f"Agent collaboration: {initiator_agent} -> {target_agent} ({collaboration_type})")
        
        # Send metrics
        self._send_metric("agent_collaboration", 1, {
            "collaboration_type": collaboration_type,
            "success": str(success)
        })
        
        return collaboration_id
    
    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get detailed data for a specific session"""
        session = None
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
        elif session_id in self.completed_sessions:
            session = self.completed_sessions[session_id]
        
        if not session:
            return {"error": f"Session {session_id} not found"}
        
        # Convert to serializable format
        return {
            "session_id": session.session_id,
            "session_type": session.session_type,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "total_duration_ms": session.total_duration_ms,
            "prospects_processed": session.prospects_processed,
            "emails_sent": session.emails_sent,
            "success": session.success,
            "summary": session.summary,
            "interactions": [
                {
                    "interaction_id": i.interaction_id,
                    "agent_id": i.agent_id,
                    "agent_role": i.agent_role,
                    "interaction_type": i.interaction_type,
                    "start_time": i.start_time.isoformat(),
                    "end_time": i.end_time.isoformat() if i.end_time else None,
                    "duration_ms": i.duration_ms,
                    "success": i.success,
                    "error_message": i.error_message
                }
                for i in session.interactions
            ],
            "collaborations": [
                {
                    "collaboration_id": c.collaboration_id,
                    "initiator_agent": c.initiator_agent,
                    "target_agent": c.target_agent,
                    "collaboration_type": c.collaboration_type,
                    "timestamp": c.timestamp.isoformat(),
                    "success": c.success
                }
                for c in session.collaborations
            ],
            "agent_performance": self._analyze_session_performance(session)
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for monitoring"""
        
        # Recent sessions (last 24 hours)
        recent_sessions = []
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for session in self.completed_sessions.values():
            if session.start_time > cutoff_time:
                recent_sessions.append({
                    "session_id": session.session_id,
                    "session_type": session.session_type,
                    "start_time": session.start_time.isoformat(),
                    "duration_ms": session.total_duration_ms,
                    "prospects_processed": session.prospects_processed,
                    "emails_sent": session.emails_sent,
                    "success": session.success
                })
        
        # Agent performance summary
        agent_performance = self._calculate_agent_performance()
        
        return {
            "system_metrics": self.metrics,
            "recent_sessions": recent_sessions,
            "active_sessions": len(self.active_sessions),
            "agent_performance": agent_performance,
            "last_updated": datetime.now().isoformat(),
            "monitoring_period_hours": 24
        }
    
    def _analyze_session_performance(self, session: MonitoringSession) -> Dict[str, Any]:
        """Analyze performance for a specific session"""
        
        agent_stats = {}
        
        for interaction in session.interactions:
            agent_role = interaction.agent_role
            if agent_role not in agent_stats:
                agent_stats[agent_role] = {
                    "total_interactions": 0,
                    "total_duration_ms": 0,
                    "successful_interactions": 0,
                    "failed_interactions": 0
                }
            
            agent_stats[agent_role]["total_interactions"] += 1
            agent_stats[agent_role]["total_duration_ms"] += interaction.duration_ms or 0
            
            if interaction.success:
                agent_stats[agent_role]["successful_interactions"] += 1
            else:
                agent_stats[agent_role]["failed_interactions"] += 1
        
        # Calculate averages
        for role, stats in agent_stats.items():
            if stats["total_interactions"] > 0:
                stats["average_duration_ms"] = stats["total_duration_ms"] / stats["total_interactions"]
                stats["success_rate"] = stats["successful_interactions"] / stats["total_interactions"]
        
        return {
            "agent_statistics": agent_stats,
            "collaboration_count": len(session.collaborations),
            "total_processing_time_ms": session.total_duration_ms
        }
    
    def _calculate_agent_performance(self) -> Dict[str, Any]:
        """Calculate overall agent performance"""
        
        agent_performance = {}
        
        # Analyze all completed sessions
        for session in self.completed_sessions.values():
            for interaction in session.interactions:
                agent_role = interaction.agent_role
                
                if agent_role not in agent_performance:
                    agent_performance[agent_role] = {
                        "total_interactions": 0,
                        "successful_interactions": 0,
                        "total_duration_ms": 0,
                        "average_duration_ms": 0,
                        "success_rate": 0
                    }
                
                agent_performance[agent_role]["total_interactions"] += 1
                agent_performance[agent_role]["total_duration_ms"] += interaction.duration_ms or 0
                
                if interaction.success:
                    agent_performance[agent_role]["successful_interactions"] += 1
        
        # Calculate final metrics
        for role, stats in agent_performance.items():
            if stats["total_interactions"] > 0:
                stats["average_duration_ms"] = stats["total_duration_ms"] / stats["total_interactions"]
                stats["success_rate"] = stats["successful_interactions"] / stats["total_interactions"]
        
        return agent_performance
    
    def _update_performance_metrics(self):
        """Update overall system performance metrics"""
        
        if self.completed_sessions:
            total_duration = sum(s.total_duration_ms for s in self.completed_sessions.values() if s.total_duration_ms)
            self.metrics["average_processing_time"] = total_duration / len(self.completed_sessions)
            
            successful_sessions = sum(1 for s in self.completed_sessions.values() if s.success)
            self.metrics["success_rate"] = successful_sessions / len(self.completed_sessions)
    
    def _send_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Send custom metric to Cloud Monitoring"""
        try:
            # Create time series data
            now = datetime.now()
            seconds = int(now.timestamp())
            nanos = int((now.timestamp() % 1) * 10**9)
            
            interval = monitoring_v3.TimeInterval({
                "end_time": {"seconds": seconds, "nanos": nanos}
            })
            
            point = monitoring_v3.Point({
                "interval": interval,
                "value": {"double_value": value}
            })
            
            # Create time series
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/gfmd_swarm/{metric_name}"
            series.resource.type = "cloud_run_revision"
            series.resource.labels["project_id"] = self.project_id
            series.resource.labels["service_name"] = "gfmd-a2a-swarm-agent"
            series.resource.labels["revision_name"] = "latest"
            
            if labels:
                for key, value_str in labels.items():
                    series.metric.labels[key] = value_str
            
            series.points = [point]
            
            # Send to Cloud Monitoring
            self.monitoring_client.create_time_series(
                name=self.project_path,
                time_series=[series]
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to send metric {metric_name}: {e}")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get comprehensive monitoring statistics"""
        return {
            "system_metrics": self.metrics,
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.completed_sessions),
            "agent_performance": self._calculate_agent_performance(),
            "last_updated": datetime.now().isoformat()
        }

# Test the monitoring system
async def test_monitoring_system():
    """Test the agent monitoring system"""
    
    print("🧪 Testing Agent Monitoring System")
    print("=" * 60)
    
    # Create monitoring system
    monitoring = AgentMonitoringSystem("windy-tiger-471523-m5")
    
    # Start a test session
    session_id = monitoring.start_session("test_processing")
    print(f"✅ Started session: {session_id}")
    
    # Log some agent interactions
    monitoring.log_agent_interaction(
        session_id=session_id,
        agent_id="researcher_001",
        agent_role="researcher",
        interaction_type="research",
        input_data={"organization": "Test Hospital"},
        output_data={"research_complete": True}
    )
    
    monitoring.log_agent_collaboration(
        session_id=session_id,
        initiator_agent="researcher_001",
        target_agent="qualifier_001",
        collaboration_type="delegate",
        message_data={"task": "qualify prospect"}
    )
    
    # End session
    monitoring.end_session(session_id, {
        "prospects_processed": 1,
        "emails_sent": 1,
        "errors": []
    })
    
    # Get session data
    session_data = monitoring.get_session_data(session_id)
    print(f"📊 Session completed with {len(session_data['interactions'])} interactions")
    
    # Get dashboard data
    dashboard = monitoring.get_dashboard_data()
    print(f"📈 Dashboard shows {dashboard['system_metrics']['total_sessions']} total sessions")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_monitoring_system())