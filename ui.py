import os
import streamlit as st
import httpx
import json
import csv
from io import StringIO

from i18n import UA, EN
from database import init_db, register_user, login_user, save_history, get_history

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/scrape")

init_db()

for key, default in [
    ("language", "ua"),
    ("user", None),
    ("page", "login"),
    ("last_result", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

lang = UA if st.session_state.language == "ua" else EN

st.set_page_config(page_title="Adaptive Web Scraper", page_icon="🌐", layout="centered")

def _render_language_selector():
    sel = st.radio(
        label="🌐",
        options=["ua", "en"],
        format_func=lambda x: "Українська" if x == "ua" else "English",
        horizontal=True,
        index=0 if st.session_state.language == "ua" else 1,
        label_visibility="collapsed",
    )
    if sel != st.session_state.language:
        if st.session_state.last_result:
            st.toast(
                ("Мову змінено. Скрапіть сторінку ще раз, "
                 "щоб отримати вміст Українською.")
                if sel == "ua"
                else ("Language changed. Scrape again "
                      "to get content in English.")
            )
        st.session_state.language = sel
        st.session_state.last_result = None
        st.rerun()

if st.session_state.user:
    with st.sidebar:
        st.success(lang["welcome"].format(st.session_state.user["username"]))
        st.markdown("---")
        if st.button(lang["nav_scraper"], use_container_width=True):
            st.session_state.page = "scraper"
            st.rerun()
        if st.button(lang["nav_history"], use_container_width=True):
            st.session_state.page = "history"
            st.rerun()
        if st.button(lang["nav_about"], use_container_width=True):
            st.session_state.page = "about"
            st.rerun()
        st.markdown("---")
        if st.button(lang["logout_btn"], use_container_width=True, type="secondary"):
            st.session_state.user = None
            st.session_state.page = "login"
            st.session_state.last_result = None
            st.rerun()
        st.markdown("---")
        st.markdown(f"**{lang['language']}:**")
        _render_language_selector()

else:
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**{lang['language']}:**")
        _render_language_selector()

if not st.session_state.user:
    if st.session_state.page == "register":
        st.markdown(f"# {lang['register_page_title']}")

        with st.container(border=True):
            with st.form("register_form", clear_on_submit=True):
                reg_user = st.text_input(lang["username"])
                reg_pass = st.text_input(lang["password"], type="password")
                if st.form_submit_button(lang["register_btn"], use_container_width=True, type="primary"):
                    if register_user(reg_user, reg_pass):
                        st.success(lang["register_success"])
                    else:
                        st.error(lang["register_failed"])

            st.markdown("---")
            if st.button(lang["has_account"] + " " + lang["login_link"]):
                st.session_state.page = "login"
                st.rerun()
    else:
        st.markdown(f"# {lang['login_page_title']}")

        with st.container(border=True):
            with st.form("login_form", clear_on_submit=True):
                login_user_input = st.text_input(lang["username"])
                login_pass_input = st.text_input(lang["password"], type="password")
                if st.form_submit_button(lang["login_btn"], use_container_width=True, type="primary"):
                    user = login_user(login_user_input, login_pass_input)
                    if user:
                        st.session_state.user = user
                        st.session_state.page = "scraper"
                        st.rerun()
                    else:
                        st.error(lang["login_failed"])

            st.markdown("---")
            if st.button(lang["no_account"] + " " + lang["register_link"]):
                st.session_state.page = "register"
                st.rerun()

elif st.session_state.page == "scraper":
    st.title(lang["app_title"])
    st.markdown(lang["subtitle"])

    url = st.text_input(lang["url_label"], placeholder=lang["url_placeholder"])

    if st.button(lang["scrape_btn"], type="primary"):
        if not url:
            st.error(lang["error_url"])
        else:
            with st.spinner(lang["spinner"]):
                try:
                    with httpx.Client(timeout=120.0) as client:
                        response = client.post(
                            BACKEND_URL,
                            json={"url": url, "language": st.session_state.language},
                        )

                    if response.status_code == 200:
                        data = response.json()

                        save_history(st.session_state.user["id"], url, data)

                        st.session_state.last_result = (url, data)
                        st.rerun()
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"Error {response.status_code}: {error_detail}")
                except httpx.ConnectError:
                    st.error(lang["error_connect"])
                except Exception as e:
                    st.error(lang["error_generic"].format(e))

    if st.session_state.last_result:
        url, data = st.session_state.last_result
        st.markdown(f"*{url}*")

        with st.container(border=True):
            if data.get("image"):
                try:
                    st.image(data["image"], use_container_width=True)
                except Exception:
                    pass

            title = data.get("title", lang["no_title"])
            atype = data.get("article_type", "")
            badges_html = ""
            if atype:
                type_label = {
                    "interview": lang["interview"],
                    "news": lang["news"],
                    "opinion": lang["opinion"],
                }.get(atype, atype)
                badges_html += (
                    f"<span style='background-color:#f0f2f6;padding:4px 12px;"
                    f"border-radius:12px;font-size:0.85em'>{type_label}</span> "
                )
            if data.get("translated"):
                badges_html += (
                    f"<span style='background-color:#fff3cd;padding:4px 12px;"
                    f"border-radius:12px;font-size:0.85em'>{lang['translated']}</span> "
                )
            st.markdown(
                f"<h3 style='text-align:center;margin-bottom:4px'>{title}</h3>"
                f"<div style='text-align:center;margin-bottom:16px'>{badges_html}</div>",
                unsafe_allow_html=True,
            )

            author_name = data.get("author", "N/A")
            author_url = data.get("author_url", "")
            author_display = f"<a href='{author_url}'>{author_name}</a>" if author_url else author_name
            st.markdown(
                f"<div style='display:flex;justify-content:space-between'>"
                f"<span><strong>{lang['author']}:</strong> {author_display}</span>"
                f"<span><strong>{lang['date']}:</strong> {data.get('date', 'N/A')}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

            st.markdown("---")
            st.markdown(f"**{lang['summary']}:**")
            summary_text = data.get("summary", lang["no_summary"])
            paragraphs = [p.strip() for p in summary_text.split("\n\n") if p.strip()]
            for p in paragraphs:
                st.write(p)

            kp = data.get("key_points", "")
            if kp:
                st.markdown("---")
                st.markdown(f"**{lang['key_points']}:**")
                for point in kp.split("\n"):
                    point = point.strip()
                    if point:
                        st.markdown(f"- {point.lstrip('- ')}")

        if data.get("error"):
            st.warning(data["error"])

elif st.session_state.page == "history" and st.session_state.user:
    st.title(lang["history_title"])
    history = get_history(st.session_state.user["id"])

    if not history:
        st.info(lang["history_empty"])
    else:
        export_data = []
        for item in history:
            res = item["result"]
            if isinstance(res, str):
                res = json.loads(res)
            export_data.append({
                "url": item["url"],
                "title": res.get("title", ""),
                "article_type": res.get("article_type", ""),
                "author": res.get("author", ""),
                "date": res.get("date", ""),
                "summary": res.get("summary", ""),
                "key_points": res.get("key_points", ""),
                "image": res.get("image", ""),
                "translated": res.get("translated", False),
                "saved_at": item["created_at"],
            })

        col1, col2 = st.columns(2)
        with col1:
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            st.download_button(
                label=lang["export_json"],
                data=json_str,
                file_name="scraping_history.json",
                mime="application/json",
                use_container_width=True,
            )
        with col2:
            buf = StringIO()
            w = csv.writer(buf)
            w.writerow(["URL", "Title", "Type", "Author", "Date", "Summary", "Key Points", "Image", "Translated", "Saved At"])
            for row in export_data:
                w.writerow([row["url"], row["title"], row["article_type"],
                           row["author"], row["date"], row["summary"],
                           row["key_points"], row["image"],
                           row["translated"], row["saved_at"]])
            st.download_button(
                label=lang["export_csv"],
                data=buf.getvalue(),
                file_name="scraping_history.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown("---")

        for item in history:
            res = item["result"]
            if isinstance(res, str):
                res = json.loads(res)

            with st.container(border=True):
                cols = st.columns([1, 4])
                with cols[0]:
                    if res.get("image"):
                        try:
                            st.image(res["image"], width=120)
                        except Exception:
                            pass
                with cols[1]:
                    atype = res.get("article_type", "")
                    type_tag = f" [{atype.upper()}]" if atype else ""
                    st.markdown(f"**{res.get('title', 'N/A')}**{type_tag}")
                    st.caption(f"{item['url']}")
                    st.caption(f"_{lang['saved_at']}: {item['created_at']}_")

                with st.expander(lang["show_details"]):
                    if res.get("image"):
                        try:
                            st.image(res["image"], use_container_width=True)
                        except Exception:
                            pass
                    st.markdown(f"**{lang['author']}:** {res.get('author', 'N/A')}")
                    st.markdown(f"**{lang['date']}:** {res.get('date', 'N/A')}")
                    st.markdown("---")
                    st.markdown(f"**{lang['summary']}:**")
                    st.write(res.get("summary", lang["no_summary"]))

                    kp = res.get("key_points", "")
                    if kp:
                        st.markdown("---")
                        st.markdown(f"**{lang['key_points']}:**")
                        for point in kp.split("\n"):
                            point = point.strip()
                            if point:
                                st.markdown(f"- {point.lstrip('- ')}")

elif st.session_state.page == "about" and st.session_state.user:
    st.markdown(f"# {lang['about_title']}")

    st.markdown(f"## {lang['about_adaptivity_title']}")
    st.markdown(lang["about_adaptivity"])

    st.markdown("---")
    st.markdown(f"## {lang['about_tech']}")

    techs = [
        ("https://img.icons8.com/color/96/python.png", "**Python 3.14 + Uvicorn**", lang["about_tech_python"]),
        ("https://img.icons8.com/color/96/api-settings.png", "**FastAPI**", lang["about_tech_fastapi"]),
        ("https://img.icons8.com/color/96/spider.png", "**Crawl4AI**", lang["about_tech_crawl4ai"]),
        ("https://img.icons8.com/color/96/bot.png", "**DeepSeek V4 (deepseek-chat)**", lang["about_tech_deepseek"]),
        ("https://img.icons8.com/color/96/dashboard.png", "**Streamlit**", lang["about_tech_streamlit"]),
        ("https://img.icons8.com/color/96/database.png", "**SQLite**", lang["about_tech_sqlite"]),
    ]
    for img_url, name, desc in techs:
        with st.container(border=True):
            cols = st.columns([1, 5])
            with cols[0]:
                try:
                    st.image(img_url, width=48)
                except Exception:
                    st.markdown("<div style='width:48px;height:48px'></div>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"{name}  \n{desc}")

    st.markdown("---")
    st.markdown(f"## {lang['about_features_heading']}")
    for i in range(1, 6):
        st.markdown(f"**{i}.** {lang[f'about_feature{i}']}")

    st.markdown("---")
    st.markdown(f"## {lang['about_purpose_title']}")
    st.markdown(lang["about_purpose"])
    st.markdown(lang["about_relevance"])

    st.markdown("---")
    st.markdown(f"## {lang['about_author_title']}")
    with st.container(border=True):
        st.markdown(f"Студент групи {lang['about_author_group']} — {lang['about_author_name']}")
        st.markdown(lang["about_author_institute"])
        st.markdown(f"Спеціальність: {lang['about_author_specialty']}")


