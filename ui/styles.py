import streamlit as st

def apply_global_styles():
    #Apply global CSS styling to the app
    st.markdown("""
        <style>
        /* Global enhancements 
        h2, h3 {
            padding-top: 30px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(219, 196, 66, 0.3);
            margin-bottom: 20px;
        }*/
        
        /* First header on page shouldn't have extra top padding */
        h2:first-of-type, h3:first-of-type {
            padding-top: 0;
        }
        
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(30, 136, 229, 0.1), rgba(219, 196, 66, 0.1));
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            cursor: default;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 8px 20px rgba(219, 196, 66, 0.3);
            border-color: rgba(219, 196, 66, 0.5);
            background: linear-gradient(135deg, rgba(30, 136, 229, 0.15), rgba(219, 196, 66, 0.15));
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(219, 196, 66, 0.3);
        }
        
        /* Divider styling */
        .stMarkdown hr,
        hr,
        .element-container hr,
        div[data-testid="stMarkdownContainer"] hr {
            border: none !important;
            height: 1px !important;
            background: linear-gradient(90deg, transparent, rgba(219, 196, 66, 0.5), transparent) !important;
            margin-top: 30px !important;
            margin-bottom: 30px !important;
            padding: 0 !important;
        }
        /* Accent colors */
        :root {
            --accent-gold: #DBC442;
            --accent-blue: #1E88E5;
            --accent-green: #2ecc71;
            --accent-red: #e74c3c;
        }
        </style>
    """, unsafe_allow_html=True)


def apply_welcome_background_styles():
    # welcome page background image and styling
    st.markdown("""
        <style>
        .stApp {
            background-image: 
                linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)),
                url('https://cmsassets.rgpub.io/sanity/images/dsfx7636/news/91ae2e211d99a8beff2f2febed20ba51fec055ac-3840x2160.jpg?auto=format&fit=fill&q=80&w=1349');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .stMarkdown, h1, h2, h3, h4, p {
            color: white !important;
        }
    """, unsafe_allow_html=True)


def remove_welcome_background_styles():
    #Remove welcome page background styling
    st.markdown("""
        <style>
        .stApp {
            background-image: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

def altair_chart_mobile_responsiveness():
    st.markdown("""
        <style>
            /* Make Altair charts responsive on mobile */
            @media (max-width: 768px) {
                .vega-embed {
                    width: 100% !important;
                }
                .vega-embed canvas {
                    max-width: 100% !important;
                    height: auto !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)

def smooth_transitions():
    st.markdown("""
        <style>
            *{
            transition: all 0.4s ease;
            }
            /* Tab styling */
            .stTabs [data-baseweb="tab"] {
                border-radius: 8px 8px 0 0;
                padding: 10px 20px;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
        </style>
""", unsafe_allow_html=True)
    
def match_history_styles():
    st.markdown("""
    <style>
        /* ====== Base (Desktop) Layout ====== */
        .match-card {
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }

        .match-card img.champion-icon {
            width: 65px !important;
            height: 65px !important;
            border-radius: 8px !important;
        }

        .match-card .stats {
            flex: 1;
            text-align: center;
        }

        .match-card .stats div:first-child {
            font-size: 18px !important;
            font-weight: 700 !important;
        }

        .match-card .stats div:last-child {
            color: #888 !important;
            font-size: 13px !important;
        }

        .match-card .items {
            display: flex;
            align-items: center;
            flex-wrap: nowrap;
            gap: 6px;
        }

        .match-card .items .item-grid {
            display: grid;
            grid-template-columns: repeat(3, 32px);
            gap: 2px;
        }

        .match-card .items img {
            width: 32px;
            height: 32px;
        }

        .match-card .items .trinket {
            width: 32px;
            height: 32px;
            border: 1px solid #d4af37;
            border-radius: 4px;
        }

        /* ====== Mobile Layout ====== */
        @media (max-width: 768px) {
            .match-card {
                display: grid !important;
                grid-template-columns: 80px 1fr;
                grid-template-rows: auto auto auto;
                gap: 4px 12px !important;
                align-items: start !important;
            }
            
            /* Champion icon - top left */
            .match-card img.champion-icon {
                width: 75px !important;
                height: 75px !important;
                grid-column: 1;
                grid-row: 1 / span 2;
            }
            
            /* Meta info (name, victory, queue) - below champion */
            .match-card .meta {
                grid-column: 1;
                grid-row: 3;
                font-size: 12px !important;
            }
            
            .match-card .meta > div:first-child {
                font-size: 14px !important;
                margin-bottom: 4px !important;
            }
            .match-card .meta > span {
                
            }
            
            /* KDA stats - top right, bigger */
            .match-card .stats {
                grid-column: 2;
                grid-row: 1;
                text-align: left !important;
                margin: 0 !important;
            }

            .match-card .stats div:first-child {
                font-size: 22px !important;
                font-weight: 700 !important;
            }
            
            .match-card .stats div:last-child {
                font-size: 14px !important;
            }

            /* Items - right side, below KDA */
            .match-card .items {
                grid-column: 2;
                grid-row: 3;
                justify-content: flex-end !important;
                flex-wrap: wrap !important;
                gap: 4px !important;
            }

            .match-card .items img {
                width: 28px !important;
                height: 28px !important;
            }
            
            .match-card .items .item-grid {
                grid-template-columns: repeat(3, 28px) !important;
            }
            
            .match-card .summoners img {
                width: 24px !important;
                height: 24px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    