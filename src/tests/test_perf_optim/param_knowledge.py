from src.performance_optimizer.param_knowledge import ParamKnowledge
from src.tests.mock_ssh_client import SshClient


ssh_client = SshClient()
param_knowledge = ParamKnowledge(ssh_client)
res = param_knowledge.describe_param_background_knob(
    "mysql", ["innodb_adaptive_flushing"]
)
print(res)
