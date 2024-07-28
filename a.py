import streamlit as st
from htbuilder import HtmlElement, div, hr, a, p, styles, img, percent, px, br

def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))

def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)

def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
    </style>
    """

    style_div = styles(
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        text_align="center",
        height="60px",
        background_color="#1e1e1e",
        color="#ffffff",
        opacity=0.9
    )

    style_hr = styles()

    body = p()
    foot = div(style=style_div)(hr(style=style_hr), body)

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)
        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)

def footer():
    myargs = [
        "<b>Meet the Team:</b>",
        br(),
        link("https://www.linkedin.com/in/person1", 
             image('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/svgs/brands/linkedin.svg',
                   width=px(18), height=px(18), margin="0em")),
        " Person 1 ",
        " | ",
        link("https://www.linkedin.com/in/person2", 
             image('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/svgs/brands/linkedin.svg',
                   width=px(18), height=px(18), margin="0em")),
        " Person 2 ",
        " | ",
        link("https://www.linkedin.com/in/person3", 
             image('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/svgs/brands/linkedin.svg',
                   width=px(18), height=px(18), margin="0em")),
        " Person 3 "
    ]
    layout(*myargs)

if __name__ == "__main__":
    footer()
