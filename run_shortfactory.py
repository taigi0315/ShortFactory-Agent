#!/usr/bin/env python3
"""
Runner script for the new multi-agent architecture
"""

import sys
import os
import asyncio
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main_new_architecture

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='New Architecture Multi-Agent Video Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_new_architecture.py "Why are dachshunds short?"
  python run_new_architecture.py "Blockchain Technology" --cost
  python run_new_architecture.py "Climate Change" --length "2-3min" --style "serious and informative"
  python run_new_architecture.py --test --cost
        """
    )
    
    parser.add_argument('topic', nargs='?', help='Video topic (e.g., "Why are dachshunds short?")')
    parser.add_argument('--length', default='60-90s', 
                       help='Video length preference (default: 60-90s)')
    parser.add_argument('--style', default='educational and engaging', 
                       help='Style profile (default: educational and engaging)')
    parser.add_argument('--audience', default='general', 
                       help='Target audience (default: general)')
    parser.add_argument('--language', default='English', 
                       help='Content language (default: English)')
    parser.add_argument('--cost', action='store_true', 
                       help='Use cost-saving mode (mock images)')
    parser.add_argument('--refs', nargs='*', 
                       help='Knowledge references (URLs or citations)')
    parser.add_argument('--test', action='store_true', 
                       help='Run test mode with sample topic')
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Handle test mode
    if args.test:
        print("🧪 Running in test mode...")
        test_topic = "Why are dachshunds so short?"
        test_refs = [
            "Parker, H. G. et al. FGF4 retrogene on CFA12 is responsible for chondrodysplasia and intervertebral disc disease in dogs. PNAS (2009)"
        ]
        
        asyncio.run(main_new_architecture(
            topic=test_topic,
            length_preference=args.length,
            style_profile=args.style,
            target_audience=args.audience,
            language=args.language,
            knowledge_refs=test_refs,
            cost_saving_mode=args.cost
        ))
    else:
        # Validate topic
        if not args.topic:
            print("❌ Error: Topic is required (or use --test for test mode)")
            print("Usage: python run_new_architecture.py \"Your Topic Here\"")
            sys.exit(1)
        
        # Normal mode
        asyncio.run(main_new_architecture(
            topic=args.topic,
            length_preference=args.length,
            style_profile=args.style,
            target_audience=args.audience,
            language=args.language,
            knowledge_refs=args.refs,
            cost_saving_mode=args.cost
        ))

if __name__ == "__main__":
    main()
