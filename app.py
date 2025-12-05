import streamlit as st
from openai import OpenAI

# --- タイトルと設定 ---
st.title("💬 AI Persona Chat")
st.caption("AIの「人格」を切り替えて議論するアプリ")

# --- APIキーの取得（ここが変わりました！） ---
# 1. まず「金庫（Secrets）」にキーがあるか確認
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    # 2. なければサイドバーで入力（開発用や、キーがない場合）
    with st.sidebar:
        st.warning("設定ファイルにAPIキーが見つかりませんでした。")
        api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

if not api_key:
    st.info("APIキーが設定されていません。")
    st.stop()

# --- サイドバー：設定エリア ---
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 人格の選択
    persona_option = st.selectbox(
        "AIの人格を選んでください",
        ("論破するコメンテーター", "優しい関西弁のおばちゃん", "厳格な英語教師", "カスタム（自分で設定）")
    )
    
    # システムプロンプトの設定
    if persona_option == "論破するコメンテーター":
        system_prompt = """
        あなたは論理的で少し冷笑的なコメンテーターです。
        相手の意見の矛盾点を突き、「それってあなたの感想ですよね？」のような口調で話してください。
        語尾は「〜ですよね？」「〜だと思っちゃうんですけど」などを使ってください。
        """
    elif persona_option == "優しい関西弁のおばちゃん":
        system_prompt = """
        あなたは大阪の商店街にいる世話焼きで明るいおばちゃんです。
        コテコテの関西弁で話してください。「アメちゃんやるわ」「知らんけど」が口癖です。
        ユーザーを全肯定して元気づけてください。
        """
    elif persona_option == "厳格な英語教師":
        system_prompt = """
        あなたは非常に厳しい英語教師です。
        ユーザーが日本語で話しかけても、必ず「英語」で返答してください。
        文法の間違いがあれば厳しく指摘し、その後に正しい表現を教えてください。
        """
    else:
        system_prompt = st.text_area("システムプロンプトを入力", "あなたは役に立つAIアシスタントです。")

# --- チャットの処理 ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "準備できたで。（人格に合わせて変わります）"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    client = OpenAI(api_key=api_key)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    messages_to_send = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages_to_send
    )
    msg = response.choices[0].message.content
    
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)