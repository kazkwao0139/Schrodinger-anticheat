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

**TTS Detection**: A working TTS detector already exists and has been cross-validated multiple times against real human voice recordings and Google TTS. However, packaging it as a binary distribution is not feasible at this time due to heavy dependencies (numpy, scipy, librosa).

Other areas — such as RF IFF (Identification Friend or Foe), tamper-proof verification, and voice fingerprinting — are theoretically feasible and currently working in simulation.

## License

All rights reserved.

This software is proprietary. No part of this software may be reproduced, distributed, modified, or used in any form without prior written permission from the author.

Reverse engineering, decompilation, and disassembly of the binary components are strictly prohibited.

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

**TTS 탐지**: TTS 탐지 프로그램은 이미 작동하며, 실제 인간 음성 녹음과 Google TTS를 대상으로 여러 차례 교차 검증을 통해 작동이 확인되었습니다. 다만 numpy, scipy, librosa 등 무거운 의존성 때문에 바이너리 파일로 제공하기는 현재로서 어렵습니다.

RF IFF(피아식별), 변조 방지, 음성 지문 등 다른 분야도 이론적으로는 적용 가능하며, 현재 시뮬레이션 단계에서 동작합니다.

## 라이선스

All rights reserved.

이 소프트웨어는 독점 소프트웨어입니다. 저작자의 사전 서면 동의 없이 본 소프트웨어의 어떠한 부분도 복제, 배포, 수정 또는 사용할 수 없습니다.

바이너리 구성 요소에 대한 역공학, 디컴파일, 디스어셈블리는 엄격히 금지됩니다.
