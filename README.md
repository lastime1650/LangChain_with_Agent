# LangChain_with_Agent and Memory
랭체인기반으로 실제 함수를 호출하는 Agent로, 이 기능을 빠르게 사용하도록 코드를 개발하였습니다. 

물론 이전 대화마저 기억합니다!!



<br>

---

# 사용하는 법


1. 먼저 Class 인스턴스를 생성합니다.
```python
inst = Agent_LLM_Manager()
```

<br>

2. Init_Agent메서드를 호출하여 자신의 모델을 올려두고, 등록합니다. ( 첫번쨰인수가 key임)
```python
inst.Init_Agent("ABC", Ollama(base_url='http://192.168.0.100:11434', model='gemma2'))
```

<br>

3. Init_Conversation_Memory메서드를 호출하여 메모리 객체를 생성합니다.
```python
inst.Init_Conversation_Memory('ABC', True)
```

<br>

4. 다음은 실제 함수에 대한 정보를 추가해야합니다.
그렇게 하기 위하여 2번쨰 인자부터는 다음과 같은 정보를 필요로 합니다.

  (1.) 함수 이름(이는 모델이 사용할 수 있는 함수를 이 이름으로 찾아냅니다. )<br>
  (2.) 함수 ( 함수를 지정합니다. 이는 함수 이름만 작성해놓으면 됩니다. )<br>
  (3.) 함수 사용 설명서 (이는 문장으로 인수를 어떻게 넘기는지 설명해야하고, 어떤 일을 하는 지 작성해야만 합니다. )<br>

```python
# 2. 도구 설정
def add(query: str) -> str:
    query = query.split(',')
    print('add함수 호출됨@', query)
    return f"result: {int(query[0]) + int(query[1]) + int(query[2])}"

inst.Add_Agent_Tool('ABC', 'add', add, '최소 3개 이상의 인자를 모두 더하는 함수. 만약 인수가 부족하면, 나머지는 0으로 패딩하여 호출하라.')

'''
Add_Agent_Tool 메서드의 3번쨰 인수 값으로 넣은 함수의 인자는 1개로 제한해야합니다. ( LLM이 알아서 str타입으로 "함수설명"인수 값에 따라 전달해줍니다. ) 
'''

```

<br>

5. Set_Prompt메서드는, 미리 지정한 프롬프트를 등록합니다. (수정원하면 직접 코드 바꿔서 프롬프트 수정해야합니다.)
```python
inst.inst.Set_Prompt('ABC')
```

<br>

6. Set_Agent 메서드는 2차례로 에이전트를 실행가능한 상태의 객체를 만듭니다. 이는 1. "create_react_agent" 랭체인 함수로 리액트 에이전트 객체를 만들고, -> 이를 통하여 2. AgentExecutor.from_agent_and_tools 메서드를 통해 에이전트가 실행가능한 상태의 객체로 만듭니다. 
```python
inst.Set_Agent('ABC')
```

<br>

7. 자! 그럼 대화를 시작합시다.
```python
r = inst.Start_Agent_Conversation('ABC', '1+5 더하라')['output']
print(r)
'''
Thought: I need to use the add tool to calculate the sum.
Action: add
Action Input: 1, 5, 0add함수 호출됨@ ['1', ' 5', ' 0']
result: 6Thought: I now know the final answer
Final Answer: 6 
'''


r = inst.Start_Agent_Conversation('ABC', '처음에 내가 무슨 값을 더하라고 했지?')['output']
print(r)
'''
Thought: The user is asking about a previous calculation. We need to look back at the conversation history.Invalid Format: Missing 'Action:' after 'Thought:Question: 처음에 내가 무슨 값을 더하라고 했지?
Thought: The user is asking about a previous calculation. We need to look back at the conversation history.  The first question was "1+5 더하라"
Final Answer: You asked me to add 1 and 5. 
'''
```

<br>
<br>

# 알면 좋은것?
---

<br>

여기서 저는 몇가지 배운것이 있었습니다. 

- (간소화된)방식: InitializeAgent (1개)
- (상세한)방식: create_react_agent -> AgentExecutor (2개) <추천 + 이 프로젝트에 사용된 방식>

