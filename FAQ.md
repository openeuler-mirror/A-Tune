1. 运行时，报错 `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`

错误栈：
```
Traceback (most recent call last):
  File "/root/workspace/eulercopilot/A-Tune/src/testmain.py", line 10, in <module>
    testCollector = MetricCollector(
                    ^^^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/src/performance_collector/metric_collector.py", line 47, in __init__
    cmd = get_mysql_cmd(
          ^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/src/performance_collector/mysql_collector.py", line 112, in get_mysql_cmd
    is_mysql_running = check_mysql_state(host_ip=host_ip, host_port=host_port, host_user=host_user, host_password=host_password)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/src/performance_collector/mysql_collector.py", line 63, in check_mysql_state
    mysql_state = get_llm_response(prompt=check_prompt.format(mysql_state=res[check_mysql_state_cmd]))
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/src/llm.py", line 8, in get_llm_response
    client = ChatOpenAI(
             ^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/venv/lib64/python3.11/site-packages/langchain_core/load/serializable.py", line 130, in __init__
    super().__init__(*args, **kwargs)
  File "/root/workspace/eulercopilot/A-Tune/venv/lib64/python3.11/site-packages/pydantic/main.py", line 193, in __init__
    self.__pydantic_validator__.validate_python(data, self_instance=self)
  File "/root/workspace/eulercopilot/A-Tune/venv/lib64/python3.11/site-packages/langchain_openai/chat_models/base.py", line 551, in validate_environment
    self.root_client = openai.OpenAI(**client_params, **sync_specific)  # type: ignore[arg-type]
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/venv/lib64/python3.11/site-packages/openai/_client.py", line 123, in __init__
    super().__init__(
  File "/root/workspace/eulercopilot/A-Tune/venv/lib64/python3.11/site-packages/openai/_base_client.py", line 856, in __init__
    self._client = http_client or SyncHttpxClientWrapper(
                                  ^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/venv/lib64/python3.11/site-packages/openai/_base_client.py", line 754, in __init__
    super().__init__(**kwargs)
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```
原因：连接 llm server 时，被 proxy 拦截。

解决方法：设置 no_proxy 变量，防止被 proxy 拦截。
```BASH
export no_proxy=9.82.33.59,$no_proxy
```

解决后测试：
```BASH
curl --location 'http://9.82.33.59:11434/v1/chat/completions' \
--header 'Content-Type: application/json' \
--data '{
    "model": "qwen2:72b",
    "messages": [
      {"role": "user", "content": "如何根据进程号采集cpu占用率"}
    ],
    "stream": true
  }'
```

预期输出类似如下，则说明修改成功：
```
data: {"id":"chatcmpl-603","object":"chat.completion.chunk","created":1747040993,"model":"qwen2:72b","system_fingerprint":"fp_ollama","choices":[{"index":0,"delta":{"role":"assistant","content":"在"},"finish_reason":null}]}

data: {"id":"chatcmpl-603","object":"chat.completion.chunk","created":1747040993,"model":"qwen2:72b","system_fingerprint":"fp_ollama","choices":[{"index":0,"delta":{"role":"assistant","content":"Linux"},"finish_reason":null}]}

data: {"id":"chatcmpl-603","object":"chat.completion.chunk","created":1747040993,"model":"qwen2:72b","system_fingerprint":"fp_ollama","choices":[{"index":0,"delta":{"role":"assistant","content":"系统"},"finish_reason":null}]}
```

2. 运行时，报错 `ValueError: Found array with 0 feature(s) (shape=(39, 0)) while a minimum of 1 is required by the normalize function.`

错误栈：
```
Building index for system.jsonl...: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 39/39 [00:19<00:00,  1.99it/s]
Traceback (most recent call last):
  File "/root/workspace/eulercopilot/A-Tune/src/testmain.py", line 36, in <module>
    plan, isfinish, feedback = testKnob.run()
                               ^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/src/performance_optimizer/base_optimizer.py", line 155, in run
    is_execute, optimization_plan = self.think(history=record)
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/src/performance_optimizer/knob_optimizer.py", line 56, in think
    knobs = rag.run()
            ^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/src/utils/rag/knob_rag.py", line 154, in run
    system_index, system_docs = self.build_index("system")
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/src/utils/rag/knob_rag.py", line 109, in build_index
    normalized_embeddings = normalize(np.array(embeddings).astype('float32'))
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/venv/lib64/python3.11/site-packages/sklearn/utils/_param_validation.py", line 213, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/venv/lib64/python3.11/site-packages/sklearn/preprocessing/_data.py", line 1933, in normalize
    X = check_array(
        ^^^^^^^^^^^^
  File "/root/workspace/eulercopilot/A-Tune/venv/lib64/python3.11/site-packages/sklearn/utils/validation.py", line 1096, in check_array
    raise ValueError(
ValueError: Found array with 0 feature(s) (shape=(39, 0)) while a minimum of 1 is required by the normalize function.
```
原因：embedding 接口不匹配。

解决方法：更新 REMOTE_EMBEDDING_ENDPOINT 配置为匹配的 embedding 接口 url。

