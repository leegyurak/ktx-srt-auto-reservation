#!/usr/bin/env python3
"""
크로스 플랫폼 빌드 스크립트
Windows와 macOS 모두에서 사용 가능
"""
import sys
import os
import subprocess
import shutil

def main():
    print("=== KTX/SRT Macro 빌드 시작 ===")
    print(f"플랫폼: {sys.platform}")

    # 플랫폼에 따라 출력 디렉토리 결정
    if sys.platform == 'darwin':
        dist_dir = 'build/mac'
        platform_name = 'macOS'
    elif sys.platform == 'win32':
        dist_dir = 'build/windows'
        platform_name = 'Windows'
    else:
        dist_dir = 'build/linux'
        platform_name = 'Linux'

    # 이전 빌드 결과 삭제
    print("이전 빌드 결과 삭제 중...")
    for dir_path in [dist_dir, 'build/temp', 'dist']:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    # PyInstaller로 빌드
    print(f"PyInstaller로 빌드 중 ({platform_name})...")
    subprocess.run([
        "pyinstaller",
        "--distpath", dist_dir,
        "--workpath", "build/temp",
        "build.spec"
    ], check=True)

    # 빌드 결과 확인
    print("\n=== 빌드 성공! ===")
    print(f"빌드된 파일 위치: {dist_dir}/")

    # 디렉토리 내용 출력
    if os.path.exists(dist_dir):
        print("\n파일 목록:")
        for item in os.listdir(dist_dir):
            item_path = os.path.join(dist_dir, item)
            size = os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            print(f"  - {item} ({size:,} bytes)" if size > 0 else f"  - {item}/")

if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\n=== 빌드 실패 ===")
        print(f"오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n=== 빌드 실패 ===")
        print(f"예상치 못한 오류: {e}")
        sys.exit(1)
