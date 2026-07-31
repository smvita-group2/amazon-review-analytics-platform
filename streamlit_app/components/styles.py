def load_css():
    return """
    <style>

    /* Main App */
    .stApp{
        background-color:#0E1117;
        color:white;
    }

    /* Main Container */
    .block-container{
        padding-top:2rem;
        max-width:1200px;
    }

    /* Hero Title */
    .hero-title{
        text-align:center;
        font-size:64px;
        font-weight:800;
        line-height:1.2;
        margin-bottom:15px;
        background:linear-gradient(90deg,#FFFFFF,#3B82F6,#60A5FA);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
    }

    /* Hero Subtitle */
    .hero-subtitle{
        text-align:center;
        font-size:24px;
        color:#60A5FA;
        font-weight:500;
        letter-spacing:1px;
    }

    /* Hero Description */
    .hero-description{
        text-align:center;
        width:70%;
        margin:auto;
        font-size:20px;
        color:#CBD5E1;
        line-height:1.9;
        padding-top:20px;
    }

    /* Premium Buttons */

    .stButton > button{
        width:100%;
        height:60px;
        border-radius:14px;
        border:1px solid #2563EB;
        background:linear-gradient(90deg,#2563EB,#3B82F6);
        color:white;
        font-size:18px;
        font-weight:600;
        transition:.35s;
        box-shadow:0px 6px 20px rgba(37,99,235,.25);
    }

    .stButton > button:hover{
        transform:translateY(-4px);
        box-shadow:0px 12px 30px rgba(37,99,235,.45);
        border:1px solid #60A5FA;
    }

    /* Category Section */

    .category-title{
        text-align:center;
        font-size:34px;
        font-weight:700;
        color:white;
        margin-top:60px;
        margin-bottom:35px;
    }

    .category-card{
        background:#1A2233;
        border:1px solid #2E3B52;
        border-radius:18px;
        padding:25px;
        min-height:170px;
        transition:.35s;
        box-shadow:0 6px 20px rgba(0,0,0,.25);
    }

    .category-card:hover{
        transform:translateY(-8px);
        border-color:#3B82F6;
        box-shadow:0 14px 35px rgba(37,99,235,.35);
    }

    .category-icon{
        font-size:42px;
        margin-bottom:12px;
    }

    .category-name{
        font-size:24px;
        font-weight:700;
        color:white;
        margin-bottom:10px;
    }

    .category-text{
        font-size:16px;
        color:#CBD5E1;
        line-height:1.6;
    }

    </style>
    """