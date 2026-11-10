# rembg-product-poc

제품 사진의 배경을 AI로 제거하고 **투명 PNG(RGBA)** 로 저장하는 가벼운 CLI 프로토타입입니다.
[`rembg`](https://github.com/danielgatis/rembg)를 감싼 것으로, 저장소를 clone한 뒤 명령 몇 줄이면 로컬에서 바로 누끼 테스트를 해볼 수 있습니다.

> A small CLI that removes image backgrounds and outputs transparent PNGs, built on `rembg`.
> Clone, install, run — see [Quick start](#빠른-시작).

- GPU 없이 CPU만으로 동작합니다 (이미지 1장 약 4~5초, Apple Silicon 기준 `birefnet-general-lite`).
- 단일 이미지와 폴더 일괄 처리를 지원합니다.
- 여러 모델을 옵션(`-m`)으로 바꿔 품질을 비교할 수 있습니다.

---

## 빠른 시작

### 1. 준비물

- Python 3.10 이상 (개발·검증 환경: Python 3.14)
- 인터넷 연결 (최초 실행 시 모델 가중치를 자동으로 내려받습니다)
- 디스크 여유 공간 약 1GB (모델에 따라 다름)

### 2. 설치

```bash
git clone https://github.com/jangyu-hong-dt/rembg-product-poc.git
cd rembg-product-poc

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 실행

본인이 가진 이미지 한 장으로 바로 테스트하세요.

```bash
python remove_bg.py -i my_product.jpg
```

- 결과는 입력 파일과 같은 폴더에 `my_product_nobg.png`로 저장됩니다.
- **최초 실행 시** 모델 파일(약 214MB)을 `~/.u2net/`에 내려받으므로 첫 실행만 시간이 더 걸립니다. 이후에는 캐시를 사용합니다.

> 이 저장소에는 테스트용 이미지가 들어 있지 않습니다. 저작권이 확실한 본인 이미지를 사용하세요.

---

## 사용법

```text
python remove_bg.py -i <입력> [-o <출력>] [-m <모델>] [--alpha-matting]
```

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `-i`, `--input` | 입력 이미지 파일 또는 이미지가 들어 있는 폴더 (필수) | - |
| `-o`, `--output` | 출력 PNG 경로 또는 저장 폴더 | `<입력이름>_nobg.png` (폴더 입력 시 `<입력폴더>/output_nobg/`) |
| `-m`, `--model` | 사용할 모델 (아래 표 참고) | `birefnet-general-lite` |
| `--alpha-matting` | 가장자리를 더 부드럽게 다듬는 알파 매팅 | 꺼짐 |

### 예시

```bash
# 단일 이미지 (기본 모델)
python remove_bg.py -i my_product.jpg

# 출력 경로 지정
python remove_bg.py -i my_product.jpg -o out/result.png

# 폴더 일괄 처리
python remove_bg.py -i ./my_images/ -o ./results/

# 최고 품질 모델로 처리
python remove_bg.py -i my_product.jpg -m birefnet-general

# 털, 반투명 소재 등 경계가 복잡한 경우 알파 매팅
python remove_bg.py -i my_product.jpg --alpha-matting
```

지원 입력 형식: `.jpg` `.jpeg` `.png` `.webp` `.bmp` `.tiff`

---

## 모델과 라이선스

| 모델 (`-m`) | 크기 | 특징 | 모델 라이선스 |
|---|---|---|---|
| `birefnet-general-lite` | 약 214MB | **기본값**. 빠르고 품질이 좋음 | MIT (BiRefNet) |
| `birefnet-general` | 약 928MB | 디테일 보존 최고 품질, 느림 | MIT (BiRefNet) |
| `isnet-general-use` | 약 170MB | 범용 IS-Net | Apache 2.0 |
| `u2net` | 약 170MB | 고전 기본 모델, 가장 가벼움 | Apache 2.0 |
| `bria-rmbg` | 약 977MB | 이커머스·제품 특화 (BRIA RMBG) | **비상업 (CC BY-NC)** |

> ⚠️ **상업적 용도로 사용하려면 `bria-rmbg`는 BRIA와 별도 계약이 필요합니다.** 다른 모델은 상업 사용이 가능하지만, 모델 가중치를 실제로 받는 출처의 라이선스를 사용 전에 직접 확인하세요.
> 모델 정보는 작성 시점 기준이며, 각 프로젝트의 최신 라이선스가 우선합니다.

이 저장소의 코드는 [MIT License](LICENSE)입니다.

---

## 품질을 높이는 팁

- 가장자리에 배경색이 번져 보이면(예: 붉은 배경의 제품이 가장자리만 붉게 보임) `--alpha-matting`을 켜 보세요. 이 번짐은 원본 사진의 색 반사라서 모델이 완전히 해결하지는 못합니다.
- 처음에는 기본 모델(`birefnet-general-lite`)로 충분한지 확인하고, 부족할 때만 `birefnet-general`로 올리세요.
- 유리·투명 용기, 머리카락·레이스 같은 얇은 디테일, 배경과 색이 비슷한 제품은 어느 모델이든 결과를 눈으로 확인하는 것이 좋습니다.

---

## 문제 해결

| 증상 | 해결 |
|---|---|
| 첫 실행이 오래 걸림 | 모델을 내려받는 중입니다. 완료되면 `~/.u2net/`에 캐시됩니다. |
| `ModuleNotFoundError` | 가상환경을 활성화했는지(`source .venv/bin/activate`), `pip install -r requirements.txt`를 실행했는지 확인하세요. |
| 모델 다운로드 실패 | 네트워크·프록시 환경을 확인하고 다시 실행하세요. |
| 처리가 느림 | CPU 연산이라 이미지 크기·모델에 비례합니다. 더 가벼운 `-m u2net` 또는 기본 `birefnet-general-lite`를 써 보세요. |

---

## 의존성

`rembg`, `onnxruntime`, `Pillow` ([requirements.txt](requirements.txt))
