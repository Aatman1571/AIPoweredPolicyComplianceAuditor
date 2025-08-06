import os
import streamlit as st
import json
from fpdf import FPDF
from policy_audit import run_policy_pipeline
import textwrap
import matplotlib.pyplot as plt

UPLOAD_DIR = "dashboard_uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Streamlit Page Config
st.set_page_config(page_title="Policy Compliance Auditor", layout="wide")
st.title("🛡️ Policy Compliance Auditor")

uploaded_file = st.file_uploader("📄 Upload a policy document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

frameworks = st.multiselect(
    "🧩 Select Compliance Framework(s)",
    ["ISO", "NIST", "CIS"],
    default=["ISO", "NIST", "CIS"]
)

def wrap_text(text, width=100):
    """Wrap long text into multiple lines for PDF rendering."""
    if not text:
        return ""
    return "\n".join(textwrap.wrap(text, width))

def sanitize_text(text):
    """Remove unsupported Unicode characters for PDF."""
    if not isinstance(text, str):
        return ""
    return (
        text.replace("•", "-")       # Replace bullet with dash
            .replace("’", "'")       # Replace curly apostrophe with straight one
            .replace("“", '"')       # Replace left quote
            .replace("”", '"')       # Replace right quote
            .replace("→", "->")      # Replace arrow
            .encode("ascii", "ignore")
            .decode("ascii")
    )

# PDF Export Function
def export_report_to_pdf(report):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(190, 10, txt="Policy Compliance Audit Report", ln=True, align="C")
    pdf.ln(8)

    # Policy Summary
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(190, 8, sanitize_text(f"Policy: {report.get('policy', 'N/A')}"), ln=True)
    summary = report.get("summary", {})
    pdf.cell(190, 8, sanitize_text(f"Score: {summary.get('score', 0)} / {summary.get('total', 0)}"), ln=True)
    pdf.cell(190, 8, sanitize_text(f"Compliance %: {summary.get('percentage', 0)}%"), ln=True)
    pdf.cell(190, 8, sanitize_text(f"Grade: {summary.get('grade', 'N/A')}"), ln=True)
    pdf.ln(6)

    # Matched Controls
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Matched Controls:", ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", size=10)
    for m in report.get("mappings", []):
        pdf.cell(190, 6, sanitize_text(f"{m['source']} - {m['id']}"), ln=True)
        pdf.multi_cell(190, 6, sanitize_text(f"Control: {wrap_text(m['text'])}"))
        for s in m.get("sentences", []):
            pdf.set_x(10)
            pdf.multi_cell(190, 6, sanitize_text(f"- {wrap_text(s)}"))
        pdf.ln(3)

    # Gaps
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Gaps:", ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", size=10)
    for g in report.get("gaps", []):
        pdf.cell(190, 6, sanitize_text(f"{g['source']} - {g['control_id']} -> {g['coverage']}"), ln=True)
        pdf.multi_cell(190, 6, sanitize_text(f"Justification: {wrap_text(g['justification'])}"))
        pdf.ln(3)

    # Remediations
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Remediation Suggestions:", ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", size=10)
    for r in report.get("remediations", []):
        pdf.cell(190, 6, sanitize_text(f"{r['source']} - {r['control_id']}"), ln=True)
        remediation_text = r.get("remediation", "")
        if isinstance(remediation_text, dict):
            remediation_text = remediation_text.get("suggestion", "")
        pdf.multi_cell(190, 6, sanitize_text(f"Suggestion: {wrap_text(remediation_text)}"))
        pdf.ln(3)

    pdf_path = os.path.join(OUTPUT_DIR, "audit_report.pdf")
    pdf.output(pdf_path)
    return pdf_path


