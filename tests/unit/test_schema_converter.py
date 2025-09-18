"""
테스트: Pydantic to ADK Schema Converter
Pydantic 모델이 ADK 스키마로 올바르게 변환되는지 테스트
"""

import pytest
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.schema_converter import PydanticToADKSchema, ADKSchemaValidator
from schemas.input_models import FullScriptInput, SceneExpansionInput, ImageGenerationInput
from schemas.output_models import FullScriptOutput, ScenePackageOutput, ImageAssetOutput


class TestPydanticToADKSchema:
    """Pydantic → ADK 스키마 conversion test"""

    def test_convert_full_script_input(self):
        """FullScriptInput → ADK 스키마 conversion test"""
        adk_schema = PydanticToADKSchema.convert_model_to_schema(FullScriptInput)
        
        # 기본 구조 확인
        assert adk_schema["type"] == "object"
        assert "properties" in adk_schema
        assert "required" in adk_schema
        
        # 필수 필드들 확인
        properties = adk_schema["properties"]
        assert "topic" in properties
        assert "length_preference" in properties
        assert "style_profile" in properties
        
        # topic 필드 상세 확인
        topic_prop = properties["topic"]
        assert topic_prop["type"] == "string"
        assert "minLength" in topic_prop
        assert topic_prop["minLength"] == 5

    def test_convert_scene_package_output(self):
        """ScenePackageOutput → ADK 스키마 conversion test"""
        adk_schema = PydanticToADKSchema.convert_model_to_schema(ScenePackageOutput)
        
        # 기본 구조 확인
        assert adk_schema["type"] == "object"
        assert "properties" in adk_schema
        
        properties = adk_schema["properties"]
        
        # 핵심 필드들 확인
        assert "scene_number" in properties
        assert "narration_script" in properties
        assert "visuals" in properties
        assert "tts" in properties
        assert "timing" in properties
        
        # SFX 관련 필드가 없는지 확인 (실제 사용하지 않음)
        assert "sfx_cues" not in properties
        
        # 배열 타입 확인
        narration_prop = properties["narration_script"]
        assert narration_prop["type"] == "array"
        assert "items" in narration_prop

    def test_get_output_key_generation(self):
        """output_key 자동 generation test"""
        
        # 다양한 모델들의 output_key 생성
        test_cases = [
            (FullScriptInput, "full_script_input_result"),
            (FullScriptOutput, "full_script_output_result"),
            (ScenePackageOutput, "scene_package_output_result"),
            (ImageAssetOutput, "image_asset_output_result")
        ]
        
        for model_class, expected_key in test_cases:
            output_key = PydanticToADKSchema.get_output_key(model_class)
            assert output_key == expected_key, f"{model_class.__name__}: {output_key} != {expected_key}"

    def test_schema_validation(self):
        """생성된 ADK 스키마가 유효한지 테스트"""
        
        models_to_test = [
            FullScriptInput,
            FullScriptOutput, 
            ScenePackageOutput,
            ImageAssetOutput
        ]
        
        for model_class in models_to_test:
            adk_schema = PydanticToADKSchema.convert_model_to_schema(model_class)
            is_valid = ADKSchemaValidator.validate_adk_schema(adk_schema)
            
            assert is_valid, f"{model_class.__name__} 스키마가 ADK 규격에 맞지 않음"

    def test_enum_handling(self):
        """Enum 타입 handling test"""
        adk_schema = PydanticToADKSchema.convert_model_to_schema(FullScriptInput)
        
        properties = adk_schema["properties"]
        
        # length_preference는 enum이어야 함
        if "length_preference" in properties:
            length_prop = properties["length_preference"]
            # enum 또는 string이어야 함 (ADK 호환)
            assert length_prop["type"] == "string"

    def test_nested_object_handling(self):
        """중첩된 객체 handling test"""
        adk_schema = PydanticToADKSchema.convert_model_to_schema(ScenePackageOutput)
        
        properties = adk_schema["properties"]
        
        # tts 필드는 중첩 객체
        if "tts" in properties:
            tts_prop = properties["tts"]
            assert tts_prop["type"] == "object"
            assert "properties" in tts_prop

    def test_array_handling(self):
        """배열 타입 handling test"""
        adk_schema = PydanticToADKSchema.convert_model_to_schema(ScenePackageOutput)
        
        properties = adk_schema["properties"]
        
        # narration_script는 배열
        if "narration_script" in properties:
            narration_prop = properties["narration_script"]
            assert narration_prop["type"] == "array"
            assert "items" in narration_prop
            
            # 배열 아이템도 객체여야 함
            items_schema = narration_prop["items"]
            assert items_schema["type"] == "object"


