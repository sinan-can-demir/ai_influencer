import os
import requests
from dotenv import load_dotenv
from groq import Groq
from pipeline.history import log_post

load_dotenv()

BASE_URL = "https://www.moltbook.com/api/v1"


def get_moltbook_credentials():
    api_key = os.environ["MOLTBOOK_API_KEY"]
    agent_name = os.environ["MOLTBOOK_AGENT_NAME"]
    print(f"Moltbook credentials loaded for agent: {agent_name}")
    return api_key, agent_name


def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def check_status(api_key):
    resp = requests.get(f"{BASE_URL}/agents/status", headers=get_headers(api_key))
    data = resp.json()
    status = data.get("status")
    print(f"Moltbook status: {status}")
    return status == "claimed"


def _solve_math_challenge(challenge_text):
    import re
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    # Step 1: use chain-of-thought to extract numbers and operation
    cot_system = (
        "You are a math parser. You will be given a heavily obfuscated math word problem "
        "with mixed caps, symbols, lobster-themed words, and broken spelling. "
        "Your job: ignore all the noise and find exactly TWO numbers and ONE arithmetic operation "
        "(add/plus, subtract/minus, multiply/times, divide). "
        "Reply in this exact format on three lines:\n"
        "NUMBER1: <first number>\n"
        "OPERATION: <+ or - or * or />\n"
        "NUMBER2: <second number>"
    )
    cot_resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": cot_system},
            {"role": "user", "content": challenge_text},
        ],
        temperature=0,
    )
    parsed = cot_resp.choices[0].message.content.strip()
    print(f"Challenge parsed: {parsed!r}")

    # Step 2: extract and compute
    try:
        n1 = float(re.search(r"NUMBER1:\s*([\d.]+)", parsed).group(1))
        op = re.search(r"OPERATION:\s*([+\-*/])", parsed).group(1)
        n2 = float(re.search(r"NUMBER2:\s*([\d.]+)", parsed).group(1))
        ops = {"+": n1 + n2, "-": n1 - n2, "*": n1 * n2, "/": n1 / n2}
        result = ops[op]
        answer = f"{result:.2f}"
        print(f"Challenge solved: {answer}")
        return answer
    except Exception as e:
        print(f"Challenge parse failed ({e}), falling back to direct solve")

    # Fallback: ask model directly
    fallback_resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "Solve the obfuscated math problem. Return ONLY the numeric answer with 2 decimal places."},
            {"role": "user", "content": challenge_text},
        ],
        temperature=0,
    )
    answer = fallback_resp.choices[0].message.content.strip()
    if re.match(r"^\d+(\.\d+)?$", answer):
        if "." not in answer:
            answer += ".00"
    print(f"Challenge solved (fallback): {answer}")
    return answer


def post_to_moltbook(api_key, title, content, submolt="general"):
    headers = get_headers(api_key)
    payload = {"submolt_name": submolt, "title": title, "content": content, "type": "text"}

    resp = requests.post(f"{BASE_URL}/posts", headers=headers, json=payload)
    data = resp.json()

    if not data.get("success"):
        print(f"Moltbook post failed: {data.get('message')}")
        return None

    post = data.get("post", {})
    post_id = post.get("id")

    if data.get("verification_required"):
        verification = post.get("verification", {})
        challenge_text = verification.get("challenge_text")
        verification_code = verification.get("verification_code")
        print(f"Verification required, solving challenge...")

        answer = _solve_math_challenge(challenge_text)

        verify_resp = requests.post(
            f"{BASE_URL}/verify",
            headers=headers,
            json={"verification_code": verification_code, "answer": answer},
        )
        verify_data = verify_resp.json()
        if not verify_data.get("success"):
            print(f"Verification failed: {verify_data.get('message')}")
            return None
        print("Verification passed: post is live")
    else:
        print(f"Post published immediately: {post_id}")

    post_url = f"https://www.moltbook.com/post/{post_id}"
    log_post(title, post_url, platform="moltbook")
    return post_url
