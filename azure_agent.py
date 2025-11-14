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
    try:
        project_client = AIProjectClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential(),
        )
        with project_client:
            agents_client = project_client.agents

            agent = agents_client.get_agent(agent_id=os.environ["AGENT_ID"])
            print(f"Using agent, ID: {agent.id}")

            thread = agents_client.threads.get(thread_id=os.environ["THREAD_ID"])
            print(f"Created thread, ID: {thread.id}")
           
            message = agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_query,
            )
            print(f"Created message, ID: {message.id}")
            run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
            print(f"Created run, ID: {run.id}")

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
                    print(f"tool_approvals: {tool_approvals}")
                    if tool_approvals:
                        agents_client.runs.submit_tool_outputs(
                            thread_id=thread.id, run_id=run.id, tool_approvals=tool_approvals
                        )
                print(f"Current run status: {run.status}")

            print(f"Run completed with status: {run.status}")
            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

            # Display run steps and tool calls
            run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)

            # Loop through each step
            for step in run_steps:
                try:
                    print(f"Step {step['id']} status: {step['status']}")

                    # Check if there are tool calls in the step details
                    step_details = step.get("step_details", {})
                    tool_calls = step_details.get("tool_calls", [])

                    if tool_calls:
                        print("  MCP Tool calls:")
                        for call in tool_calls:
                            print(f"    Tool Call ID: {call.get('id')}")
                            print(f"    Type: {call.get('type')}")

                    if isinstance(step_details, RunStepActivityDetails):
                        for activity in step_details.activities:
                            for function_name, function_definition in activity.tools.items():
                                print(
                                    f'  The function {function_name} with description "{function_definition.description}" will be called.:'
                                )
                                if len(function_definition.parameters) > 0:
                                    print("  Function parameters:")
                                    for argument, func_argument in function_definition.parameters.properties.items():
                                        print(f"      {argument}")
                                        print(f"      Type: {func_argument.type}")
                                        print(f"      Description: {func_argument.description}")
                                else:
                                    print("This function has no parameters")

                    print()
                except Exception as step_err:
                    print(f"Step処理中にエラー: {step_err}")

            messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            print("\nConversation:")
            print("-" * 50)

            return_message = ""
            last_message_id = ""

            for msg in messages:
                try:
                    if msg.text_messages:
                        print(f"msg.id: {msg.id}")
                        last_text = msg.text_messages[-1]
                        print(f"{msg.role.upper()}: {last_text.text.value}")
                        print("-" * 50)
                        return_message = last_text.text.value
                        last_message_id = msg.id
                except Exception as msg_err:
                    print(f"メッセージ処理中にエラー: {msg_err}")

            return return_message
    except Exception as e:
        print(f"全体処理中にエラー: {e}")
        return ""
