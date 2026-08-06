def load_css():
    return """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"]{
        font-family:'Inter',sans-serif;
    }

    /* =======================================================
       APP
    ======================================================= */

    .stApp{
        background:#FFFFFF !important;
        color:#111111 !important;
    }

    .block-container{
        max-width:1280px;
        padding-top:1.5rem;
        padding-bottom:2rem;
    }

    header,
    footer,
    #MainMenu{
        visibility:hidden;
    }

    /* =======================================================
       HERO
    ======================================================= */

    .hero-logo{
        display:flex;
        justify-content:center;
        margin-top:10px;
        margin-bottom:20px;
    }

    .hero-title{
        text-align:center;
        font-size:54px;
        font-weight:800;
        color:#111111;
        margin-top:5px;
        margin-bottom:10px;
        line-height:1.2;
    }

    .hero-subtitle{
        text-align:center;
        font-size:22px;
        font-weight:500;
        color:#666666;
        margin-bottom:25px;
        line-height:1.4;
    }

    .hero-description{
        text-align:center;
        width:72%;
        margin:auto;
        color:#555555;
        font-size:18px;
        line-height:1.8;
        margin-bottom:35px;
    }

    /* =======================================================
       SEARCH
    ======================================================= */

    .stTextInput{
        margin-top:10px;
    }

    .stTextInput input{

        background:#FFFFFF;

        border:2px solid #DDDDDD;

        border-radius:16px;

        padding:14px 18px;

        font-size:17px;

        color:#111111;

    }

    .stTextInput input:focus{

        border:2px solid #FF9900;

        box-shadow:0 0 10px rgba(255,153,0,.25);

    }

    /* =======================================================
       BUTTONS
    ======================================================= */

    .stButton>button{

        width:100%;

        height:55px;

        border:none;

        border-radius:14px;

        background:#FF9900;

        color:white;

        font-size:17px;

        font-weight:600;

        transition:.30s;

    }

    .stButton>button:hover{

        background:#E68900;

        transform:translateY(-3px);

    }

    /* =======================================================
       TOGGLE / RADIO
    ======================================================= */

    div[role="radiogroup"]{

        display:flex;

        justify-content:center;

        gap:25px;

        margin-top:20px;

        margin-bottom:25px;

    }

    /* =======================================================
       CATEGORY TITLE
    ======================================================= */

    .category-title{

        text-align:center;

        font-size:40px;

        font-weight:700;

        color:#111111;

        margin-top:55px;

        margin-bottom:30px;

    }

    /* =======================================================
       CATEGORY CARD
    ======================================================= */

    .category-card{

        background:#FFFFFF;

        border-radius:22px;

        border:1px solid #E5E7EB;

        overflow:hidden;

        box-shadow:0 8px 24px rgba(0,0,0,.08);

        transition:.35s;

        margin-bottom:25px;

    }

    .category-card:hover{

        transform:translateY(-8px);

        box-shadow:0 18px 35px rgba(0,0,0,.15);

    }

    /* =======================================================
       IMAGE
    ======================================================= */

    .stImage img{

        width:100% !important;

        height:350px !important;

        object-fit:cover !important;

        border-radius:18px;

    }

    /* =======================================================
       CATEGORY TEXT
    ======================================================= */

    .category-content{

        padding:18px;

    }

    .category-name{

        font-size:25px;

        font-weight:700;

        color:#111111;

        margin-bottom:10px;

    }

    .category-text{

        font-size:16px;

        color:#666666;

        line-height:1.7;

    }

    /* =======================================================
       REMOVE EXTRA WHITE SPACE
    ======================================================= */

    .element-container{

        margin-bottom:0.5rem;

    }
    /* =========================================================
   NAVIGATION
========================================================= */

div[data-testid="stSegmentedControl"]{
    margin-top:10px;
    margin-bottom:30px;
}

div[data-testid="stSegmentedControl"] div[role="radiogroup"]{
    justify-content:center;
}

/* =========================================================
   CATEGORY TITLE
========================================================= */

.category-title{

    text-align:center;

    font-size:38px;

    font-weight:700;

    color:#111111;

    margin-top:40px;

    margin-bottom:35px;

}

/* =========================================================
   CATEGORY IMAGE
========================================================= */

.stImage img{

    width:100% !important;

    height:350px !important;

    object-fit:cover !important;

    border-radius:22px;

    transition:0.35s;

    box-shadow:0px 8px 30px rgba(0,0,0,.10);

}

.stImage img:hover{

    transform:translateY(-8px);

    box-shadow:0px 20px 45px rgba(0,0,0,.18);

}

/* =========================================================
   CATEGORY NAME
========================================================= */

h3{

    text-align:center;

    font-weight:700;

    color:#111111;

    margin-top:12px;

}

/* =========================================================
   CATEGORY DESCRIPTION
========================================================= */

div[data-testid="stCaptionContainer"]{

    text-align:center;

    color:#666666;

    font-size:15px;

    margin-bottom:25px;

}

/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width:768px){

.hero-title{

    font-size:40px;

}

.hero-subtitle{

    font-size:18px;

}

.hero-description{

    width:95%;

}

.block-container{

    padding-left:1rem;

    padding-right:1rem;

}

.stImage img{

    height:250px !important;

}

}

    </style>
    """