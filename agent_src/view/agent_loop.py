import json

from openai import OpenAI
import streamlit as st

from agent_src.functions import get_active_chat_msgs
from agent_src.models.models import *
from agent_src.tools import get_all_tools_list, AgentTool
from agent_src.values.const import *
from agent_src.view.common import add_message


def is_goal_achieved() -> bool:
    if len(st.session_state.get(MSGS_KEY)) == 0:
        return False

    last_msg = st.session_state.get(MSGS_KEY)[-1]

    if not isinstance(last_msg, AssistantChatMsg):
        return False

    assistant_msg = last_msg

    if assistant_msg.content.strip().endswith("?"):
        return True

    if len(assistant_msg.tool_calls) > 0:
        return False

    if len(assistant_msg.reasoning) >= 0 and len(assistant_msg.content) == 0:
        return False

    return True


def call_model():
    try:
        client = OpenAI(
            base_url=st.session_state.get(URL_KEY) + st.session_state.get(END_POINT_KEY),
            api_key='111'
        )

        st.session_state[CALLS_COUNTER] = st.session_state[CALLS_COUNTER] + 1

        completion = client.chat.completions.create(
            model=st.session_state.get(MODEL_KEY),
            messages=[
                m.to_json() for m in get_active_chat_msgs()
            ],
            tools=get_all_tools_list(),
        )

        assistant_msg = AssistantChatMsg(
            dump=completion.choices[0].message.model_dump(),
            content=completion.choices[0].message.content,
            reasoning=getattr(completion.choices[0].message, "reasoning", None),
            tool_calls=completion.choices[0].message.tool_calls,
        )

        add_message(assistant_msg)

        for tool_call_json in assistant_msg.tool_calls:
            function_name = tool_call_json['function']['name']
            function_arguments = json.loads(tool_call_json['function']['arguments'])
            tool_call_id = tool_call_json['id']

            result = "Tool Not Found"

            for tool_class in AgentTool.__subclasses__():
                tool_obj = tool_class()
                if tool_obj.get_name() == function_name:
                    result = tool_obj.execute(parameters=function_arguments)
                    break

            if isinstance(result, dict):
                result = json.dumps(result)

            add_message(
                ToolCallChatMsg(
                    tool_call_id=tool_call_id,
                    function_name=function_name,
                    function_arguments=function_arguments,
                    result=result
                )
            )

    except Exception as e:
        st.session_state[AGENT_STATUS] = AgentStatus.STOPPED
        # raise e
        st.error(e)

    finally:
        pass


def mark_expired_msgs():
    msgs = st.session_state.get(MSGS_KEY)

    start_expiring = len(msgs) - 10

    # Remove all reasoning msgs when model gives an answer
    def stage_1():
        flag_remove_reasoning = False

        for i in range(start_expiring, -1, -1):
            if isinstance(msgs[i], AssistantChatMsg):
                if msgs[i].content != "":
                    flag_remove_reasoning = True

                if flag_remove_reasoning:
                    if msgs[i].reasoning != "":
                        msgs[i].expired = True

    # Remove old tools messages before user messages
    def stage_2():
        flag_remove_tools = False

        for i in range(start_expiring, -1, -1):
            if isinstance(msgs[i], UserChatMsg):
                flag_remove_tools = True

            if flag_remove_tools and isinstance(msgs[i], ToolCallChatMsg):
                msgs[i].expired = True

    # Remove duplicated tools calls with same name&args
    def stage_3():
        discovered_meta_data = set()

        for i in range(start_expiring, -1, -1):
            if isinstance(msgs[i], ToolCallChatMsg):
                meta_data_i = "{}#{}".format(
                    msgs[i].function_name,
                    json.dumps(
                        msgs[i].function_arguments,
                        sort_keys=True,
                    )
                )

                if meta_data_i in discovered_meta_data:
                    msgs[i].expired = True
                else:
                    discovered_meta_data.add(meta_data_i)

    stage_1()
    stage_2()
    stage_3()
