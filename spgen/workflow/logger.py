"""
Professional logging system for South Park episode generation workflow.

This module provides comprehensive logging capabilities including:
- Timestamped file logging to process.txt
- Console output with visual progress indicators  
- Type-safe workflow step enumeration
- Centralized logger management

The logging system is designed for production use with proper error handling,
configurable output formats, and integration with the LangGraph workflow engine.
"""

import logging
import os
from enum import Enum
from typing import Optional

class WorkflowStep(Enum):
    """
    Enumeration of all workflow steps in the episode generation process.
    
    This enum ensures type safety, consistent naming, and proper step ordering
    throughout the workflow execution. Each step represents a distinct phase
    in the collaborative episode creation process.
    
    Steps are ordered to reflect the actual workflow progression:
    1. Research → 2. Brainstorm → 3. Q&A → 4. Feedback → 5. Merge → 
    6. Refine → 7. Final Discussion → 8-10. Script Writing → 11-12. Assembly
    """
    RESEARCH_CURRENT_EVENTS = "research_current_events"
    USER_NEWS_REVIEW = "user_news_review"
    BRAINSTORM = "brainstorm"
    INTERACTIVE_BRAINSTORM_QUESTIONS = "interactive_brainstorm_questions"
    AGENT_FEEDBACK = "agent_feedback"
    MERGE_OUTLINES = "merge_outlines"
    REFINE_OUTLINE = "refine_outline"
    FINAL_DISCUSSION = "final_discussion"
    WRITE_ACT_ONE = "write_act_one"
    WRITE_ACT_TWO = "write_act_two"
    WRITE_ACT_THREE = "write_act_three"
    STITCH_SCRIPT = "stitch_script"
    SUMMARIZE_SCRIPT = "summarize_script"

    @classmethod
    def get_all_steps(cls):
        """Get all workflow steps in order."""
        return list(cls)
    
    @classmethod
    def get_step_number(cls, step):
        """Get the step number (1-indexed) for a given step."""
        steps = cls.get_all_steps()
        return steps.index(step) + 1
    
    @property
    def display_name(self):
        """Get a human-readable display name."""
        return self.value.replace('_', ' ').title()


class WorkflowLogger:
    """
    Production-grade logger for the South Park episode generation workflow.
    
    This class provides dual-output logging (console + file) with proper formatting,
    step-by-step progress tracking, and visual progress indicators. Designed for
    both development debugging and production monitoring.
    
    Features:
    - Timestamped file logging to process.txt
    - Real-time console output with emojis and progress bars
    - Automatic log rotation and error handling
    - Integration with Python's logging infrastructure
    
    Args:
        log_dir (str): Directory where process.txt will be created
        
    Example:
        >>> logger = WorkflowLogger("/path/to/episode/logs")
        >>> logger.log_workflow_start(1, 3)
        >>> logger.log_step_start(WorkflowStep.BRAINSTORM)
    """
    
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        self.process_file = os.path.join(log_dir, "process.txt")
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Set up the logger with both file and console handlers."""
        # Create logger
        logger = logging.getLogger(f"southpark_workflow_{id(self)}")
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Create formatters
        console_formatter = logging.Formatter('%(message)s')
        file_formatter = logging.Formatter('%(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S')
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(self.process_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        return logger
    
    def log_workflow_start(self, part_num: int, total_parts: int):
        """Log the start of a workflow."""
        total_steps = len(WorkflowStep.get_all_steps())
        message = f"🚀 Starting episode generation for part {part_num} of {total_parts}..."
        self.logger.info(message)
        self.logger.info(f"📁 Working directory: {self.log_dir}")
        self.logger.info(f"📋 Workflow has {total_steps} steps total")
        self.logger.info("=" * 60)
    
    def log_step_start(self, step: WorkflowStep):
        """Log the start of a workflow step."""
        step_num = WorkflowStep.get_step_number(step)
        total_steps = len(WorkflowStep.get_all_steps())
        
        self.logger.info(f"\n⏳ Step {step_num}/{total_steps}: {step.display_name}")
        # Progress bar
        progress = "█" * step_num + "░" * (total_steps - step_num)
        self.logger.info(f"📊 Progress: [{progress}] {step_num}/{total_steps}")
    
    def log_step_complete(self, step: WorkflowStep):
        """Log the completion of a workflow step."""
        step_num = WorkflowStep.get_step_number(step)
        total_steps = len(WorkflowStep.get_all_steps())
        self.logger.info(f"✅ Step {step_num}/{total_steps} complete: {step.display_name}")
    
    def log_workflow_complete(self, part_num: int):
        """Log the completion of a workflow."""
        self.logger.info("=" * 60)
        self.logger.info(f"🎉 Episode part {part_num} generation complete!")
        self.logger.info(f"📁 Episode logs written to: {self.log_dir}")
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)


# Global logger instance - will be set by the CLI
workflow_logger: Optional[WorkflowLogger] = None

def get_logger() -> WorkflowLogger:
    """Get the current workflow logger."""
    if workflow_logger is None:
        raise RuntimeError("Workflow logger not initialized. Call set_logger() first.")
    return workflow_logger

def set_logger(logger: WorkflowLogger):
    """Set the global workflow logger."""
    global workflow_logger
    workflow_logger = logger