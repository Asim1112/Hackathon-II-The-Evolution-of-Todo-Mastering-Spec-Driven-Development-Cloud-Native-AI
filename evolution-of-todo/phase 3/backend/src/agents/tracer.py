"""
Runtime tracer for agent execution path.
Logs every step of the ChatKit → Runner → MCP → Tools execution flow.
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentExecutionTracer:
    """Trace agent execution with precise timestamps and values."""

    def __init__(self):
        self.trace_id = None
        self.steps = []

    def start_trace(self):
        """Start a new execution trace."""
        self.trace_id = f"trace_{datetime.now().strftime('%H%M%S_%f')}"
        self.steps = []
        logger.info(f"[TRACER] 🚀 START Trace ID: {self.trace_id}")
        return self.trace_id

    def log_step(self, step_name: str, data: Any = None, details: str = ""):
        """Log a step in the execution flow."""
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": step_name,
            "data": data,
            "details": details,
            "trace_id": self.trace_id
        }
        self.steps.append(step_data)

        # Format data for logging
        data_str = str(data)[:200] + "..." if data and len(str(data)) > 200 else str(data)
        logger.info(f"[TRACER] [{self.trace_id}] {step_name}: {data_str} | {details}")

    def log_error(self, step_name: str, error: Exception, context: str = ""):
        """Log an error in the execution flow."""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "step": step_name,
            "error": str(error),
            "context": context,
            "trace_id": self.trace_id
        }
        self.steps.append(error_data)
        logger.error(f"[TRACER] [{self.trace_id}] ❌ {step_name}: ERROR={str(error)} | {context}")

    def end_trace(self):
        """End the execution trace."""
        logger.info(f"[TRACER] ✅ END Trace ID: {self.trace_id}, Total Steps: {len(self.steps)}")

    def get_trace_summary(self):
        """Get a summary of the trace."""
        return {
            "trace_id": self.trace_id,
            "total_steps": len(self.steps),
            "steps": self.steps
        }

# Global tracer instance
tracer = AgentExecutionTracer()

def get_tracer():
    """Get the global tracer instance."""
    return tracer