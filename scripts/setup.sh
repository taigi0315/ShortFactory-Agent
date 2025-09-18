#!/bin/bash
# ShortFactory Agent 개발 환경 설정 스크립트

set -e  # 에러 발생 시 스크립트 중단

echo "🚀 ShortFactory Agent 개발 환경 설정 시작..."

# 1. Python 버전 확인
echo "1️⃣ Python 버전 확인..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python 버전: $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python 3.8 이상이 필요합니다. 현재 버전: $python_version"
    exit 1
fi

# 2. 가상 환경 생성 (선택사항)
if [ "$1" = "--venv" ]; then
    echo "2️⃣ 가상 환경 생성..."
    python3 -m venv venv
    source venv/bin/activate
    echo "   ✅ 가상 환경 활성화됨"
fi

# 3. 의존성 설치
echo "3️⃣ 프로덕션 의존성 설치..."
pip install -r requirements.txt

echo "4️⃣ 개발 의존성 설치..."
pip install -r requirements-dev.txt

# 4. 환경 변수 파일 확인
echo "5️⃣ 환경 변수 설정 확인..."
if [ ! -f ".env" ]; then
    echo "   ⚠️ .env 파일이 없습니다. 템플릿을 생성합니다..."
    cat > .env << EOF
# ShortFactory Agent API Keys
GEMINI_API_KEY=your-gemini-api-key-here
LEMONFOX_API_KEY=your-lemonfox-api-key-here
LEMONFOX_VOICE=sarah

# Optional: Stability AI for real image generation
STABILITY_API_KEY=your-stability-ai-key-here

# Optional: ElevenLabs (more expensive than LemonFox)
# ELEVENLABS_API_KEY=your-elevenlabs-key
# ELEVENLABS_VOICE_ID=your-voice-id
EOF
    echo "   📝 .env 템플릿이 생성되었습니다. API 키를 설정해주세요."
else
    echo "   ✅ .env 파일이 존재합니다."
fi

# 5. FFmpeg 확인
echo "6️⃣ FFmpeg 설치 확인..."
if command -v ffmpeg >/dev/null 2>&1; then
    ffmpeg_version=$(ffmpeg -version 2>&1 | head -n1 | awk '{print $3}')
    echo "   ✅ FFmpeg 설치됨: $ffmpeg_version"
else
    echo "   ⚠️ FFmpeg가 설치되지 않았습니다."
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt install ffmpeg"
    echo "   Windows: https://ffmpeg.org/download.html"
fi

# 6. 디렉토리 구조 확인
echo "7️⃣ 디렉토리 구조 확인..."
mkdir -p sessions
mkdir -p logs
echo "   ✅ 필수 디렉토리 생성됨"

# 7. 테스트 실행
echo "8️⃣ 기본 테스트 실행..."
if python -m pytest tests/unit/test_enhanced_response_models.py -v --tb=short; then
    echo "   ✅ 기본 테스트 통과"
else
    echo "   ⚠️ 일부 테스트 실패 - 확인이 필요합니다"
fi

echo ""
echo "🎉 설정 완료!"
echo ""
echo "📋 다음 단계:"
echo "   1. .env 파일에 API 키 설정"
echo "   2. 테스트 실행: python run_shortfactory.py --test --cost"
echo "   3. 실제 사용: python run_shortfactory.py \"Your Topic\" --cost"
echo ""
echo "📚 문서:"
echo "   - docs/AGENT-ROLES-GUIDE.md - 에이전트 역할 가이드"
echo "   - docs/TECHNICAL-REFACTORING-TASKS.md - 기술 개선 계획"
echo ""