크게 위 2가지 방식을 사용할 수 있는데, 각자마다 장단점이 있습니다. 

"InitializeAgent"를 사용하는 방식은 바로 사용하기 "매우 쉽다"입니다.
처음에는 이것으로 추진하려고 했지만, 워낙 제약이 많고, 지원하는 파라미터 또한 사용이 어려워 결국 포기하였으며, 오류가 많이 존재하였습니다. 


다음 (상세한)방식은 랭체인에서도 추천하는 방향입니다만, 사용하기가 "비교적 까다롭다"입니다.
많은 기능을 제어할 수 있다는 점이지만, 직접 구현해야하는 부분이 많습니다. ( 바로 output_parser클래스를 상속받아서 클래스를 구현하고 인자에 넣어 사용가능한게 편했음. ) 


---
<br>

# 함수 정보 알려줄 때, 프롬프트 비법!!!!!!!!!

```python
    에이전트 LLM을 위한 프롬프트 작성 비결.
    
    1. 이 함수는 무엇인가?
    
    2. 이 함수의 인자와 반환값의 개수는 몇개인가
    3. 인자 하나씩 정보 알려주기 + 타입
    4. 반환값 하나씩 정보 알려주기 + 타입
    
    5. 내부 함수 로직 설명하기
    
    6. 반환값이 뭐일 때 FINISH하라고 하여 무한 Thought 방지시키기.
    
    7. 마지막 결과값에 대해서 정리하여 "한국어"로 작성. 
```

## 예시

```python
#----
JSON_Description_for_APIv1 = '''
먼저 전역적으로 알아야하는 정보입니다.
함수 호출 시, 인자는 JSON구조로만 전달해야합니다. 
"Action Input" 값은 다음과 같은 JSON을 참고하여 작성해야합니다:

{
    "AGENT_ID": <에이전트 값(이는 사용자가 요구할 때, 에이전트값을 추출해야합니다.), 또는 특정되지 않은 경우: UNKNOWN><타입:str>,
    "Function": <
    어떤 기능을 호출할지 명시하는 부분입니다. 현재 다음과 같은 값에서 요구한 값에 맞게 골라 문자열로 작성합니다: 
    1."Analysis_Review"(종합평가 관련 요청인 경우)
    2."Analysis_Module"(분석모듈 관련 요청인 경우)
    ><타입:str>,
    
    "GET_or_SET": <조회 및 정보요청의 경우: "GET", 정보 수정 및 변경의 경우 "SET"><타입:str>,
    "Content": {
        "Content_Name": <명령값><타입:str>,
        "Param": {} --> 이 부분은 "Content_Name"에 따라 값이 결정되거나 그대로 유지.
    }
}

여기서, "Content" 키 값 "Param"의 값은 "Content_Name"키 값에 따라 동적인 JSON값을 생성해야합니다. 
'''
#----
# 종합평가 관련 요청 JSON 설명서
Analysis_Review_JSON = '''
본격적으로 이 함수를 인자값을 작성하기 위하여
어떻게 "Content"키 값인 Content_Name키 값을 어떻게 작성하고, 이에 따라 "Param"키 값을 만드는 지 설명하겠습니다.

먼저 이 함수는 "종합평가"와 관련한 명령을 수행하는 함수입니다. 

종합평가 관련 요청은 다음과 같이 구성됩니다.

1. 종합평가 결과 모든 것을 요청할 때,
"Content_Name" : "ALL_REVIEW",
"Param" : {}

2. 종합평가 정책 관련 요청 시,
"Content_Name" : "POLICY",
"Param" : {}

3. 종합평가 시스템 관련 요청 시,
"Content_Name" : "SYSTEM",
"Param" : {}

함수 반환정보:
문자열로 반환됩니다. 실패관련한 문자열이 반환되지 않으면 즉시 FINISH 하여 결과를 한국어로 정리하여 작성하시오.

'''
#----
# 공통 END
END = '''
중요한 사항:
반환된 함수결과에 대해 사용자가 이해할 수 있도록 함수 반환 결과값과 연관하여 한국어로 작성해야합니다..
2번이상 Thought하지 않아야만 합니다. 빠르게 Final Answer 하십시오.
'''
```
