#!/usr/bin/env python3
"""
배경 투명 누끼 제거 프로토타입 (rembg 기반)
BiRefNet, BRIA RMBG, U2Net 등 지원
"""

import argparse
import sys
import time
from pathlib import Path
from PIL import Image
from rembg import new_session, remove

SUPPORTED_MODELS = [
    "birefnet-general",
    "birefnet-general-lite",
    "bria-rmbg",
    "isnet-general-use",
    "u2net",
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def process_image(
    input_path: Path,
    output_path: Path,
    session,
    alpha_matting: bool = False,
):
    print(f"\n[작업 시작] {input_path.name} -> {output_path.name}")
    start_time = time.time()

    try:
        with Image.open(input_path) as img:
            # EXIF 회전 보정 및 RGB 변환
            img = img.convert("RGB")
            
            output = remove(
                img,
                session=session,
                alpha_matting=alpha_matting,
            )

            # 출력 디렉토리 확인 및 저장 (RGBA 투명 PNG)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output.save(output_path, format="PNG")

        elapsed = time.time() - start_time
        print(f"[완료] 저장 위치: {output_path} (소요 시간: {elapsed:.2f}초)")
        return True
    except Exception as e:
        print(f"[오류 발생] {input_path}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="제품 이미지 배경 제거 (누끼 따기) 프로토타입",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="입력 이미지 경로 또는 이미지가 들어있는 폴더 경로",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="출력 PNG 경로 또는 저장 폴더 경로 (기본값: input파일명_nobg.png)",
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        choices=SUPPORTED_MODELS,
        default="birefnet-general-lite",
        help="사용할 배경 제거 AI 모델",
    )
    parser.add_argument(
        "--alpha-matting",
        action="store_true",
        help="알파 매팅(경계선 미세 다듬기) 활성화",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"오류: 입력 경로 '{input_path}'를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    print(f"==================================================")
    print(f" [AI 배경 제거 프로토타입] ")
    print(f" - 선택 모델: {args.model}")
    print(f" - 알파 매팅: {'활성화' if args.alpha_matting else '비활성화'}")
    print(f"==================================================")
    print(f"모델 세션을 초기화하고 가중치를 로드합니다 (최초 실행 시 다운로드 진행)...")
    
    init_start = time.time()
    session = new_session(model_name=args.model)
    print(f"세션 로드 완료 ({time.time() - init_start:.2f}초 소요)")

    if input_path.is_file():
        if args.output:
            out_p = Path(args.output)
            # 만약 out_p가 디렉토리이면 그 안에 원본이름_nobg.png로 저장
            if out_p.is_dir() or (not out_p.suffix and not out_p.exists()):
                output_file = out_p / f"{input_path.stem}_nobg.png"
            else:
                output_file = out_p
        else:
            output_file = input_path.with_name(f"{input_path.stem}_nobg.png")

        process_image(input_path, output_file, session, args.alpha_matting)

    elif input_path.is_dir():
        image_files = [
            p for p in input_path.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        ]

        if not image_files:
            print(f"지정한 디렉토리에 지원되는 이미지 파일이 없습니다: {input_path}")
            sys.exit(0)

        out_dir = Path(args.output) if args.output else (input_path / "output_nobg")
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"총 {len(image_files)}장의 이미지를 일괄 처리합니다. 출력 폴더: {out_dir}")

        success_count = 0
        for img_file in image_files:
            target_out = out_dir / f"{img_file.stem}_nobg.png"
            if process_image(img_file, target_out, session, args.alpha_matting):
                success_count += 1

        print(f"\n[일괄 처리 완료] 전체 {len(image_files)}개 중 {success_count}개 성공")


if __name__ == "__main__":
    main()
