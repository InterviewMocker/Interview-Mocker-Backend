import json
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class StreamJsonParser:
    """
    Parses a stream of text to extract JSON objects.
    Expects a stream of independent JSON objects (e.g. JSON Lines or concatenated objects).
    Automatically handles whitespace and basic markdown fence stripping.
    """
    def __init__(self):
        self.buffer = ""
        self.decoder = json.JSONDecoder()
        
    def feed(self, chunk: str) -> List[Dict[str, Any]]:
        """
        Feed a chunk of text and return any complete JSON objects found.
        """
        self.buffer += chunk
        found_objects = []
        
        while True:
            # Clean buffer of initial whitespace or markdown markers if present at start
            self.buffer = self.buffer.lstrip()
            
            # Remove ```json or ``` if at the very start
            if self.buffer.startswith("```"):
                # Find end of line
                newline_pos = self.buffer.find('\n')
                if newline_pos != -1:
                    self.buffer = self.buffer[newline_pos+1:]
                    continue
                else:
                    # Waiting for newline to consume the marker
                    break
            
            if not self.buffer:
                break
                
            try:
                # Try to decode a JSON object from the start of the buffer
                obj, idx = self.decoder.raw_decode(self.buffer)
                
                # Check if it looks like a question
                if self._is_valid_question(obj):
                    found_objects.append(obj)
                
                # Advance buffer
                self.buffer = self.buffer[idx:]
            except json.JSONDecodeError:
                # Not enough data for a full object yet, or invalid data
                # If buffer is huge and we are stuck, we might want to skip char (error recovery),
                # but for now assume LLM produces valid JSON eventually.
                break
                
        return found_objects

    def _is_valid_question(self, obj: Any) -> bool:
        """Check if the object looks like a question"""
        return (
            isinstance(obj, dict) 
            and "title" in obj
        )
