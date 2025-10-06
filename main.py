#!/usr/bin/env python3
"""
PyQt6 애플리케이션 메인 런처
"""
import sys
import os

# stdout을 unbuffered로 설정 (Windows GUI 모드에서는 None일 수 있음)
if sys.stdout is not None and hasattr(sys.stdout, 'fileno'):
    try:
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
    except (AttributeError, OSError):
        pass  # GUI 모드에서는 stdout이 없을 수 있음

if sys.stderr is not None and hasattr(sys.stderr, 'fileno'):
    try:
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)
    except (AttributeError, OSError):
        pass  # GUI 모드에서는 stderr이 없을 수 있음

# src 디렉토리를 Python 경로에 추가
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

if __name__ == '__main__':
    # 디버그 모드 확인 (stdout이 있을 때만)
    if sys.stdout is not None:
        print("=== 프로그램 시작 ===", flush=True)
        print(f"Python version: {sys.version}", flush=True)
        print(f"stdout: {sys.stdout}", flush=True)

    from src.presentation.qt import main
    main()