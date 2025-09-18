#!/usr/bin/env python3
"""
ADK-based ShortFactory System Runner
Uses proper ADK patterns with output_schema for guaranteed JSON format
"""

import asyncio
import argparse
import logging
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.session_manager import SessionManager
from agents.adk_orchestrator_agent import ADKOrchestratorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('adk_system.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function for ADK-based video generation"""
    parser = argparse.ArgumentParser(description="ADK-based ShortFactory Video Generation System")
    parser.add_argument("topic", nargs="?", help="Video topic (not required in test mode)")
    parser.add_argument("--length", default="60-90s", choices=["30-45s", "60-90s", "2-3min", "3-5min"], 
                       help="Video length preference")
    parser.add_argument("--style", default="informative and engaging", 
                       help="Overall style profile")
    parser.add_argument("--audience", default="general", 
                       help="Target audience")
    parser.add_argument("--language", default="English", 
                       choices=["English", "Korean", "Spanish", "French", "German", "Japanese"],
                       help="Content language")
    parser.add_argument("--cost", action="store_true", 
                       help="Enable cost-saving mode")
    parser.add_argument("--test", action="store_true",
                       help="Run test mode with sample data")
    
    args = parser.parse_args()
    
    if args.test:
        await run_test_mode()
        return
    
    if not args.topic:
        parser.error("topic is required when not in test mode")
    
    try:
        logger.info("🚀 Starting ADK-based ShortFactory System")
        logger.info(f"📝 Topic: {args.topic}")
        logger.info(f"⏱️ Length: {args.length}")
        logger.info(f"🎨 Style: {args.style}")
        logger.info(f"👥 Audience: {args.audience}")
        logger.info(f"🌐 Language: {args.language}")
        logger.info(f"💰 Cost-saving: {args.cost}")
        
        # Initialize system
        session_manager = SessionManager()
        orchestrator = ADKOrchestratorAgent(session_manager)
        
        # Generate video package
        start_time = datetime.now()
        
        package = await orchestrator.create_video_package(
            topic=args.topic,
            length_preference=args.length,
            style_profile=args.style,
            target_audience=args.audience,
            language=args.language,
            cost_saving_mode=args.cost
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Display results
        session_id = package.get("session_id")
        build_report = package.get("build_report", {})
        performance = build_report.get("performance_metrics", {})
        
        print(f"\n🎉 ADK Video Generation Complete!")
        print(f"📁 Session ID: {session_id}")
        print(f"⏱️ Total Time: {duration:.1f} seconds")
        print(f"✅ Success: {build_report.get('success', False)}")
        print(f"📊 Overall Success Rate: {performance.get('overall_success_rate', 0):.1%}")
        print(f"🔧 JSON Parsing Success: {performance.get('json_parsing_success_rate', 0):.1%}")
        print(f"📋 Schema Validation Success: {performance.get('schema_validation_success_rate', 0):.1%}")
        
        # Scene breakdown
        scenes_total = performance.get('total_scenes', 0)
        scenes_success = performance.get('successful_scenes', 0)
        scenes_failed = performance.get('failed_scenes', 0)
        
        print(f"\n📝 Scene Generation:")
        print(f"   Total Scenes: {scenes_total}")
        print(f"   ✅ Successful: {scenes_success}")
        print(f"   ❌ Failed: {scenes_failed}")
        
        # Validation results
        validation = package.get("build_report", {}).get("validation_results", {})
        if validation:
            print(f"\n🔍 Validation Results:")
            print(f"   Full Script Valid: {validation.get('full_script_valid', False)}")
            print(f"   Valid Scene Packages: {validation.get('scene_packages_valid', 0)}/{validation.get('total_scene_packages', 0)}")
            
            issues = validation.get('issues', [])
            if issues:
                print(f"   ⚠️ Issues Found: {len(issues)}")
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"     - {issue}")
        
        # File locations
        session_path = Path(f"sessions/{session_id}")
        print(f"\n📂 Generated Files:")
        print(f"   📄 Full Script: {session_path}/full_script.json")
        print(f"   📦 Production Package: {session_path}/production_package.json")
        print(f"   📊 Build Report: {session_path}/build_report.json")
        
        scene_files = list(session_path.glob("scene_package_*.json"))
        print(f"   🎬 Scene Packages: {len(scene_files)} files")
        
        if build_report.get("success"):
            print(f"\n🎊 Success! Video production package ready for assembly.")
        else:
            print(f"\n❌ Generation failed. Check build report for details.")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 Generation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        return 1

async def run_test_mode():
    """Run system in test mode with predefined scenarios"""
    logger.info("🧪 Running ADK system in test mode")
    
    test_scenarios = [
        {
            "topic": "Why do cats purr? The surprising science behind feline happiness",
            "length": "60-90s",
            "style": "informative and heartwarming",
            "audience": "general"
        },
        {
            "topic": "The hidden mathematics in everyday objects",
            "length": "2-3min", 
            "style": "informative and mysterious",
            "audience": "students"
        },
        {
            "topic": "How artificial intelligence learns to be creative",
            "length": "60-90s",
            "style": "informative and futuristic",
            "audience": "professionals"
        }
    ]
    
    session_manager = SessionManager()
    orchestrator = ADKOrchestratorAgent(session_manager)
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 Test Scenario {i}/{len(test_scenarios)}")
        print(f"📝 Topic: {scenario['topic']}")
        
        try:
            start_time = datetime.now()
            
            package = await orchestrator.create_video_package(
                topic=scenario["topic"],
                length_preference=scenario["length"],
                style_profile=scenario["style"],
                target_audience=scenario["audience"],
                cost_saving_mode=True  # Use cost-saving for tests
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            build_report = package.get("build_report", {})
            performance = build_report.get("performance_metrics", {})
            
            result = {
                "scenario": i,
                "topic": scenario["topic"],
                "success": build_report.get("success", False),
                "duration_seconds": duration,
                "scenes_total": performance.get("total_scenes", 0),
                "scenes_success": performance.get("successful_scenes", 0),
                "success_rate": performance.get("overall_success_rate", 0),
                "json_parsing_rate": performance.get("json_parsing_success_rate", 0),
                "session_id": package.get("session_id")
            }
            
            results.append(result)
            
            print(f"   ✅ Success: {result['success']}")
            print(f"   ⏱️ Duration: {result['duration_seconds']:.1f}s")
            print(f"   📊 Success Rate: {result['success_rate']:.1%}")
            print(f"   🔧 JSON Parsing: {result['json_parsing_rate']:.1%}")
            
        except Exception as e:
            logger.error(f"❌ Test scenario {i} failed: {e}")
            result = {
                "scenario": i,
                "topic": scenario["topic"],
                "success": False,
                "error": str(e)
            }
            results.append(result)
    
    # Summary
    successful_tests = sum(1 for r in results if r.get("success", False))
    total_tests = len(results)
    
    print(f"\n📊 Test Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Successful: {successful_tests}")
    print(f"   ❌ Failed: {total_tests - successful_tests}")
    print(f"   📈 Success Rate: {successful_tests/total_tests:.1%}")
    
    if successful_tests > 0:
        avg_duration = sum(r.get("duration_seconds", 0) for r in results if r.get("success")) / successful_tests
        avg_json_rate = sum(r.get("json_parsing_rate", 0) for r in results if r.get("success")) / successful_tests
        print(f"   ⏱️ Average Duration: {avg_duration:.1f}s")
        print(f"   🔧 Average JSON Success: {avg_json_rate:.1%}")
    
    # Save test results
    test_results_file = Path("test_results_adk.json")
    with open(test_results_file, 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "system_type": "adk_structured",
            "results": results,
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests/total_tests
            }
        }, f, indent=2)
    
    print(f"   📄 Test results saved to: {test_results_file}")

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
