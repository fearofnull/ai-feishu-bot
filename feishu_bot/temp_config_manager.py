"""
Temporary Configuration Manager for Claude CLI

This module provides a context manager for creating and managing temporary
configuration directories for Claude Code CLI execution.
"""

import os
import tempfile
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TempConfigManager:
    """
    Manages temporary configuration directories for Claude Code CLI.
    
    This class implements the context manager protocol to ensure proper
    cleanup of temporary directories, even when exceptions occur.
    
    Usage:
        with TempConfigManager() as temp_dir:
            # CLAUDE_CONFIG_DIR environment variable is set
            # Execute Claude Code CLI commands
            pass
        # Temporary directory is automatically cleaned up
    
    Requirements:
        - 4.1: Create temporary directory with "claude_" prefix
        - 4.2: Set CLAUDE_CONFIG_DIR environment variable
        - 4.3: Delete temporary directory after execution
        - 4.4: Log errors if cleanup fails but continue processing
    """
    
    def __init__(self):
        """Initialize the temporary configuration manager."""
        self.temp_dir: Optional[str] = None
        self.original_config_dir: Optional[str] = None
    
    def create_temp_dir(self) -> str:
        """
        Create a temporary directory with "claude_" prefix.
        
        Returns:
            str: Path to the created temporary directory
            
        Raises:
            OSError: If directory creation fails
        """
        self.temp_dir = tempfile.mkdtemp(prefix="claude_")
        logger.debug(f"Created temporary directory: {self.temp_dir}")
        return self.temp_dir
    
    def cleanup(self, temp_dir: str) -> None:
        """
        Delete the temporary directory and its contents.
        
        Args:
            temp_dir: Path to the temporary directory to delete
            
        Note:
            If cleanup fails, logs the error but does not raise an exception,
            allowing the main process to continue.
        """
        try:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            # Log error but don't raise - cleanup failure shouldn't stop processing
            logger.error(f"Failed to cleanup temporary directory {temp_dir}: {e}")
    
    def __enter__(self) -> str:
        """
        Context manager entry point.
        
        Creates a temporary directory and sets the CLAUDE_CONFIG_DIR
        environment variable to point to it.
        
        Returns:
            str: Path to the temporary directory
        """
        # Save original CLAUDE_CONFIG_DIR if it exists
        self.original_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
        
        # Create temporary directory
        temp_dir = self.create_temp_dir()
        
        # Set CLAUDE_CONFIG_DIR environment variable
        os.environ["CLAUDE_CONFIG_DIR"] = temp_dir
        logger.debug(f"Set CLAUDE_CONFIG_DIR to: {temp_dir}")
        
        return temp_dir
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit point.
        
        Cleans up the temporary directory and restores the original
        CLAUDE_CONFIG_DIR environment variable, even if an exception occurred.
        
        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        # Cleanup temporary directory
        if self.temp_dir:
            self.cleanup(self.temp_dir)
        
        # Restore original CLAUDE_CONFIG_DIR or remove it
        if self.original_config_dir is not None:
            os.environ["CLAUDE_CONFIG_DIR"] = self.original_config_dir
            logger.debug(f"Restored CLAUDE_CONFIG_DIR to: {self.original_config_dir}")
        else:
            # Remove CLAUDE_CONFIG_DIR if it wasn't set originally
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
            logger.debug("Removed CLAUDE_CONFIG_DIR environment variable")
