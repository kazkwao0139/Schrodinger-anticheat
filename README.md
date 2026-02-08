# Schrodinger Anti-Cheat

Mouse trajectory-based aimbot detection system.

## Overview

Schrodinger analyzes mouse movement patterns in real-time to detect aimbot cheating. The core engine processes cursor trajectory data and flags anomalous movement that deviates from natural human behavior.

## Detection Coverage

| Type | Status | Note |
|------|--------|------|
| Aimlock | Detected | Instant cursor teleport to target |
| Snap | Detected | Fast cursor animation to target |
| Smooth | Theoretically detectable | Not implemented in demo due to pygame limitations |
| Silent | Server-side recommended | Cursor stays in place while hits register at target — requires server-side hit validation |

## Current Limitations

This is a working proof-of-concept, not a production-ready solution. The detection theory is sound, but the following areas need further tuning:

- Threshold calibration across different screen resolutions
- Tick rate sensitivity adjustments
- Edge case handling for extreme mouse DPI / sensitivity settings

## Demo

Interactive Pygame demo with built-in cheat simulations for testing.

### Requirements

- Python 3.10+
- Pygame 2.x

### Controls

| Key | Action |
|-----|--------|
| TAB | Toggle Normal / Aimbot mode |
| SPACE | Start / Stop challenge |
| 1 / 2 / 3 | Select aim type (Silent / Aimlock / Snap) |
| T / 5 | Toggle Triggerbot |
| Scroll | Adjust aim FOV |
| F1 / F2 | Tick rate -/+ |
| R | Reset |
| ESC | Quit |

## Structure

- `schrodinger_core.pyd` — Detection engine (binary)
- `schrodinger_demo.py` — Interactive demo

## Beyond Anti-Cheat

The Schrodinger engine is applicable to any domain that requires distinguishing human from machine behavior.

**TTS/Deepfake Voice Detection**: The TTS detector (v5) achieves 100% accuracy on a test set of 40 human speakers (LibriSpeech dev-clean, ~480s per speaker) + 21 TTS samples (Google TTS, Microsoft Edge TTS across 7 languages). 0% false positive rate on human speech. Packaging as a binary distribution is not feasible at this time due to heavy dependencies (numpy, scipy).

Other areas — such as RF IFF (Identification Friend or Foe), tamper-proof verification, and voice fingerprinting — are theoretically feasible and currently working in simulation.

## License

All rights reserved.

This software is proprietary. No part of this software may be reproduced, distributed, modified, or used in any form without prior written permission from the author.

Reverse engineering, decompilation, and disassembly of the binary components are strictly prohibited.

I would like to open-source the detection logic, but due to the nature of anti-cheat and security systems, I am unable to do so. I appreciate your understanding.

---

# Schrodinger Anti-Cheat (한국어)

마우스 궤적 기반 에임핵 탐지 시스템.

## 개요

Schrodinger는 마우스 움직임 패턴을 실시간으로 분석하여 에임핵 치팅을 탐지합니다. 커서 궤적 데이터를 처리하여 자연스러운 인간의 움직임에서 벗어나는 이상 움직임을 감지합니다.

## 탐지 범위

| 유형 | 상태 | 비고 |
|------|------|------|
| Aimlock | 탐지됨 | 커서가 타겟으로 즉시 이동 |
| Snap | 탐지됨 | 커서가 타겟으로 빠르게 애니메이션 이동 |
| Smooth | 이론상 탐지 가능 | pygame 데모 한계로 미구현 |
| Silent | 서버사이드 권장 | 커서는 제자리, 히트는 타겟에 등록 — 서버측 히트 검증 필요 |

## 현재 한계

동작하는 개념 증명(PoC) 단계이며, 프로덕션 수준은 아닙니다. 탐지 이론은 유효하나 다음 항목의 추가 조정이 필요합니다:

- 다양한 화면 해상도에 따른 임계값 보정
- 틱레이트 민감도 조정
- 극단적인 마우스 DPI / 감도 설정에 대한 예외 처리

## 데모

에임핵 시뮬레이션이 내장된 Pygame 인터랙티브 데모.

### 요구사항

- Python 3.10+
- Pygame 2.x

### 조작법

| 키 | 동작 |
|----|------|
| TAB | Normal / Aimbot 모드 전환 |
| SPACE | 챌린지 시작 / 종료 |
| 1 / 2 / 3 | 에임 유형 선택 (Silent / Aimlock / Snap) |
| T / 5 | 트리거봇 토글 |
| Scroll | 에임 FOV 조절 |
| F1 / F2 | 틱레이트 -/+ |
| R | 리셋 |
| ESC | 종료 |

