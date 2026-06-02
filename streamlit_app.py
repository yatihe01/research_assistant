from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from research_assistant.graph import process_new_idea


st.set_page_config(page_title="Research Assistant", page_icon=":memo:")

st.title("Research Assistant")


idea_text = st.text_area(
    "New idea",
    height=220,
    placeholder="Paste a research idea to summarize and save.",
)

if st.button("Save idea", type="primary", disabled=not idea_text.strip()):
    try:
        result = process_new_idea(idea_text)
    except Exception as exc:
        st.error(f"Could not save idea: {exc}")
    else:
        summary = result["summary"]
        st.success(f"Saved {result['persisted_idea_id']}")
        st.subheader(summary["title"])
        st.write(summary["statement"])
        st.markdown("**Critic notes**")
        st.write(result["critique"])

        with st.expander("Base-paper context"):
            base_context = result.get("base_context") or ["No base-paper context retrieved."]
            for chunk in base_context:
                st.write(chunk)

        with st.expander("Literature"):
            literature = result.get("literature") or []
            if not literature:
                st.write("No literature retrieved.")
            for paper in literature:
                title = paper.get("title", "Untitled paper")
                url = paper.get("url")
                year = paper.get("year") or "n.d."
                source = paper.get("source", "source")
                if url:
                    st.markdown(f"**[{title}]({url})** ({year}, {source})")
                else:
                    st.markdown(f"**{title}** ({year}, {source})")
                st.write(paper.get("abstract_snippet", ""))
