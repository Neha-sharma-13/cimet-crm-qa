import streamlit as st
import pandas as pd
import re

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CIMET - CRM QA Automation",
    page_icon="✅",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.title("CRM QA Automation")
st.caption(
    "Automatically score a CRM sale against retailer QA checks "
    "before submission."
)

# ============================================================
# MOCK CRM DATA
# ============================================================

lead = {
    "Lead ID": "DEMO-1001",
    "Customer Name": "Rahul Sharma",
    "Email": "rahul.sharma@example.com",
    "Plan": "Premium",
    "Rate": 599
}

# ============================================================
# MOCK CALL TRANSCRIPT
# ============================================================

transcript = """
[00:01] Agent: Hello Rahul, thank you for choosing our service.

[00:08] Agent: Before we continue, I need to inform you that
this call may be recorded.

[00:18] Agent: Your Premium plan costs 599 rupees per month.

[00:30] Customer: Yes, that is correct.

[00:35] Agent: Can I confirm that your email is
rahul.sharma@example.com?

[00:45] Customer: Yes, that's correct.
"""

# ============================================================
# MOCK RETAILER CHECK LIBRARY
# ============================================================

check_library = [
    {
        "check_id": "CHK001",
        "check_name": "Required recording disclaimer",
        "check_type": "Verbatim",
        "severity": "CRITICAL",
        "expected": "call may be recorded"
    },
    {
        "check_id": "CHK002",
        "check_name": "Correct plan rate communicated",
        "check_type": "Factual",
        "severity": "CRITICAL",
        "expected": "599"
    },
    {
        "check_id": "CHK003",
        "check_name": "Customer email confirmed",
        "check_type": "Factual",
        "severity": "CRITICAL",
        "expected": "rahul.sharma@example.com"
    }
]

# ============================================================
# QA FUNCTIONS
# ============================================================

def find_evidence(transcript, expected):
    """
    Find the first transcript line containing the expected value.
    """

    for line in transcript.splitlines():

        if expected.lower() in line.lower():

            timestamp_match = re.search(
                r"\[(.*?)\]",
                line
            )

            timestamp = (
                timestamp_match.group(1)
                if timestamp_match
                else "Unknown"
            )

            return line.strip(), timestamp

    return None, None


def run_check(check, transcript):

    evidence, timestamp = find_evidence(
        transcript,
        check["expected"]
    )

    if evidence:

        return {
            "Check ID": check["check_id"],
            "Check": check["check_name"],
            "Type": check["check_type"],
            "Severity": check["severity"],
            "Status": "PASS",
            "Expected": check["expected"],
            "Evidence": evidence,
            "Timestamp": timestamp
        }

    else:

        return {
            "Check ID": check["check_id"],
            "Check": check["check_name"],
            "Type": check["check_type"],
            "Severity": check["severity"],
            "Status": "FAIL",
            "Expected": check["expected"],
            "Evidence": "Expected information not found.",
            "Timestamp": "N/A"
        }


# ============================================================
# LEAD INFORMATION
# ============================================================

st.header("1. Lead Information")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Lead ID",
    lead["Lead ID"]
)

col2.metric(
    "Customer",
    lead["Customer Name"]
)

col3.metric(
    "Plan",
    lead["Plan"]
)

col4.metric(
    "Rate",
    f"₹{lead['Rate']}"
)

st.divider()

# ============================================================
# TRANSCRIPT
# ============================================================

st.header("2. Call Transcript")

st.text_area(
    "Transcript",
    transcript,
    height=250
)

st.divider()

# ============================================================
# CHECK LIBRARY
# ============================================================

st.header("3. Retailer Check Library")

check_library_df = pd.DataFrame(check_library)

st.dataframe(
    check_library_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ============================================================
# RUN QA
# ============================================================

st.header("4. Automated QA")

if st.button(
    "▶ Run QA Check",
    type="primary",
    use_container_width=True
):

    results = []

    for check in check_library:

        result = run_check(
            check,
            transcript
        )

        results.append(result)

    results_df = pd.DataFrame(results)

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    st.subheader("Check Results")

    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # COUNTS
    # --------------------------------------------------------

    total_checks = len(results_df)

    passed = len(
        results_df[
            results_df["Status"] == "PASS"
        ]
    )

    failed = len(
        results_df[
            results_df["Status"] == "FAIL"
        ]
    )

    critical_failures = len(
        results_df[
            (results_df["Status"] == "FAIL")
            &
            (results_df["Severity"] == "CRITICAL")
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Checks",
        total_checks
    )

    col2.metric(
        "Passed",
        passed
    )

    col3.metric(
        "Failed",
        failed
    )

    col4.metric(
        "Critical Failures",
        critical_failures
    )

    # --------------------------------------------------------
    # FINAL GATE
    # --------------------------------------------------------

    st.subheader("5. Final Gate")

    if critical_failures > 0:

        st.error(
            "🔴 HOLD — Critical QA failure detected"
        )

        st.write(
            "The sale must not be submitted automatically."
        )

    else:

        st.success(
            "🟢 AUTO-SUBMIT — All critical checks passed"
        )

        st.write(
            "The sale can proceed to submission."
        )