## 구조

- `schrodinger_core.pyd` — 탐지 엔진 (바이너리)
- `schrodinger_demo.py` — 인터랙티브 데모

## 안티치트를 넘어서

Schrodinger 엔진은 인간과 기계를 구별해야 하는 모든 분야에 적용 가능합니다.

**TTS/딥페이크 음성 탐지**: TTS 탐지기(v5)는 40명의 인간 화자(LibriSpeech dev-clean, 화자당 ~480초) + 21개 TTS 샘플(Google TTS, Microsoft Edge TTS, 7개 언어)로 구성된 테스트셋에서 100% 정확도를 달성했습니다. 인간 음성 오탐률 0%. 대수의 법칙에 의해 오디오가 길수록 탐지 안정성이 높아지며, 짧은 클립(<5초)에서는 불안정할 수 있습니다. 이 수렴은 TTS에도 동일하게 적용되어, 긴 TTS 오디오는 더 확실하게 TTS로 수렴합니다 (50초 gTTS, 40초 Edge TTS 검증 완료). 전화 통화 등 연속 음성 스트림 환경에 최적화되어 있습니다. numpy, scipy 등 무거운 의존성 때문에 바이너리 파일로 제공하기는 현재로서 어렵습니다.

RF IFF(피아식별), 변조 방지, 음성 지문 등 다른 분야도 이론적으로는 적용 가능하며, 현재 시뮬레이션 단계에서 동작합니다.

## 라이선스

All rights reserved.

이 소프트웨어는 독점 소프트웨어입니다. 저작자의 사전 서면 동의 없이 본 소프트웨어의 어떠한 부분도 복제, 배포, 수정 또는 사용할 수 없습니다.

바이너리 구성 요소에 대한 역공학, 디컴파일, 디스어셈블리는 엄격히 금지됩니다.

로직을 공개하고 싶지만, 안티치트와 보안이라는 특성상 공개할 수 없음을 양해 부탁드립니다.

## Changelog

### TTS Detector v5 (2026-02-08)
- 100% accuracy on 40 human speakers + 21 TTS samples (61/61)
- 0% false positive rate on human speech
- Tested against: Google TTS, Microsoft Edge TTS (7 languages, 12 voices), Windows SAPI5
- Human data: LibriSpeech dev-clean (40 speakers, ~480s per speaker)
- Law of Large Numbers: detection reliability scales with audio length. Short clips (<5s) may produce unstable results. The detector is designed for continuous voice streams (e.g. phone calls), not short utterances. This convergence applies equally to TTS — longer TTS audio converges more reliably to TTS, not toward human. Verified with 50s gTTS and 40s Edge TTS concatenations.

### TTS Detector v4 (2025)
- Initial detection approach
- 75.6% accuracy on mixed test set

### Anti-Cheat v1
- Mouse trajectory analysis for aimbot detection

---

## TTS Detector v5 — Test Log (2026-02-08)

Threshold: 0.28 | Score >= threshold → HUMAN, Score < threshold → TTS/AI

### Human Speech (LibriSpeech dev-clean, 40 speakers)

