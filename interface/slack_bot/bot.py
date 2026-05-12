from ai_agent.graph import app_graph
from mcp_server.dispatcher import dispatch_tool
from slack_bolt import App
from dotenv import load_dotenv
import os

load_dotenv()

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

# MEMORY ĐƠN GIẢN
last_plan_cache = {}

@app.message("")
def message_handler(message, say):

    global last_plan_cache

    if message.get("bot_id"):
        return

    user_id = message.get("user")
    user_text = message.get("text", "").strip().lower()

    if not user_text:
        return

    try:

        # =========================
        # CASE 1: CONFIRMATION (NO LLM)
        # =========================
        if user_text in ["y", "yes"]:

            if user_id not in last_plan_cache:
                say("❌ Không có kế hoạch nào để xác nhận.")
                return

            say("🚀 Đang thực thi plan đã duyệt...")

            plan = last_plan_cache[user_id]

            for action in plan:
                tool_name = action.get("tool_name")
                args = action.get("tool_arguments", {})

                print(f"Executing: {tool_name}")

                result = dispatch_tool(tool_name, args)

                if result.get("status") != "SUCCESS":
                    say(f"❌ Failed: {result.get('raw_log')}")
                    return

            say("✅ Đã thực thi xong (NO LLM USED).")
            return

        # =========================
        # CASE 2: NORMAL REQUEST (LLM ONLY HERE)
        # =========================
        initial_state = {
            "user_prompt": user_text,
            "raw_input": user_text,
            "raw_user_input": user_text,
            "intent": "",
            "plan": {},
            "raw_log": ""
        }

        result = app_graph.invoke(initial_state)

        plan_data = result.get("plan", {})

        if isinstance(plan_data, dict):
            plan_output = plan_data.get("plan", [])
        else:
            plan_output = plan_data

        if not plan_output:
            say(f"🧠 Intent:\n```{result.get('intent')}```\n❌ Không có plan.")
            return

        # SAVE PLAN
        last_plan_cache[user_id] = plan_output

        say("🧠 INTENT")
        say("```" + str(result.get("intent")) + "```")

        say("⚙️ PLAN")
        say("```" + str(plan_output) + "```")

        say("❓ Reply 'y' để xác nhận thực thi")

    except Exception as e:
        say(f"❌ Lỗi: {str(e)}")


if __name__ == "__main__":
    print("🚀 Slack bot starting on port 3000...")
    app.start(port=3000)
