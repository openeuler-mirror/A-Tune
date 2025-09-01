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

3. openai客户端连接服务器时ssl证书校验失败

错误栈：
```
2025-09-01 15:05:56 - INFO [_base_client.py:_retry_request:1086] - Retrying request to /chat/completions in 0.995184 seconds
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/httpx/_transports/default.py", line 72, in map_httpcore_exceptions
    yield
  File "/usr/local/lib/python3.11/site-packages/httpx/_transports/default.py", line 236, in handle_request
    resp = self._pool.handle_request(req)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/httpcore/_sync/connection_pool.py", line 256, in handle_request
    raise exc from None
  File "/usr/local/lib/python3.11/site-packages/httpcore/_sync/connection_pool.py", line 236, in handle_request
    response = connection.handle_request(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/httpcore/_sync/http_proxy.py", line 316, in handle_request
    stream = stream.start_tls(**kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/httpcore/_sync/http11.py", line 376, in start_tls
    return self._stream.start_tls(ssl_context, server_hostname, timeout)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/httpcore/_backends/sync.py", line 154, in start_tls
    with map_exceptions(exc_map):
  File "/usr/lib64/python3.11/contextlib.py", line 155, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/httpcore/_exceptions.py", line 14, in map_exceptions
    raise to_exc(exc) from exc
httpcore.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1006)

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/openai/_base_client.py", line 990, in _request
    response = self._client.send(
               ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/httpx/_client.py", line 926, in send
    response = self._send_handling_auth(
               ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/httpx/_client.py", line 954, in _send_handling_auth
    response = self._send_handling_redirects(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/httpx/_client.py", line 991, in _send_handling_redirects
    response = self._send_single_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/httpx/_client.py", line 1027, in _send_single_request
    response = transport.handle_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/httpx/_transports/default.py", line 235, in handle_request
    with map_httpcore_exceptions():
  File "/usr/lib64/python3.11/contextlib.py", line 155, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/httpx/_transports/default.py", line 89, in map_httpcore_exceptions
    raise mapped_exc(message) from exc
httpx.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1006)

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/root/workspace/copilot/A-Tune-copilot/src/utils/llm.py", line 35, in <module>
    res = get_llm_response("介绍一下中国")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/workspace/copilot/A-Tune-copilot/src/utils/llm.py", line 19, in get_llm_response
    result = client.invoke(input=prompt)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 307, in invoke
    self.generate_prompt(
  File "/usr/local/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 843, in generate_prompt
    return self.generate(prompt_messages, stop=stop, callbacks=callbacks, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 683, in generate
    self._generate_with_cache(
  File "/usr/local/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 908, in _generate_with_cache
    result = self._generate(
             ^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langchain_openai/chat_models/base.py", line 689, in _generate
    return generate_from_stream(stream_iter)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 91, in generate_from_stream
    generation = next(stream, None)
                 ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/langchain_openai/chat_models/base.py", line 656, in _stream
    response = self.client.create(**payload)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/openai/_utils/_utils.py", line 274, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/openai/resources/chat/completions.py", line 815, in create
    return self._post(
           ^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/openai/_base_client.py", line 1277, in post
    return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/openai/_base_client.py", line 954, in request
    return self._request(
           ^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/openai/_base_client.py", line 1014, in _request
    return self._retry_request(
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/openai/_base_client.py", line 1092, in _retry_request
    return self._request(
           ^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/openai/_base_client.py", line 1014, in _request
    return self._retry_request(
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/openai/_base_client.py", line 1092, in _retry_request
    return self._request(
           ^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/openai/_base_client.py", line 1024, in _request
    raise APIConnectionError(request=request) from err
openai.APIConnectionError: Connection error.
```

解决办法：修改 /usr/local/lib/python3.11/site-packages/httpx/_client.py ，在 httpx.Client 创建时改为默认禁用ssl校验 verify=False：

```python
class Client(BaseClient):
    def __init__(
        self,
        *,
        auth: AuthTypes | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        # verify: VerifyTypes = True,
        verify: VerifyTypes = False, # 禁用ssl校验
        cert: CertTypes | None = None,
        http1: bool = True,
        http2: bool = False,
```