| # | Speaker | Duration | Anomaly Score | Verdict |
|---|---------|----------|---------------|---------|
| 1 | spk84 | 481.2s | 0.4509 | HUMAN |
| 2 | spk174 | 482.6s | 0.8924 | HUMAN |
| 3 | spk251 | 482.2s | 0.5102 | HUMAN |
| 4 | spk422 | 503.0s | 1.1151 | HUMAN |
| 5 | spk652 | 498.6s | 1.5129 | HUMAN |
| 6 | spk777 | 483.7s | 0.8171 | HUMAN |
| 7 | spk1272 | 481.0s | 0.5719 | HUMAN |
| 8 | spk1462 | 482.2s | 0.3035 | HUMAN |
| 9 | spk1673 | 484.0s | 0.5429 | HUMAN |
| 10 | spk1919 | 490.2s | 0.2893 | HUMAN |
| 11 | spk1988 | 489.4s | 0.5493 | HUMAN |
| 12 | spk1993 | 486.8s | 0.5551 | HUMAN |
| 13 | spk2035 | 486.3s | 0.5288 | HUMAN |
| 14 | spk2078 | 481.8s | 0.5868 | HUMAN |
| 15 | spk2086 | 482.4s | 0.6782 | HUMAN |
| 16 | spk2277 | 480.5s | 0.3483 | HUMAN |
| 17 | spk2412 | 483.9s | 0.4411 | HUMAN |
| 18 | spk2428 | 481.0s | 0.7900 | HUMAN |
| 19 | spk2803 | 491.9s | 0.7445 | HUMAN |
| 20 | spk2902 | 485.7s | 0.7503 | HUMAN |
| 21 | spk3000 | 482.1s | 0.9202 | HUMAN |
| 22 | spk3081 | 480.2s | 1.0248 | HUMAN |
| 23 | spk3170 | 485.8s | 0.7134 | HUMAN |
| 24 | spk3536 | 488.9s | 0.6260 | HUMAN |
| 25 | spk3576 | 480.1s | 0.7559 | HUMAN |
| 26 | spk3752 | 483.6s | 0.8498 | HUMAN |
| 27 | spk3853 | 482.9s | 0.4411 | HUMAN |
| 28 | spk5338 | 484.1s | 0.6589 | HUMAN |
| 29 | spk5536 | 487.9s | 0.5775 | HUMAN |
| 30 | spk5694 | 480.6s | 0.4518 | HUMAN |
| 31 | spk5895 | 481.3s | 0.3295 | HUMAN |
| 32 | spk6241 | 482.9s | 0.8855 | HUMAN |
| 33 | spk6295 | 482.3s | 0.9153 | HUMAN |
| 34 | spk6313 | 490.2s | 0.7595 | HUMAN |
| 35 | spk6319 | 480.5s | 0.2855 | HUMAN |
| 36 | spk6345 | 484.4s | 0.6085 | HUMAN |
| 37 | spk7850 | 483.6s | 0.6467 | HUMAN |
| 38 | spk7976 | 487.9s | 0.5958 | HUMAN |
| 39 | spk8297 | 482.6s | 0.6020 | HUMAN |
| 40 | spk8842 | 485.9s | 0.9415 | HUMAN |

### TTS / AI Speech (Google TTS + Microsoft Edge TTS)

| # | Source | Duration | Anomaly Score | Verdict |
|---|--------|----------|---------------|---------|
| 1 | gTTS (ko) | 6.3s | 0.2348 | TTS/AI |
| 2 | gTTS (ko) | 6.3s | 0.2280 | TTS/AI |
| 3 | gTTS (en) | 4.9s | 0.2560 | TTS/AI |
| 4 | gTTS (en) | 5.5s | 0.1799 | TTS/AI |
| 5 | gTTS (ja) | 6.1s | 0.2376 | TTS/AI |
| 6 | gTTS (zh-CN) | 5.9s | 0.1754 | TTS/AI |
| 7 | gTTS (es) | 5.4s | 0.1446 | TTS/AI |
| 8 | gTTS (fr) | 4.4s | 0.1935 | TTS/AI |
| 9 | gTTS (de) | 5.1s | 0.2636 | TTS/AI |
| 10 | EdgeTTS (ko-F) | 4.1s | 0.2400 | TTS/AI |
| 11 | EdgeTTS (ko-M) | 3.6s | 0.0878 | TTS/AI |
| 12 | EdgeTTS (en-US-F) | 3.2s | 0.0585 | TTS/AI |
| 13 | EdgeTTS (en-US-M) | 2.8s | 0.1354 | TTS/AI |
| 14 | EdgeTTS (en-GB-F) | 2.8s | 0.1799 | TTS/AI |
| 15 | EdgeTTS (ja-F) | 3.9s | 0.1051 | TTS/AI |
| 16 | EdgeTTS (ja-M) | 3.3s | 0.2495 | TTS/AI |
| 17 | EdgeTTS (zh-F) | 2.6s | 0.1937 | TTS/AI |
| 18 | EdgeTTS (zh-M) | 3.7s | 0.0599 | TTS/AI |
| 19 | EdgeTTS (es-F) | 3.0s | 0.1104 | TTS/AI |
| 20 | EdgeTTS (fr-F) | 3.2s | 0.1881 | TTS/AI |
| 21 | EdgeTTS (de-F) | 3.5s | 0.1504 | TTS/AI |

### Summary

```
Human  anomaly_score:  min=0.2855  max=1.5129  mean=0.6642  (n=40)
TTS    anomaly_score:  min=0.0585  max=0.2636  mean=0.1749  (n=21)
Gap (Human min - TTS max): 0.0219
Accuracy: 61/61 (100.0%)
```
