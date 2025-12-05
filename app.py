import streamlit as st

from openai import OpenAI

# --- タイトルと設定 ---
st.title("💬 AI Persona Chat")
st.caption("AIの「人格」を切り替えて議論するアプリ")

# --- サイドバー：設定エリア ---
with st.sidebar:
    st.header("⚙️ 設定")
    
    # APIキーの入力（セキュリティのためパスワード形式）
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    
    st.markdown("---")
    
    # 人格の選択
    persona_option = st.selectbox(
        "AIの人格を選んでください",
        ("論破するひろゆき風", "優しい関西弁のおばちゃん", "厳格な英語教師", "カスタム（自分で設定）")
    )
    
    # システムプロンプト（AIへの裏指示書）の定義
    if persona_option == "論破するひろゆき風":
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

    st.write("---")
    st.write("現在のシステム指示:")
    st.info(system_prompt) # 今どんな指示が入っているか表示

# --- チャットの処理 ---

# 1. チャット履歴の初期化（履歴がない場合）
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "準備できたで。何でも話しかけてな！（人格に合わせて変わります）"}]

# 2. 過去のチャット内容を画面に描画
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 3. ユーザーの入力があった時の処理
if prompt := st.chat_input():
    if not openai_api_key:
        st.info("左のサイドバーにOpenAI APIキーを入力してください")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    
    # ユーザーの入力を画面に表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # AIへの送信メッセージを作成（システムプロンプト + 会話履歴）
    # ここが「介入」のポイント！一番最初に「人格設定」を差し込みます。
    messages_to_send = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # AIからの返答を取得
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", # または "gpt-4o"
        messages=messages_to_send
    )
    msg = response.choices[0].message.content
    
    # AIの返答を画面に表示
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)