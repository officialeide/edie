pythonimport anthropic
import json
import os
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

today = datetime.now().strftime("%Y년 %m월 %d일")

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1500,
    messages=[{
        "role": "user",
        "content": f"""오늘({today}) 기준 한국 경제 브리핑을 작성해줘.
        
형식:
**[주제1 제목]**
내용 2~3문장

**[주제2 제목]**
내용 2~3문장

**[주제3 제목]**
내용 2~3문장

**[주제4 제목]**
내용 2~3문장

주요 분야: 환율, 주식시장, 부동산, 국내외 경제 이슈"""
    }]
)

briefing = {
    "date": today,
    "content": message.content[0].text,
    "updated": datetime.now().strftime("%H:%M")
}

with open("briefing.json", "w", encoding="utf-8") as f:
    json.dump(briefing, f, ensure_ascii=False, indent=2)

print("브리핑 생성 완료")
print(briefing["content"][:200])
