pythonimport anthropic
import json
import os
import sys
from datetime import datetime

today = datetime.now().strftime("%Y년 %m월 %d일")

# 주말 체크 (토=5, 일=6)
weekday = datetime.now().weekday()
if weekday >= 5:
    briefing = {
        "date": today,
        "content": "오늘은 쉬어요 ☕\n\n주말에는 시장이 열리지 않아요.\n월요일에 다시 만나요.",
        "updated": datetime.now().strftime("%H:%M"),
        "is_weekend": True
    }
    with open("briefing.json", "w", encoding="utf-8") as f:
        json.dump(briefing, f, ensure_ascii=False, indent=2)
    print("주말 — 브리핑 스킵")
    sys.exit(0)

# 평일만 실행
client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

SYSTEM_PROMPT = """
너는 한국 주식 투자자를 위한 거시경제 및 시장 브리핑 전문가야.
매일 아침 다음 항목들을 반드시 웹서치로 실시간 데이터를 확인하고 브리핑해.

[체크 항목]
1. 세계 정세 (이란 협상 동향, 지정학 리스크)
2. 코스피·코스닥 지수 및 등락률
3. 미장 지수 (S&P500, 나스닥, 필라델피아반도체지수)
4. KS200 선물 외인 포지션 및 베이시스
5. 미국 10년물·30년물 국채 금리
6. WTI·브렌트유
7. 원·달러 환율 및 달러 인덱스
8. 삼성전자·SK하이닉스 레버리지 ETF 수급 (전날 변동 클 때)
9. 국민연금 리밸런싱 동향 (주 1회)

[보유 포트폴리오]
- 삼성전자 4주, 삼성전자우 4주
- KODEX 200 30주
- 현대건설 4주
- 한화에어로스페이스 2주
- 한화시스템 15주
- TIGER 코리아AI전력기기TOP3플러스 90주
- SOL 한국원자력SMR 10주
- TIGER 코리아원자력 40주
- 버크셔 해서웨이 B 0.3956주
- 예수금 약 210만원

[브리핑 규칙]
- 두괄식: 결론 먼저, 설명은 뒤에
- 비판적 시각 유지, 과도한 낙관 금지
- 각 항목이 포트폴리오에 미치는 영향 명시
- 한독은 절대 언급하지 말 것
- 마지막에 "오늘 핵심 한 줄"로 요약
- 투자 조언 아닌 정보 제공임을 마지막에 명시
"""

BRIEFING_PROMPT = f"""
오늘({today}) 기준 실시간 데이터를 웹서치로 확인하고 브리핑해줘.

다음 형식으로 작성:

**① 🌍 세계 정세**
내용

**② 📈 한국 증시 (코스피·코스닥)**
내용

**③ 📊 미장 지수 & 선물**
- S&P500, 나스닥, 필라델피아반도체지수
- KS200 선물 외인 포지션

**④ 💸 금리·환율·유가**
- 미국 10년물·30년물 국채 금리
- WTI·브렌트유
- 원·달러 환율, 달러 인덱스

**⑤ 💼 포트폴리오 영향**
보유 종목별 오늘 방향 간략히

**⚡ 오늘 핵심 한 줄**
한 줄 요약

> ⚠️ 투자 조언 아닙니다.
"""

def run_briefing():
    messages = [{"role": "user", "content": BRIEFING_PROMPT}]
    tools = [{"type": "web_search_20250305", "name": "web_search"}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        messages.append({
            "role": "assistant",
            "content": response.content
        })

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": ""
                })

        messages.append({
            "role": "user",
            "content": tool_results
        })

    full_text = "\n".join(
        block.text for block in response.content
        if hasattr(block, "text")
    )

    return full_text


briefing_content = run_briefing()

briefing = {
    "date": today,
    "content": briefing_content,
    "updated": datetime.now().strftime("%H:%M"),
    "is_weekend": False
}

with open("briefing.json", "w", encoding="utf-8") as f:
    json.dump(briefing, f, ensure_ascii=False, indent=2)

print(f"✅ 브리핑 생성 완료 ({briefing['updated']})")
print("=" * 50)
print(briefing_content)
