import json

from openai import OpenAI
import streamlit as st

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
                m.to_json() for m in st.session_state.get(MSGS_KEY)
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
        raise e
        st.error(e)

    finally:
        pass
