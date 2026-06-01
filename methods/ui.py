import streamlit as st


def apply_base_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
          --bg: #ffffff;
          --surface: #f8f9fa;
          --surface-alt: #e9ecef;
          --text: #2c3e50;
          --muted: #7f8c8d;
          --accent: #1e3a5f;
          --border: #e3e6e8;
          --radius: 10px;
          --shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
          --primary-color: #1e3a5f;
          --primary-color-light: rgba(30, 58, 95, 0.12);
        }

        html, body, [class*="css"] {
          font-family: "Inter", "Open Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
          color: var(--text);
          line-height: 1.7;
          font-size: 16px;
        }

        .stApp {
          background: var(--bg);
        }

        header[data-testid="stHeader"] {
          background: var(--bg);
        }

        div[data-testid="stToolbar"] {
          background: var(--bg);
        }

        #MainMenu,
        footer {
          visibility: hidden;
        }

        .block-container {
          max-width: 1200px;
          padding: 5rem 5rem 6.5rem;
        }

        @media (max-width: 1200px) {
          .block-container {
            padding: 3.5rem 3rem 5rem;
          }
        }

        @media (max-width: 768px) {
          .block-container {
            padding: 2.5rem 1.5rem 4rem;
          }
        }

        h1, h2, h3, h4 {
          font-weight: 600;
          letter-spacing: -0.01em;
          color: var(--text);
        }

        h1 {
          font-size: 2.25rem;
          margin-bottom: 1rem;
        }

        h2 {
          font-size: 1.6rem;
          margin-top: 3.5rem;
          margin-bottom: 1.25rem;
        }

        h3 {
          font-size: 1.25rem;
          margin-top: 2.5rem;
          margin-bottom: 0.75rem;
        }

        p, label, .stMarkdown {
          color: var(--text);
        }

        div[data-testid="stMarkdownContainer"] * {
          color: var(--text);
        }

        div[data-testid="stText"],
        div[data-testid="stText"] * {
          color: var(--text);
        }

        .stCaption, small {
          color: var(--muted);
        }

        div[data-testid="stForm"] {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 1.5rem;
          box-shadow: var(--shadow);
        }

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {
          background: var(--bg);
          padding: 0.6rem 0.9rem;
          box-shadow: none;
          color: var(--text);
        }

        div[data-baseweb="select"] > div {
          border-radius: var(--radius);
          border: 1px solid var(--border);
          background: var(--bg);
          box-shadow: none;
          color: var(--text);
        }

        div[data-baseweb="select"] * {
          color: var(--text);
        }

        div[data-baseweb="select"] > div:hover {
          border-color: var(--accent);
        }

        div[data-baseweb="popover"] * {
          color: var(--text);
        }

        div[data-baseweb="popover"] {
          background: var(--bg);
        }

        ul[role="listbox"],
        div[role="listbox"] {
          background: var(--bg);
        }

        ul[role="listbox"] li,
        div[role="listbox"] li,
        div[role="option"] {
          background: var(--bg) !important;
          color: var(--text) !important;
        }

        ul[role="listbox"] li:hover,
        div[role="listbox"] li:hover,
        div[role="option"]:hover,
        div[role="option"][aria-selected="true"] {
          background: var(--surface) !important;
          color: var(--text) !important;
        }

        div[role="option"]:focus {
          outline: 2px solid rgba(30, 58, 95, 0.2);
          outline-offset: -2px;
        }

        input[type="checkbox"],
        input[type="radio"],
        input[type="range"] {
          accent-color: var(--accent);
        }

        div[data-testid="stToggle"] input {
          accent-color: var(--accent);
        }

        button:focus-visible,
        input:focus-visible,
        textarea:focus-visible,
        select:focus-visible {
          outline-color: var(--accent);
        }

        div[data-baseweb="input"] {
          padding: 0;
        }

        .stTextInput input:focus,
        .stTextArea textarea:focus,
        .stNumberInput input:focus,
        div[data-baseweb="select"] > div:focus-within {
          border-color: var(--accent);
          box-shadow: 0 0 0 2px rgba(30, 58, 95, 0.12);
        }

        .stButton > button,
        .stForm button {
          border: 1px solid var(--accent) !important;
          background: var(--accent) !important;
          color: #ffffff !important;
          padding: 0.55rem 1.1rem;
          font-weight: 600;
          box-shadow: none;
          transition: background 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
        }

        .stButton > button *,
        .stForm button * {
          color: #ffffff !important;
        }

        .stButton > button:hover,
        .stForm button:hover {
          background: #162c48;
          border-color: #162c48;
        }

        .stButton > button:focus {
          box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.2);
        }

        hr {
          border-color: var(--border);
          margin: 4rem 0;
        }

        .stDataFrame,
        .stTable,
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
          border-radius: var(--radius);
          border: 1px solid var(--border);
          background: var(--bg);
          overflow: hidden;
        }

        div[data-testid="stDataFrame"] thead tr,
        div[data-testid="stTable"] thead tr {
          background: var(--accent);
        }

        div[data-testid="stDataFrame"] table,
        div[data-testid="stTable"] table {
          background: var(--bg);
        }

        div[data-testid="stDataFrame"] tbody tr,
        div[data-testid="stTable"] tbody tr,
        div[data-testid="stDataFrame"] td,
        div[data-testid="stTable"] td {
          background: var(--bg);
        }

        div[data-testid="stDataFrame"] th,
        div[data-testid="stTable"] th,
        div[data-testid="stDataFrame"] td,
        div[data-testid="stTable"] td {
          border-color: var(--border);
          color: var(--text);
        }

        div[data-testid="stDataFrame"] *,
        div[data-testid="stTable"] * {
          color: var(--text);
        }

        div[data-testid="stDataFrame"] th,
        div[data-testid="stTable"] th {
          color: #ffffff !important;
        }

        div[data-testid="stAlert"] {
          background: var(--surface);
          border: 1px solid var(--border);
          color: var(--text);
        }

        div[data-testid="stAlert"] * {
          color: var(--text);
        }

        div[data-testid="stMetric"] * {
          color: var(--text);
        }

        section[data-testid="stSidebar"] {
          background: var(--surface);
          border-right: 1px solid var(--border);
        }

        section[data-testid="stSidebar"] * {
          color: var(--text);
        }

        a, a:visited {
          color: var(--text);
          text-decoration: none;
          transition: color 160ms ease;
        }

        a:hover {
          color: var(--accent);
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.get("is_authenticated"):
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"] {
              display: none;
            }

            div[data-testid="stSidebarNav"] {
              display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
