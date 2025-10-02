#!/usr/bin/env python3
"""
PyQt6 애플리케이션 메인 런처
"""
import sys
import os

# stdout을 unbuffered로 설정
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

# src 디렉토리를 Python 경로에 추가
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

if __name__ == '__main__':
    # 디버그 모드 확인
    print("=== 프로그램 시작 ===", flush=True)
    print(f"Python version: {sys.version}", flush=True)
    print(f"stdout: {sys.stdout}", flush=True)

    from src.presentation.qt import main
    main()