import os

import time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    SubmitToolApprovalAction,
    ToolApproval,
)
from dotenv import load_dotenv



load_dotenv()

def ask_azure_agent(user_query):
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    with project_client:
        agents_client = project_client.agents
        agent = agents_client.get_agent(agent_id=os.environ["AGENT_ID"])
        # スレッドを新規作成
        thread = agents_client.threads.create()
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_query,
        )
        run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
            if run.status == "requires_action" and isinstance(run.required_action, SubmitToolApprovalAction):
                tool_calls = run.required_action.submit_tool_approval.tool_calls
                if not tool_calls:
                    agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
                    break
                tool_approvals = []
                for tool_call in tool_calls:
                    if isinstance(tool_call, RequiredMcpToolCall):
                        tool_approvals.append(
                            ToolApproval(
                                tool_call_id=tool_call.id,
                                approve=True,
                            )
                        )
                if tool_approvals:
                    agents_client.runs.submit_tool_outputs(
                        thread_id=thread.id, run_id=run.id, tool_approvals=tool_approvals
                    )
        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        return_message = ""
        last_message_id = ""
        for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                return_message = last_text.text.value
                last_message_id = msg.id
        # Clean up messages
        agents_client.messages.delete(thread_id=thread.id, message_id=message.id)
        agents_client.messages.delete(thread_id=thread.id, message_id=last_message_id)
        return return_message
