"""
Streamlit GUI for testing the Appraisal Reporting System backend.
"""
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Appraisal System Test GUI")

if 'token' not in st.session_state:
    st.session_state['token'] = None
if 'role' not in st.session_state:
    st.session_state['role'] = None

# Initialize widget states if they don't exist
if 'reg_manager_id' not in st.session_state:
    st.session_state['reg_manager_id'] = 1 # Default value from input
if 'login_user' not in st.session_state:
    st.session_state['login_user'] = ""
if 'login_pass' not in st.session_state:
    st.session_state['login_pass'] = ""
if 'hr_report_empid' not in st.session_state:
    st.session_state['hr_report_empid'] = 1 # Default value from input
if 'admin_userid' not in st.session_state:
    st.session_state['admin_userid'] = 1 # Default value from input

menu = st.sidebar.selectbox("Menu", ["Register", "Login", "Employee Appraisals", "Manager Review", "HR Reports", "Reports", "Profile", "Admin", "Logout"])
headers = {"Authorization": f"Bearer {st.session_state['token']}"} if st.session_state['token'] else {}

if menu == "Register":
    st.header("Register User")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Employee", "Manager", "HR", "Admin"])
    manager_id = st.number_input("Manager ID (optional, required for Employee)", min_value=1, step=1, key="reg_manager_id") # Use session state value
    department_id = None
    department_options = []
    if role in ("Employee", "Manager"):
        resp = requests.get(f"{API_URL}/departments/public")
        if resp.status_code == 200:
            departments = resp.json()
            department_options = [(d['id'], d['name']) for d in departments]
            dept_names = [d['name'] for d in departments]
            if dept_names:
                selected = st.selectbox("Department (required)", dept_names)
                department_id = next((d[0] for d in department_options if d[1] == selected), None)
            else:
                st.warning("No departments available. Please contact HR.")
        else:
            st.warning("Could not fetch departments.")
    if st.button("Register"):
        data = {"username": username, "password": password, "role": role}
        if manager_id:
            data["manager_id"] = manager_id
        if department_id:
            data["department_id"] = department_id
        resp = requests.post(f"{API_URL}/auth/register", json=data)
        if resp.status_code == 200:
            st.success("Registered! Now login.")
        else:
            st.error(resp.json().get("detail", "Registration failed"))

