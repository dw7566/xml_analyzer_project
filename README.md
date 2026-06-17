# XML Analyzer - Advanced Analysis

MZM 및 IV 커브 데이터를 분석하고 시각화하는 통합 GUI 애플리케이션입니다.
<img width="1045" height="736" alt="image" src="https://github.com/user-attachments/assets/0243242c-ec55-4afc-a7dd-82c6a0b21377" />


## 실행 방법
1. 필요 라이브러리 설치: `pip install -r requirements.txt`
2. 프로그램 실행: `python main.py`\n

# 프로젝트 소개 (Overview)
반도체 소자(Silicon Photonics, MZM 등) 측정 후 생성되는 대량의 XML 데이터에서 핵심 파라미터를 추출하고, 분석 및 시각화를 자동화하는 Python 기반 GUI 애플리케이션입니다.
수작업으로 진행되던 MZI Fitting 및 IV Curve 분석 과정을 자동화하여 데이터 처리 시간을 획기적으로 단축하고 분석의 정확도를 높였습니다.

# 🚀 핵심 기능 (Key Features)
1. 대용량 다중 파일 처리: 여러 개의 XML 파일을 한 번에 불러와 TestSite별 데이터를 통합 파싱

2. 자동화된 광학 분석 (Optical Analysis):

     Reference Spectrum (6차 다항식) 피팅 및 보정 처리

     MZI 모델 기반 커브 피팅(Curve Fitting) 및 타겟 파장(1550nm) 정규화

3. 전기적 특성 분석 (Electrical Analysis):

    -1.0V 및 1.0V 기준 특정 전압에서의 전류(I) 값 자동 추출

   다이오드 방정식(Diode Model) 및 다항식을 활용한 Advanced IV Fitting

   리포트 자동 생성: 추출된 주요 파라미터(Rsq, Max trans 등)를 취합하여 날짜별 디렉토리에 Excel(.xlsx) 포맷으로 자동 저장 (file_manager 모듈)

# 🛠️ 개발 및 문제 해결 전략 (Development Approach)
본 프로젝트는 도메인 지식과 최신 AI 도구를 결합한 'AI 페어 프로그래밍(Pair Programming)' 방식으로 개발되어 생산성과 코드 품질을 극대화했습니다.

1. 나의 핵심 역할 (Domain Logic & Architecture):

   수학적 모델링 설계: 광소자 특성에 맞는 mzi_model 방정식과 diode_model 수식을 직접 정의하고 초기 파라미터(Initial Guess) 설정.

   데이터 파이프라인 기획: 복잡한 XML 구조에서 필요한 태그(WavelengthSweep, IVMeasurement)를 식별하고, 최종 엑셀 리포트로 출력되기까지의 데이터 흐름 설계.

   트러블슈팅 및 검증: 다중 파일 병합 시 발생하는 예외 처리를 디버깅하고, 피팅된 그래프가 물리적 의미(Reference 일치 여부 등)에 부합하는지 교차 검증.

2. AI 도구 활용 (Efficiency & Implementation):

   Tkinter 기반의 복잡한 UI 레이아웃 및 Matplotlib 시각화 뼈대 등 반복적인 보일러플레이트(Boilerplate) 코드를 AI를 통해 신속하게 구현.

   유지보수성을 높이기 위해 하나의 스크립트였던 코드를 app.py, models.py, file_manager.py 등 객체지향적 모듈로 분리(Refactoring)하는 과정에서 AI의 설계 제안을 수용 및 적용.

# 💻 기술 스택 (Tech Stack)
Language: Python 3.x

GUI: Tkinter

Data Processing & Math: Pandas, NumPy, SciPy (curve_fit)

Visualization: Matplotlib
