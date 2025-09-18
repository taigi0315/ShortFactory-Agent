"""
Cost Optimization System
Reduces API costs by validating inputs and optimizing requests before sending to AI models
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class CostOptimizer:
    """
    Cost optimization system that validates and optimizes requests before sending to AI
    """
    
    @staticmethod
    def validate_prompt_quality(prompt: str, context_name: str = "unknown") -> Tuple[bool, str]:
        """
        Validate prompt quality to avoid wasted API calls
        
        Args:
            prompt: The prompt to validate
            context_name: Context for logging
            
        Returns:
            Tuple[bool, str]: (is_valid, reason)
        """
        logger.debug(f"🔍 Validating prompt quality for {context_name}")
        
        # Basic length validation
        if len(prompt.strip()) < 50:
            return False, "Prompt too short (< 50 characters)"
        
        if len(prompt) > 50000:
            return False, "Prompt too long (> 50,000 characters)"
        
        # Check for required elements in prompts
        required_keywords = {
            'full_script': ['JSON', 'scene', 'title'],
            'scene_': ['scene_number', 'narration_script', 'visuals', 'JSON'],
            'image_': ['image', 'prompt', 'generate']
        }
        
        context_type = None
        for key in required_keywords:
            if key in context_name.lower():
                context_type = key
                break
        
        if context_type and context_type in required_keywords:
            missing_keywords = []
            for keyword in required_keywords[context_type]:
                if keyword.lower() not in prompt.lower():
                    missing_keywords.append(keyword)
            
            if missing_keywords:
                return False, f"Missing required keywords: {missing_keywords}"
        
        # Check for JSON format requirement
        if 'JSON' in prompt and 'json' not in prompt.lower():
            return False, "JSON requirement mentioned but not properly specified"
        
        logger.debug(f"✅ Prompt validation passed for {context_name}")
        return True, "Valid"
    
    @staticmethod
    def optimize_prompt_for_cost(prompt: str, context_name: str = "unknown") -> str:
        """
        Optimize prompt to reduce token usage while maintaining quality
        
        Args:
            prompt: Original prompt
            context_name: Context for logging
            
        Returns:
            str: Optimized prompt
        """
        logger.debug(f"🔧 Optimizing prompt for cost efficiency: {context_name}")
        
        optimized = prompt
        
        # Remove excessive whitespace
        lines = optimized.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line:  # Keep non-empty lines
                cleaned_lines.append(cleaned_line)
            elif len(cleaned_lines) > 0 and cleaned_lines[-1] != '':  # Keep single empty lines
                cleaned_lines.append('')
        
        optimized = '\n'.join(cleaned_lines)
        
        # Remove redundant instructions
        redundant_phrases = [
            'Remember to',
            'Make sure to',
            'Don\'t forget to',
            'It is important to',
            'Please ensure that',
        ]
        
        for phrase in redundant_phrases:
            # Only remove if there are multiple instances
            if optimized.count(phrase) > 1:
                optimized = optimized.replace(phrase, '', 1)  # Remove first instance only
        
        # Calculate savings
        original_length = len(prompt)
        optimized_length = len(optimized)
        savings = original_length - optimized_length
        
        if savings > 0:
            logger.debug(f"🔧 Prompt optimized: saved {savings} characters ({savings/original_length*100:.1f}%)")
        
        return optimized
    
    @staticmethod
    def validate_response_before_parsing(response: str, context_name: str = "unknown") -> Tuple[bool, str]:
        """
        Validate AI response before expensive parsing operations
        
        Args:
            response: AI response to validate
            context_name: Context for logging
            
        Returns:
            Tuple[bool, str]: (is_valid, reason)
        """
        logger.debug(f"🔍 Pre-validating response for {context_name}")
        
        if not response or not response.strip():
            return False, "Empty response"
        
        # Check minimum length
        if len(response.strip()) < 20:
            return False, "Response too short (< 20 characters)"
        
        # Check for JSON if expected
        if 'scene_' in context_name.lower() or 'full_script' in context_name.lower():
            if '{' not in response or '}' not in response:
                return False, "No JSON structure found in response"
            
            # Count braces for basic structure validation
            open_braces = response.count('{')
            close_braces = response.count('}')
            
            if abs(open_braces - close_braces) > 3:  # Allow some tolerance
                return False, f"Severely unbalanced JSON braces ({open_braces} open, {close_braces} close)"
        
        # Check for obvious errors
        error_indicators = [
            'I cannot',
            'I\'m unable',
            'I apologize',
            'Error:',
            'Sorry,',
            'I don\'t have',
            'As an AI'
        ]
        
        response_lower = response.lower()
        for indicator in error_indicators:
            if indicator.lower() in response_lower[:200]:  # Check first 200 chars
                return False, f"Response contains error indicator: {indicator}"
        
        logger.debug(f"✅ Response pre-validation passed for {context_name}")
        return True, "Valid"
    
    @staticmethod
    def estimate_cost_savings(session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate cost savings from optimizations
        
        Args:
            session_data: Session data with timing and retry information
            
        Returns:
            Dict with cost savings analysis
        """
        total_requests = 0
        failed_requests = 0
        retry_requests = 0
        
        # Analyze build report if available
        if 'build_report' in session_data:
            build_report = session_data['build_report']
            
            # Count errors (failed requests)
            if 'errors' in build_report:
                failed_requests = len(build_report['errors'])
            
            # Estimate total requests from stages
            stages = build_report.get('stages', {})
            for stage_name, stage_info in stages.items():
                if 'full_script' in stage_name:
                    total_requests += 1
                elif 'scene_script' in stage_name:
                    # Estimate scene count from other data
                    scene_count = len(session_data.get('scene_packages', []))
                    total_requests += scene_count
        
        # Calculate savings
        successful_requests = total_requests - failed_requests
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        # Estimate cost (rough approximation)
        estimated_cost_per_request = 0.02  # $0.02 per request (rough estimate)
        total_cost = total_requests * estimated_cost_per_request
        wasted_cost = failed_requests * estimated_cost_per_request
        
        savings_analysis = {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': success_rate,
            'estimated_total_cost': total_cost,
            'estimated_wasted_cost': wasted_cost,
            'estimated_savings_potential': wasted_cost,
            'recommendations': []
        }
        
        # Add recommendations
        if success_rate < 0.9:
            savings_analysis['recommendations'].append(
                "Success rate is below 90%. Consider implementing more robust validation."
            )
        
        if failed_requests > 0:
            savings_analysis['recommendations'].append(
                f"Prevented {failed_requests} failed requests could save ~${wasted_cost:.2f}"
            )
        
        return savings_analysis
    
    @staticmethod
    def should_retry_request(error_message: str, attempt_number: int, max_retries: int = 3) -> bool:
        """
        Determine if a request should be retried based on the error
        
        Args:
            error_message: The error message from the failed request
            attempt_number: Current attempt number (1-based)
            max_retries: Maximum number of retries allowed
            
        Returns:
            bool: Whether to retry the request
        """
        if attempt_number >= max_retries:
            return False
        
        # Don't retry for certain types of errors that won't be fixed by retrying
        non_retryable_errors = [
            'invalid api key',
            'quota exceeded',
            'billing',
            'permission denied',
            'unauthorized',
            'forbidden',
            'content policy',
            'safety filter'
        ]
        
        error_lower = error_message.lower()
        for non_retryable in non_retryable_errors:
            if non_retryable in error_lower:
                logger.info(f"❌ Not retrying due to non-retryable error: {non_retryable}")
                return False
        
        # Retry for network/temporary errors
        retryable_errors = [
            'timeout',
            'connection',
            'network',
            'server error',
            'internal error',
            'rate limit',
            'too many requests',
            'service unavailable',
            'bad gateway',
            'gateway timeout'
        ]
        
        for retryable in retryable_errors:
            if retryable in error_lower:
                logger.info(f"🔄 Retrying due to temporary error: {retryable}")
                return True
        
        # Default: retry for unknown errors (could be temporary)
        logger.info(f"🔄 Retrying unknown error (attempt {attempt_number}/{max_retries})")
        return True
    
    @staticmethod
    def get_optimal_retry_delay(attempt_number: int, base_delay: float = 2.0) -> float:
        """
        Calculate optimal retry delay with exponential backoff and jitter
        
        Args:
            attempt_number: Current attempt number (1-based)
            base_delay: Base delay in seconds
            
        Returns:
            float: Delay in seconds
        """
        import random
        
        # Exponential backoff: base_delay * (2 ^ (attempt - 1))
        exponential_delay = base_delay * (2 ** (attempt_number - 1))
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.5, 1.5)
        final_delay = exponential_delay * jitter
        
        # Cap maximum delay at 30 seconds
        return min(final_delay, 30.0)

# Convenience functions for integration
def validate_and_optimize_prompt(prompt: str, context_name: str = "unknown") -> Tuple[bool, str, str]:
    """
    Validate and optimize a prompt before sending to AI
    
    Returns:
        Tuple[bool, str, str]: (is_valid, optimized_prompt, validation_message)
    """
    # Validate first
    is_valid, reason = CostOptimizer.validate_prompt_quality(prompt, context_name)
    if not is_valid:
        return False, prompt, reason
    
    # Optimize if valid
    optimized_prompt = CostOptimizer.optimize_prompt_for_cost(prompt, context_name)
    return True, optimized_prompt, "Valid and optimized"

def validate_response_quality(response: str, context_name: str = "unknown") -> Tuple[bool, str]:
    """
    Validate AI response before expensive parsing
    
    Returns:
        Tuple[bool, str]: (is_valid, reason)
    """
    return CostOptimizer.validate_response_before_parsing(response, context_name)
