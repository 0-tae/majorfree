import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc
import platform

# 운영체제별 한글 폰트 설정
if platform.system() == 'Windows':
    font_path = "C:/Windows/Fonts/malgun.ttf"
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font_name)
elif platform.system() == 'Darwin':  # macOS
    rc('font', family='AppleGothic')
else:  # Linux
    rc('font', family='NanumGothic')
    
plt.rcParams['axes.unicode_minus'] = False

# CSV 파일 읽기
df = pd.read_csv('자율전공학부 전공 탐색 지원 서비스 개발을 위한 설문조사(응답).csv', encoding='utf-8')

# 1. 전공 정보 수집 방법 분석
info_collection = df['현재 전공을 선택하기 위해 어떤 방법으로 정보를 수집하고 있나요? (복수 선택 가능)'].str.split(', ').explode().value_counts()
total_responses = len(df)
info_collection_pct = (info_collection / total_responses * 100).round(1).reset_index(drop=True)

plt.figure(figsize=(10, 6))
bars = plt.bar(range(len(info_collection)), info_collection)
plt.title('전공 정보 수집 방법')
plt.xlabel('수집 방법')
plt.ylabel('응답 수')

# 각 막대 위에 퍼센트 표시
for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{info_collection_pct.iloc[i]}%',
             ha='center', va='bottom')

plt.xticks(range(len(info_collection)), info_collection.index, rotation=45)
plt.tight_layout()
plt.show()

# 2. 만족도 분포
satisfaction = df['현재 학교에서 제공하는 전공 탐색 정보나 지원 제도 (설명회, 멘토링 등)에 만족하시나요?'].value_counts()
plt.figure(figsize=(8, 6))
plt.pie(satisfaction, labels=satisfaction.index, autopct='%1.1f%%')
plt.title('전공 탐색 정보/지원 제도 만족도')
plt.tight_layout()
plt.show()

# 3. 전공 선택 기준
selection_criteria = df['현재 어떤 기준으로 전공을 선택하였나요? (복수 선택 가능)'].str.split(', ').explode().value_counts()
selection_criteria_pct = (selection_criteria / total_responses * 100).round(1).reset_index(drop=True)

plt.figure(figsize=(12, 6))
bars = plt.bar(range(len(selection_criteria)), selection_criteria)
plt.title('전공 선택 기준')
plt.xlabel('선택 기준')
plt.ylabel('응답 수')

for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{selection_criteria_pct.iloc[i]}%',
             ha='center', va='bottom')

plt.xticks(range(len(selection_criteria)), selection_criteria.index, rotation=45)
plt.tight_layout()
plt.show()

# 4. 전공 탐색 시 어려운 점
difficulties = df['현재 전공 탐색 과정에서 어려운 점이 있다면 무엇인가요? (복수 선택 가능)'].str.split(', ').explode().value_counts()
difficulties_pct = (difficulties / total_responses * 100).round(1).reset_index(drop=True)

plt.figure(figsize=(12, 6))
bars = plt.bar(range(len(difficulties)), difficulties)
plt.title('전공 탐색 시 어려운 점')
plt.xlabel('어려운 점')
plt.ylabel('응답 수')

for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{difficulties_pct.iloc[i]}%',
             ha='center', va='bottom')

plt.xticks(range(len(difficulties)), difficulties.index, rotation=45)
plt.tight_layout()
plt.show()

# 5. AI 서비스 사용 의향
ai_interest = df['시간과 장소에 구애받지 않고 전공 탐색을 도와주는 생성형 AI 가이드 서비스가 있다면 사용해보고 싶나요?'].value_counts().sort_index()
ai_interest_pct = (ai_interest / total_responses * 100).round(1).reset_index(drop=True)

plt.figure(figsize=(8, 6))
bars = plt.bar(range(len(ai_interest)), ai_interest)
plt.title('AI 가이드 서비스 사용 의향')
plt.xlabel('응답 (1-5)')
plt.ylabel('응답 수')

for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{ai_interest_pct.iloc[i]}%',
             ha='center', va='bottom')

plt.xticks(range(len(ai_interest)), ai_interest.index)
plt.tight_layout()
plt.show()

# 6. 전공 탐색을 위해 강의 수강 경험
lecture_experience = df['전공 적합성 탐색을 위해 직접 강의를 수강해본 경험이 있나요?'].value_counts()
lecture_experience_pct = (lecture_experience / total_responses * 100).round(1)

plt.figure(figsize=(8, 6))
plt.pie(lecture_experience, labels=lecture_experience.index, autopct='%1.1f%%')
plt.title('전공 탐색을 위한 강의 수강 경험')
plt.tight_layout()
plt.show()

# 7. 원하지 않는 전공 발견 경험
wrong_major = df[df['전공 적합성 탐색을 위해 직접 강의를 수강해본 경험이 있나요?'] == '예']['만약 있다면 해당 강의를 수강한 뒤 내가 원하지 않거나 나와 맞지 않는 전공이라는 것을 깨달은 경험이 있나요?'].value_counts()
wrong_major_pct = (wrong_major / len(df[df['전공 적합성 탐색을 위해 직접 강의를 수강해본 경험이 있나요?'] == '예']) * 100).round(1)

plt.figure(figsize=(8, 6))
plt.pie(wrong_major, labels=wrong_major.index, autopct='%1.1f%%')
plt.title('수강 후 부적합 전공 발견 경험\n(강의 수강 경험자 대상)')
plt.tight_layout()
plt.show()

# 8. 기회비용 부담 경험
opportunity_cost = df[df['전공 적합성 탐색을 위해 직접 강의를 수강해본 경험이 있나요?'] == '예']['전공탐색을 위해 강의를 듣고나서 기회비용에(시간, 학점 낭비 등)에 대한 부담을 느낀 적이 있나요?'].value_counts()
opportunity_cost_pct = (opportunity_cost / len(df[df['전공 적합성 탐색을 위해 직접 강의를 수강해본 경험이 있나요?'] == '예']) * 100).round(1)

plt.figure(figsize=(8, 6))
plt.pie(opportunity_cost, labels=opportunity_cost.index, autopct='%1.1f%%')
plt.title('전공 탐색 강의 수강의 기회비용 부담\n(강의 수강 경험자 대상)')
plt.tight_layout()
plt.show()

# 9. 희망하는 전공 탐색 정보
desired_info = df['전공 탐색을 위해 어떤 정보를 가장 얻고 싶나요? (복수 선택 가능)'].str.split(', ').explode().value_counts()
desired_info_pct = (desired_info / total_responses * 100).round(1).reset_index(drop=True)

plt.figure(figsize=(12, 6))
bars = plt.bar(range(len(desired_info)), desired_info)
plt.title('희망하는 전공 탐색 정보')
plt.xlabel('정보 종류')
plt.ylabel('응답 수')

for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{desired_info_pct.iloc[i]}%',
             ha='center', va='bottom')

plt.xticks(range(len(desired_info)), desired_info.index, rotation=45)
plt.tight_layout()
plt.show()