elif menu == "Login":
    st.header("Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        resp = requests.post(f"{API_URL}/auth/token", data={"username": username, "password": password})
        if resp.status_code == 200:
            st.session_state['token'] = resp.json()['access_token']
            # Get user role (simulate by registering and logging in)
            st.success("Login successful!")
        else:
            st.error("Login failed")

elif menu == "Employee Appraisals":
    st.header("Employee: Submit/View Appraisals")
    if not st.session_state['token']:
        st.warning("Please login first.")
    else:
        # Submit appraisal with attachment
        with st.form("submit_appraisal_form", clear_on_submit=True):
            period = st.text_input("Period (e.g., 2024-Q1)")
            self_review = st.text_area("Self Review")
            attachment = st.file_uploader("Attach Document (PDF, Excel, CSV)", type=["pdf", "xlsx", "xls", "csv"])
            submitted = st.form_submit_button("Submit Appraisal")
            if submitted:
                files = {}
                data = {"period": period, "self_review": self_review}
                if attachment is not None:
                    files = {"attachment": (attachment.name, attachment, attachment.type)}

                # Send as multipart/form-data
                resp = requests.post(f"{API_URL}/appraisals/", data=data, files=files, headers=headers)

                if resp.status_code == 200:
                    st.success("Appraisal submitted!")
                else:
                    st.error(resp.json().get("detail", "Submission failed"))

        # List my appraisals
        st.subheader("My Submitted Appraisals")
        if st.button("View My Appraisals"):
            resp = requests.get(f"{API_URL}/appraisals/my", headers=headers)
            if resp.status_code == 200:
                appraisals_data = resp.json()
                if not appraisals_data:
                    st.info("No appraisals submitted yet.")
                for ap in appraisals_data:
                    st.markdown(f"**ID:** {ap['id']}, **Period:** {ap['period']}, **Status:** {ap['status']}")
                    st.text_area("Self Review", value=ap.get('self_review', ''), key=f"my_self_{ap['id']}", disabled=True)
                    st.text_area("Manager Review", value=ap.get('manager_review', ''), key=f"my_mgr_{ap['id']}", disabled=True)
                    if ap.get('attachment_filename'):
                        st.markdown(f"**Attachment:** {ap['attachment_filename']}")
                        # Provide download link (Streamlit doesn't directly support button for GET request with headers easily)
                        # We construct the URL and let the user click it. Browser handles download.
                        # NOTE: This assumes the user is logged in the browser session where Streamlit runs,
                        # which might not be true if API/Streamlit are separate. A proper solution might need
                        # Streamlit to proxy the download request with the token.
                        # For this test GUI, we'll provide the link.
                        download_url = f"{API_URL}/appraisals/{ap['id']}/attachment"
                        st.markdown(f"[Download Attachment]({download_url}) (Requires login token in request)")
                        # Alternative: Button that triggers backend call (more complex state needed)
                    st.divider()
            else:
                st.error(resp.json().get("detail", "Submission failed"))
        # List my appraisals
        if st.button("View My Appraisals"):
            resp = requests.get(f"{API_URL}/appraisals/my", headers=headers)
            if resp.status_code == 200:
                for ap in resp.json():
                    st.write(ap)
            else:
                st.error(f"Could not fetch appraisals: {resp.status_code} {resp.text}")

elif menu == "Manager Review":
    st.header("Manager: Review Team Appraisals")
    if not st.session_state['token']:
        st.warning("Please login first.")
    else:
        if st.button("List Team Appraisals"):
            resp = requests.get(f"{API_URL}/appraisals/team", headers=headers)
            if resp.status_code == 200:
                appraisals_data = resp.json()
                if not appraisals_data:
                    st.info("No appraisals found for your team.")
                for ap in appraisals_data:
                    st.markdown(f"**ID:** {ap['id']}, **Employee ID:** {ap['employee_id']}, **Period:** {ap['period']}, **Status:** {ap['status']}")
                    st.text_area("Self Review", value=ap.get('self_review', ''), key=f"team_self_{ap['id']}", disabled=True)
                    if ap.get('attachment_filename'):
                        st.markdown(f"**Attachment:** {ap['attachment_filename']}")
                        download_url = f"{API_URL}/appraisals/{ap['id']}/attachment"
                        st.markdown(f"[Download Attachment]({download_url}) (Requires login token in request)")
                    with st.form(key=f"review_{ap['id']}"):
                        manager_review = st.text_area("Manager Review", value=ap.get("manager_review", ""), key=f"mgr_review_text_{ap['id']}")
                        status = st.selectbox("Status", ["pending", "reviewed"], index=0 if ap['status']=="pending" else 1, key=f"mgr_status_{ap['id']}")
                        submit = st.form_submit_button("Update Review")
                        if submit:
                            data = {"manager_review": manager_review, "status": status}
                            r = requests.patch(f"{API_URL}/appraisals/{ap['id']}", json=data, headers=headers)
                            if r.status_code == 200:
                                st.success("Updated!")
                            else:
                                st.error(f"Update failed: {r.status_code} {r.text}")
                    st.divider()
            else:
                st.error(f"Could not fetch team appraisals: {resp.status_code} {resp.text}")

elif menu == "Reports": # This section seems redundant with "HR Reports", maybe consolidate later?
    st.header("Reports (Manager/HR)")
    if not st.session_state['token']:
        st.warning("Please login first.")
    else:
        # Manager team report download
        st.subheader("Manager: Download Team Report")
        report_format = st.radio("Download format", ["PDF", "JSON"], horizontal=True, key="mgr_report_format")
        if st.button("Download Team Report"):
            fmt = "pdf" if report_format == "PDF" else "json"
            resp = requests.get(f"{API_URL}/appraisals/team/report?format={fmt}", headers=headers)
            if resp.status_code == 200:
                if fmt == "pdf":
                    st.download_button("Download PDF", resp.content, file_name="team_appraisal_report.pdf")
                else:
                    import json
                    st.download_button("Download JSON", json.dumps(resp.json(), indent=2), file_name="team_appraisal_report.json")
            else:
                st.error("Not a manager or failed to fetch team report.")
        # Show team appraisals as JSON
        if st.button("Show My Team Reports (Manager)"):
            resp = requests.get(f"{API_URL}/appraisals/team", headers=headers)
            if resp.status_code == 200:
                st.write("Team Appraisals:")
                for ap in resp.json():
                    st.json(ap)
            else:
                st.error("Not a manager or failed to fetch.")
        st.subheader("HR: All Reports")
        if st.button("Show All Reports (HR)"):
            resp = requests.get(f"{API_URL}/hr/appraisals", headers=headers)
            if resp.status_code == 200:
                appraisals_data = resp.json()
                st.write("All Appraisals:")
                if not appraisals_data:
                    st.info("No appraisals found.")
                for ap in appraisals_data:
                    st.markdown(f"**ID:** {ap['id']}, **Employee ID:** {ap['employee_id']}, **Period:** {ap['period']}, **Status:** {ap['status']}")
                    if ap.get('attachment_filename'):
                         st.markdown(f"**Attachment:** {ap['attachment_filename']}")
                         download_url = f"{API_URL}/appraisals/{ap['id']}/attachment"
                         st.markdown(f"[Download Attachment]({download_url}) (Requires login token in request)")
                    st.json(ap) # Keep full JSON view for now
                    st.divider()
            else:
                st.error(f"Not HR or failed to fetch: {resp.status_code} {resp.text}")

elif menu == "HR Reports":
    st.header("HR: All Appraisals & Reports")
    if not st.session_state['token']:
        st.warning("Please login first.")
    else:
        st.subheader("Department Management")
        # List departments
        resp = requests.get(f"{API_URL}/departments/", headers=headers)
        if resp.status_code == 200:
            departments = resp.json()
            for d in departments:
                st.write(f"{d['id']}: {d['name']} - {d.get('description','')}")
                if st.button(f"Delete Department {d['id']}"):
                    del_resp = requests.delete(f"{API_URL}/departments/{d['id']}", headers=headers)
                    if del_resp.status_code == 200:
                        st.success("Department deleted.")
                    else:
                        st.error("Delete failed.")
        # Add department
        with st.form("add_dept_form"):
            dept_name = st.text_input("New Department Name")
            dept_desc = st.text_input("Description")
            submit = st.form_submit_button("Add Department")
            if submit and dept_name:
                resp = requests.post(f"{API_URL}/departments/", json={"name": dept_name, "description": dept_desc}, headers=headers)
                if resp.status_code == 200:
                    st.success("Department added!")
                else:
                    st.error("Failed to add department.")
        st.subheader("Appraisals & Reports")
        if st.button("List All Appraisals"):
            resp = requests.get(f"{API_URL}/hr/appraisals", headers=headers)
            if resp.status_code == 200:
                appraisals_data = resp.json()
                if not appraisals_data:
                    st.info("No appraisals found.")
                for ap in appraisals_data:
                    st.markdown(f"**ID:** {ap['id']}, **Employee ID:** {ap['employee_id']}, **Period:** {ap['period']}, **Status:** {ap['status']}")
                    st.text_area("Self Review", value=ap.get('self_review', ''), key=f"hr_self_{ap['id']}", disabled=True)
                    st.text_area("Manager Review", value=ap.get('manager_review', ''), key=f"hr_mgr_{ap['id']}", disabled=True)
                    if ap.get('attachment_filename'):
                        st.markdown(f"**Attachment:** {ap['attachment_filename']}")
                        download_url = f"{API_URL}/appraisals/{ap['id']}/attachment"
                        st.markdown(f"[Download Attachment]({download_url}) (Requires login token in request)")
                    st.divider()
            else:
                st.error(f"Could not fetch appraisals: {resp.status_code} {resp.text}")
        employee_id = st.number_input("Employee ID for Report", min_value=1, step=1, key="hr_report_empid") # Use session state value
        report_format = st.radio("Download format", ["PDF", "JSON"], horizontal=True, key="hr_report_radio")
        if st.button("Download Employee Report"):
            fmt = "pdf" if report_format == "PDF" else "json"
            resp = requests.get(f"{API_URL}/hr/appraisals/{employee_id}/report?format={fmt}", headers=headers)
            if resp.status_code == 200:
                if fmt == "pdf":
                    st.download_button("Download PDF", resp.content, file_name=f"employee_{employee_id}_report.pdf")
                else:
                    import json
                    st.download_button("Download JSON", json.dumps(resp.json(), indent=2), file_name=f"employee_{employee_id}_report.json")
            else:
                st.error("Could not generate report")

elif menu == "Profile":
    st.header("My Profile")
    if not st.session_state['token']:
        st.warning("Please login first.")
    else:
        resp = requests.get(f"{API_URL}/admin/profile", headers=headers)
        if resp.status_code == 200:
            st.json(resp.json())
        else:
            st.error("Could not fetch profile.")

elif menu == "Admin":
    st.header("Admin Dashboard")
    if not st.session_state['token']:
        st.warning("Please login first.")
    else:
        # List users
        if st.button("List All Users"):
            resp = requests.get(f"{API_URL}/admin/users", headers=headers)
            if resp.status_code == 200:
                users = resp.json()
                for user in users:
                    st.write(f"User #{user['id']}: {user['username']} ({user['role']})")
                    with st.expander("Details", expanded=False):
                        st.json(user)
                        if st.button(f"Delete User {user['id']}"):
                            del_resp = requests.delete(f"{API_URL}/admin/users/{user['id']}", headers=headers)
                            if del_resp.status_code == 200:
                                st.success("User deleted.")
                            else:
                                st.error("Delete failed.")
            else:
                st.error("Not admin or failed to fetch users.")
        # View user by ID
        user_id = st.number_input("User ID to View/Edit", min_value=1, step=1, key="admin_userid") # Use session state value
        if st.button("View User"):
            resp = requests.get(f"{API_URL}/admin/users/{user_id}", headers=headers)
            if resp.status_code == 200:
                st.json(resp.json())
            else:
                st.error("User not found or not admin.")

elif menu == "Logout":
    st.session_state['token'] = None
    st.session_state['role'] = None
    st.success("Logged out.")