class TestADKSchemaValidator:
    """ADK 스키마 검증기 테스트"""

    def test_valid_schema(self):
        """유효한 ADK 스키마 검증"""
        valid_schema = {
            "type": "object",
            "description": "Test schema",
            "properties": {
                "test_field": {
                    "type": "string",
                    "description": "Test field"
                }
            },
            "required": ["test_field"]
        }
        
        assert ADKSchemaValidator.validate_adk_schema(valid_schema) == True

    def test_invalid_schema_missing_type(self):
        """type 필드 누락 스키마 검증"""
        invalid_schema = {
            "properties": {},
            "required": []
        }
        
        assert ADKSchemaValidator.validate_adk_schema(invalid_schema) == False

    def test_invalid_schema_wrong_type(self):
        """잘못된 type 필드 스키마 검증"""
        invalid_schema = {
            "type": "array",  # object가 아님
            "properties": {},
            "required": []
        }
        
        assert ADKSchemaValidator.validate_adk_schema(invalid_schema) == False

    def test_schema_conversion_test_utility(self):
        """스키마 conversion test 유틸리티 검증"""
        
        test_result = ADKSchemaValidator.test_schema_conversion(FullScriptInput)
        
        # 테스트 결과 구조 확인
        assert "model_class" in test_result
        assert "schema_valid" in test_result
        assert "output_key" in test_result
        
        # 성공적인 변환인지 확인
        assert test_result["schema_valid"] == True
        assert test_result["model_class"] == "FullScriptInput"
        assert test_result["output_key"] == "full_script_input_result"


class TestEndToEndConversion:
    """전체 변환 과정 테스트"""

    def test_all_input_models_conversion(self):
        """모든 입력 모델들의 conversion test"""
        input_models = [
            FullScriptInput,
            SceneExpansionInput,
            ImageGenerationInput
        ]
        
        for model_class in input_models:
            # conversion test
            test_result = ADKSchemaValidator.test_schema_conversion(model_class)
            
            assert test_result["schema_valid"] == True, f"{model_class.__name__} 변환 실패"
            assert "output_key" in test_result
            assert test_result["properties_count"] > 0

    def test_all_output_models_conversion(self):
        """모든 출력 모델들의 conversion test"""
        output_models = [
            FullScriptOutput,
            ScenePackageOutput,
            ImageAssetOutput
        ]
        
        for model_class in output_models:
            # conversion test
            test_result = ADKSchemaValidator.test_schema_conversion(model_class)
            
            assert test_result["schema_valid"] == True, f"{model_class.__name__} 변환 실패"
            assert test_result["properties_count"] > 0

    def test_schema_json_serialization(self):
        """생성된 스키마가 JSON 직렬화 가능한지 테스트"""
        adk_schema = PydanticToADKSchema.convert_model_to_schema(FullScriptOutput)
        
        # JSON 직렬화 테스트
        json_str = json.dumps(adk_schema, indent=2)
        assert len(json_str) > 0
        
        # 다시 파싱 가능한지 테스트
        parsed_schema = json.loads(json_str)
        assert parsed_schema == adk_schema


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
