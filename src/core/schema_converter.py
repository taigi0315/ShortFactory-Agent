"""
Pydantic to ADK Schema Converter
Pydantic 모델을 ADK input_schema/output_schema 형식으로 자동 변환
"""

import json
import logging
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PydanticToADKSchema:
    """
    Pydantic 모델을 ADK 스키마로 변환하는 유틸리티
    
    ADK 공식 문서 패턴:
    https://google.github.io/adk-docs/agents/llm-agents/#structuring-data-input_schema-output_schema-output_key
    """
    
    @staticmethod
    def convert_model_to_schema(model_class: Type[BaseModel]) -> Dict[str, Any]:
        """
        Pydantic 모델을 ADK input_schema/output_schema 형식으로 변환
        
        Args:
            model_class: 변환할 Pydantic 모델 클래스
            
        Returns:
            Dict: ADK 호환 JSON 스키마
        """
        try:
            # Pydantic에서 JSON 스키마 생성
            pydantic_schema = model_class.model_json_schema()
            
            # ADK 형식으로 변환
            adk_schema = {
                "type": "object",
                "description": pydantic_schema.get("description", f"Schema for {model_class.__name__}"),
                "properties": pydantic_schema.get("properties", {}),
                "required": pydantic_schema.get("required", [])
            }
            
            # ADK에서 지원하지 않는 필드들 제거 ($defs 전달)
            adk_schema = PydanticToADKSchema._clean_schema_for_adk(
                adk_schema, 
                pydantic_schema.get("$defs", {})
            )
            
            logger.debug(f"✅ {model_class.__name__} → ADK 스키마 변환 완료")
            return adk_schema
            
        except Exception as e:
            logger.error(f"❌ {model_class.__name__} Schema conversion failed: {e}")
            # 기본 스키마 반환
            return {
                "type": "object",
                "description": f"Fallback schema for {model_class.__name__}",
                "properties": {},
                "required": []
            }
    
    @staticmethod
    def _clean_schema_for_adk(schema: Dict[str, Any], defs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        ADK에서 지원하지 않는 JSON 스키마 필드들 제거
        
        Args:
            schema: 원본 JSON 스키마
            defs: $defs 정의들
            
        Returns:
            Dict: ADK 호환 스키마
        """
        cleaned = schema.copy()
        if defs is None:
            defs = {}
        
        # ADK에서 지원하지 않는 필드들 제거
        unsupported_fields = [
            "$defs",  # Pydantic 내부 정의
            "title",  # ADK에서 자동 생성
            "allOf", "anyOf", "oneOf",  # 복잡한 조건들
        ]
        
        for field in unsupported_fields:
            if field in cleaned:
                del cleaned[field]
        
        # properties 내부도 재귀적으로 정리
        if "properties" in cleaned:
            cleaned["properties"] = PydanticToADKSchema._clean_properties(cleaned["properties"], defs)
        
        return cleaned
    
    @staticmethod
    def _clean_properties(properties: Dict[str, Any], defs: Dict[str, Any] = None) -> Dict[str, Any]:
        """properties 필드들을 ADK 호환으로 정리"""
        cleaned_props = {}
        if defs is None:
            defs = {}
        
        for prop_name, prop_schema in properties.items():
            if isinstance(prop_schema, dict):
                cleaned_prop = prop_schema.copy()
                
                # Pydantic 특화 필드들 제거
                pydantic_fields = ["title", "allOf", "anyOf", "oneOf", "$ref"]
                for field in pydantic_fields:
                    if field in cleaned_prop:
                        del cleaned_prop[field]
                
                # $ref 필드 처리 - 실제 정의를 resolve
                if "$ref" in prop_schema:
                    ref_path = prop_schema["$ref"]
                    # #/$defs/TTSSettings → TTSSettings
                    if ref_path.startswith("#/$defs/"):
                        def_name = ref_path.replace("#/$defs/", "")
                        if def_name in defs:
                            # 실제 정의로 교체
                            ref_definition = defs[def_name]
                            cleaned_prop.update(ref_definition)
                            # 기본값이 원본에 있으면 유지
                            if "default" in prop_schema:
                                cleaned_prop["default"] = prop_schema["default"]
                        else:
                            # 정의를 찾을 수 없으면 string으로 fallback
                            cleaned_prop["type"] = "string"
                    else:
                        cleaned_prop["type"] = "string"
                
                # enum 처리 (ADK 호환)
                if "enum" in cleaned_prop:
                    # enum 값들이 문자열인지 확인
                    enum_values = cleaned_prop["enum"]
                    if all(isinstance(v, str) for v in enum_values):
                        cleaned_prop["enum"] = enum_values
                    else:
                        # enum이 복잡하면 제거하고 string으로 변경
                        del cleaned_prop["enum"]
                        cleaned_prop["type"] = "string"
                
                # type 필드가 없으면 추가
                if "type" not in cleaned_prop:
                    if "properties" in cleaned_prop:
                        cleaned_prop["type"] = "object"
                    elif "items" in cleaned_prop:
                        cleaned_prop["type"] = "array"
                    else:
                        cleaned_prop["type"] = "string"  # 기본값
                
                # 중첩된 객체 처리
                if cleaned_prop.get("type") == "object" and "properties" in cleaned_prop:
                    cleaned_prop["properties"] = PydanticToADKSchema._clean_properties(
                        cleaned_prop["properties"], defs
                    )
                
                # 배열 items 처리
                if cleaned_prop.get("type") == "array" and "items" in cleaned_prop:
                    items_schema = cleaned_prop["items"]
                    if isinstance(items_schema, dict):
                        # items에 $ref가 있으면 resolve
                        if "$ref" in items_schema:
                            ref_path = items_schema["$ref"]
                            if ref_path.startswith("#/$defs/"):
                                def_name = ref_path.replace("#/$defs/", "")
                                if def_name in defs:
                                    cleaned_prop["items"] = defs[def_name].copy()
                                else:
                                    cleaned_prop["items"] = {"type": "string"}
                        # items가 object이고 properties가 있으면 재귀 처리
                        elif items_schema.get("type") == "object" and "properties" in items_schema:
                            items_copy = items_schema.copy()
                            items_copy["properties"] = PydanticToADKSchema._clean_properties(
                                items_schema["properties"], defs
                            )
                            cleaned_prop["items"] = items_copy
                
                cleaned_props[prop_name] = cleaned_prop
        
        return cleaned_props
    
    @staticmethod
    def validate_with_schema(data: Dict[str, Any], 
                           model_class: Type[BaseModel],
                           context_name: str = "unknown") -> BaseModel:
        """
        ADK 스키마로 검증 후 Pydantic 모델 반환
        
        Args:
            data: 검증할 데이터
            model_class: 목표 Pydantic 모델
            context_name: 로깅용 컨텍스트 이름
            
        Returns:
            BaseModel: 검증된 Pydantic 모델 인스턴스
        """
        try:
            # Pydantic으로 직접 검증 (더 강력함)
            validated_model = model_class.model_validate(data)
            logger.debug(f"✅ {context_name} Schema validation success")
            return validated_model
            
        except Exception as e:
            logger.error(f"❌ {context_name} Schema validation failed: {e}")
            
            # 기본값으로 모델 생성 시도
            try:
                default_model = model_class()
                logger.warning(f"⚠️ {context_name} Using default model")
                return default_model
            except Exception as default_error:
                logger.error(f"❌ {context_name} Default model creation also failed: {default_error}")
                raise
    
    @staticmethod
    def get_output_key(model_class: Type[BaseModel]) -> str:
        """
        모델 클래스에서 ADK output_key 생성
        
        Args:
            model_class: Pydantic 모델 클래스
            
        Returns:
            str: ADK output_key (예: "full_script_result")
        """
        class_name = model_class.__name__
        
        # 클래스명을 snake_case로 변환하고 _result 접미사 추가
        import re
        snake_case = re.sub('([A-Z]+)', r'_\1', class_name).lower().strip('_')
        output_key = f"{snake_case}_result"
        
        logger.debug(f"✅ {class_name} → output_key: {output_key}")
        return output_key


class ADKSchemaValidator:
    """
    ADK 스키마 검증 유틸리티
    """
    
    @staticmethod
    def validate_adk_schema(schema: Dict[str, Any]) -> bool:
        """
        ADK 스키마가 유효한지 검증
        
        Args:
            schema: 검증할 스키마
            
        Returns:
            bool: 유효성 여부
        """
        required_fields = ["type", "properties"]
        
        for field in required_fields:
            if field not in schema:
                logger.error(f"❌ ADK 스키마에 필수 필드 누락: {field}")
                return False
        
        if schema["type"] != "object":
            logger.error(f"❌ ADK 스키마는 type='object'여야 함: {schema['type']}")
            return False
        
        logger.debug("✅ ADK 스키마 검증 통과")
        return True
    
    @staticmethod
    def test_schema_conversion(model_class: Type[BaseModel]) -> Dict[str, Any]:
        """
        스키마 변환 테스트
        
        Args:
            model_class: 테스트할 Pydantic 모델
            
        Returns:
            Dict: 테스트 결과
        """
        try:
            # 스키마 변환
            adk_schema = PydanticToADKSchema.convert_model_to_schema(model_class)
            
            # 검증
            is_valid = ADKSchemaValidator.validate_adk_schema(adk_schema)
            
            # output_key 생성
            output_key = PydanticToADKSchema.get_output_key(model_class)
            
            return {
                "model_class": model_class.__name__,
                "schema_valid": is_valid,
                "output_key": output_key,
                "schema_size": len(json.dumps(adk_schema)),
                "properties_count": len(adk_schema.get("properties", {})),
                "required_fields": len(adk_schema.get("required", []))
            }
            
        except Exception as e:
            return {
                "model_class": model_class.__name__,
                "error": str(e),
                "schema_valid": False
            }
