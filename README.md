# LangChain_with_Agent and Memory
랭체인기반으로 실제 함수를 호출하는 Agent를 빠르게 사용하는 코드를 개발하였습니다. 

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

  (1.) 함수 이름(이는 모델이 사용할 수 있는 함수를 이 이름으로 찾아냅니다. )
  (2.) 함수 ( 함수를 지정합니다. 이는 함수 이름만 작성해놓으면 됩니다. )
  (3.) 함수 사용 설명서 (이는 문장으로 인수를 어떻게 넘기는지 설명해야하고, 어떤 일을 하는 지 작성해야만 합니다. )
  (4.) 주의사항. 함수의 인자는 1개가 고정입니다. 타입은 str이며, (3)항목에서 요구하는 인수값에 따라 천차만별달라지므로, 정확하게 인수값을 모델이 전달해야할지 작성해야합니다!

```python
inst.Add_Agent_Tool('ABC', 'add', add, '3개의 인자를 모두 더하는 함수. 만약 인수가 부족하면, 나머지는 0으로 패딩하여 호출하라.')
```

<br>

5. Set_Prompt메서드는, 미리 지정한 프롬프트에 생성합니다. 
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
r = inst.Start_Agent_Conversation('ABC', '처음에 내가 무슨 값을 더하라고 했지?')['output']
print(r)
```

<br>