# Main App Logic
if uploaded_file and frameworks:
    filename = uploaded_file.name
    uploaded_path = os.path.join(UPLOAD_DIR, filename)

    with open(uploaded_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🚀 Run Audit"):
        stage_box = st.empty()
        stage_box.info("🔍 Starting audit...")

        try:
            report_path = run_policy_pipeline(uploaded_path, frameworks, status_box=stage_box)
        except Exception as e:
            st.error(f"❌ Audit failed: {e}")
            st.stop()

        if report_path and os.path.exists(report_path):
            st.success("✅ Audit completed successfully!")
            st.divider()
            st.subheader("📊 Audit Results")

            with open(report_path, encoding="utf-8") as f:
                report = json.load(f)

            # ---- Visualizations ----
            st.markdown("### 📌 Compliance Overview")

            summary = report.get("summary", {})
            gaps = report.get("gaps", [])
            mappings = report.get("mappings", [])

            score = summary.get("score", 0)
            total = summary.get("total", 1)
            percentage = summary.get("percentage", 0)

            # Small charts in columns
            col1, col2, col3 = st.columns(3)

            with col1:
                fig, ax = plt.subplots(figsize=(2, 2))
                ax.bar(["Compliance"], [percentage], color="green" if percentage >= 70 else "orange")
                ax.set_ylim(0, 100)
                ax.set_ylabel("%", fontsize=8)
                ax.set_title("Compliance", fontsize=10)
                ax.tick_params(axis='y', labelsize=7)
                st.pyplot(fig, use_container_width=False)

            with col2:
                matched_count = len(mappings)
                gaps_count = len(gaps)
                labels = ['Matched', 'Gaps']
                sizes = [matched_count, gaps_count]
                colors = ['#4CAF50', '#F44336']

                fig_pie, ax_pie = plt.subplots(figsize=(2, 2))
                ax_pie.pie(sizes, labels=labels, autopct='%1.0f%%', colors=colors, textprops={'fontsize': 7})
                ax_pie.set_title("Matched vs Gaps", fontsize=10)
                st.pyplot(fig_pie, use_container_width=False)

            with col3:
                gap_sources = [g["source"] for g in gaps] if gaps else []
                if gap_sources:
                    gap_counts = {src: gap_sources.count(src) for src in set(gap_sources)}

                    fig2, ax2 = plt.subplots(figsize=(2, 2))
                    ax2.bar(gap_counts.keys(), gap_counts.values(), color="red")
                    ax2.set_ylabel("Gaps", fontsize=7)
                    ax2.set_title("Gaps by Framework", fontsize=10)
                    ax2.tick_params(axis='x', labelsize=7)
                    ax2.tick_params(axis='y', labelsize=7)
                    st.pyplot(fig2, use_container_width=False)

            st.divider()

            # ---- Tabs for Details ----
            tabs = st.tabs(["✅ Matched Controls", "🚨 Gap Analysis", "📈 Compliance Score", "🛠️ Remediations"])

            with tabs[0]:
                st.markdown("### ✅ Matched Controls")
                if not mappings:
                    st.warning("No controls matched.")
                else:
                    for m in mappings:
                        label = f"{m['source']} - {m['id']} → {len(m.get('sentences', []))} sentence(s)"
                        with st.expander(label):
                            st.markdown("**Control:**")
                            st.code(m["text"], language="markdown")
                            st.markdown("**Matched Sentences:**")
                            for s in m.get("sentences", []):
                                st.write(f"• {s}")

            with tabs[1]:
                st.markdown("### 🚨 Gaps Found")
                if not gaps:
                    st.success("No gaps found!")
                else:
                    for g in gaps:
                        st.markdown(f"**{g['source']} - {g['control_id']}** → `{g['coverage']}`")
                        st.markdown(f"<p style='color:black;'><strong>Justification:</strong> {g['justification']}</p>", unsafe_allow_html=True)

            with tabs[2]:
                st.markdown("### 📈 Compliance Score")
                st.metric("Score", f"{score} / {total}")
                st.metric("Compliance %", f"{percentage}%")
                st.metric("Grade", summary.get("grade", "N/A"))

            with tabs[3]:
                st.markdown("### 🛠️ Remediation Suggestions")
                remediations = report.get("remediations", [])
                if not remediations:
                    st.success("No remediations needed!")
                else:
                    for r in remediations:
                        st.markdown(f"**{r['source']} - {r['control_id']}**")
                        st.markdown(f"<p style='color:black;'><strong>Suggestion:</strong> {r['remediation']}</p>", unsafe_allow_html=True)

            # PDF Export
            pdf_path = export_report_to_pdf(report)
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 Export & Download PDF Report",
                    data=pdf_file,
                    file_name="audit_report.pdf",
                    mime="application/pdf"
                )

        else:
            st.error("❌ Failed to complete audit. Check console/logs.")
