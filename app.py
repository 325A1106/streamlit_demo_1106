import streamlit as st
import random

# --- カード画像のURLを生成する関数 ---
def get_card_url(card):
    # APIの命名規則に合わせて変換 (例: ♠A -> https://deckofcardsapi.com/static/img/AS.png)
    rank = card['rank']
    if rank == '10': rank = '0' # 10だけは '0' と表記される仕様
    suit = card['suit_code']
    return f"https://deckofcardsapi.com/static/img/{rank}{suit}.png"

# --- ゲームのロジック ---
def create_deck():
    # 画像取得のために suit_code を追加
    suits = [('♠', 'S'), ('♥', 'H'), ('♦', 'D'), ('♣', 'C')]
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return [{'rank': r, 'suit': s[0], 'suit_code': s[1]} for s in suits for r in ranks]

def calculate_score(hand):
    score = 0
    aces = 0
    for card in hand:
        if card['rank'] in ['J', 'Q', 'K']:
            score += 10
        elif card['rank'] == 'A':
            aces += 1
            score += 11
        else:
            score += int(card['rank'])
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score

# --- Streamlit UI ---
st.set_page_config(page_title="Card Image Blackjack", layout="wide")
st.title("🃏 Blackjack")
st.image("black_jack.jpg")

if 'deck' not in st.session_state:
    st.session_state.deck = create_deck()
    random.shuffle(st.session_state.deck)
    st.session_state.player_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.dealer_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.game_over = False
    st.session_state.result = ""

def reset_game():
    st.session_state.deck = create_deck()
    random.shuffle(st.session_state.deck)
    st.session_state.player_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.dealer_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
    st.session_state.game_over = False
    st.session_state.result = ""
    
# サイドバーにリセットボタン
st.sidebar.button("ゲームをリセット", on_click=reset_game)

# --- 表示エリア ---
player_score = calculate_score(st.session_state.player_hand)

# ディーラーセクション
st.subheader("Dealer's Hand")
d_cols = st.columns(6)
for i, card in enumerate(st.session_state.dealer_hand):
    with d_cols[i]:
        if i == 1 and not st.session_state.game_over:
            # 2枚目のカードは裏向き
            st.image("https://deckofcardsapi.com/static/img/back.png")
        else:
            st.image(get_card_url(card))

# プレイヤーセクション
st.subheader(f"Your Hand (Score: {player_score})")
p_cols = st.columns(6)
for i, card in enumerate(st.session_state.player_hand):
    with p_cols[i]:
        st.image(get_card_url(card))

# --- アクション ---
st.divider()
if not st.session_state.game_over:
    if player_score > 21:
        st.error("バースト！あなたの負けです。")
        st.session_state.game_over = True
    else:
        c1, c2, _ = st.columns([1, 1, 4])
        if c1.button("ヒット (Hit)"):
            st.session_state.player_hand.append(st.session_state.deck.pop())
            st.rerun()
        if c2.button("スタンド (Stand)"):
            while calculate_score(st.session_state.dealer_hand) < 17:
                st.session_state.dealer_hand.append(st.session_state.deck.pop())
            st.session_state.game_over = True
            st.rerun()

# 最終結果判定
if st.session_state.game_over:
    dealer_score = calculate_score(st.session_state.dealer_hand)
    if not st.session_state.result:
        if player_score > 21: st.session_state.result = "バースト！あなたの負けです。"
        elif dealer_score > 21: st.session_state.result = "ディーラーがバースト！あなたの勝ちです！"
        elif player_score > dealer_score: st.session_state.result = "あなたの勝ちです！"
        elif player_score < dealer_score: st.session_state.result = "ディーラーの勝ちです。"
        else: st.session_state.result = "引き分けです。"
    
    st.info(f"結果: {st.session_state.result} (Dealer: {dealer_score})")
    if st.button("もう一度遊ぶ"):
        reset_game()

        st.rerun()

