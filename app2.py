import streamlit as st
import requests
from datetime import datetime

def получить_транзакции(адрес):
    """Получение данных транзакций для указанного адреса кошелька"""
    try:
        url = f'https://blockchain.info/rawaddr/{адрес}'
        ответ = requests.get(url)
        ответ.raise_for_status()
        return ответ.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка при получении данных: {str(e)}")
        return None

def форматировать_время(timestamp):
    """Преобразование Unix-времени в читаемый формат"""
    return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M:%S')

def форматировать_btc(satoshi):
    """Преобразование сатоши в BTC с правильным форматированием"""
    return f"{satoshi / 1e8:.8f} BTC"

# Настройка страницы
st.set_page_config(
    page_title="Модуль поиска криптовалютных средств",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Стилизация
st.markdown("""
    <style>
        .stButton>button {
            background-color: #1E88E5;
            color: white;
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            width: 100%;
        }
        .stTextInput>div>div>input {
            font-size: 16px;
            padding: 10px;
        }
        h1 {
            color: #1E88E5;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Заголовок и описание
st.title("📊 Модуль поиска криптовалютных средств")
st.markdown("""
    ### Информация о транзакциях криптовалютных кошельков
    Введите адрес Bitcoin-кошелька для получения подробной информации о транзакциях и балансе.
""")

# Поле ввода адреса
адрес_кошелька = st.text_input(
    "Введите адрес Bitcoin-кошелька",
    placeholder="Например: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    help="Введите полный адрес Bitcoin-кошелька для поиска"
)

# Кнопка поиска
if st.button("🔍 Найти транзакции"):
    if not адрес_кошелька:
        st.warning("⚠️ Пожалуйста, введите адрес кошелька")
    else:
        with st.spinner("⏳ Получение данных..."):
            данные = получить_транзакции(адрес_кошелька)
            
            if данные:
                # Основная информация о кошельке
                st.markdown("### 📈 Общая статистика кошелька")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Всего транзакций", данные['n_tx'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Текущий баланс", форматировать_btc(данные['final_balance']))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Всего получено", форматировать_btc(данные['total_received']))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Всего отправлено", форматировать_btc(данные['total_sent']))
                    st.markdown('</div>', unsafe_allow_html=True)

                # Вкладки с историей транзакций
                st.markdown("### 📋 История транзакций")
                вкладка1, вкладка2 = st.tabs(["Подробный вид", "Компактный вид"])
                
                with вкладка1:
                    for tx in данные['txs']:
                        with st.expander(
                            f"💸 Транзакция {tx['hash'][:8]}... от {форматировать_время(tx['time'])}"
                        ):
                            cols = st.columns(2)
                            with cols[0]:
                                st.markdown("**Хэш транзакции:**")
                                st.code(tx['hash'])
                                st.markdown(f"**Сумма:** {форматировать_btc(abs(tx['result']))}")
                            with cols[1]:
                                st.markdown(f"**Дата:** {форматировать_время(tx['time'])}")
                                st.markdown(f"**Подтверждений:** {tx.get('confirmations', 0)}")
                                st.markdown(f"**Высота блока:** {tx.get('block_height', 'В ожидании')}")
                
                with вкладка2:
                    транзакции = []
                    for tx in данные['txs']:
                        транзакции.append({
                            "Дата": форматировать_время(tx['time']),
                            "Сумма": форматировать_btc(abs(tx['result'])),
                            "Тип": "Получение" if tx['result'] > 0 else "Отправка",
                            "Подтверждений": tx.get('confirmations', 0)
                        })
                    
                    if транзакции:
                        st.dataframe(
                            транзакции,
                            use_container_width=True,
                            height=400
                        )

                # Дополнительная информация
                st.markdown("### ℹ️ Дополнительная информация")
                st.info(
                    "Данные обновляются в реальном времени из блокчейна Bitcoin. "
                    "Для получения актуальной информации обновите страницу."
                )
