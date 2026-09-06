import pandas as pd
import streamlit as st
from datetime import date
from utils import timed_message

from api_client import APIClient
from session import (initialize_session, is_authenticated, login, logout, get_user, get_token,)


API_BASE_URL = "http://127.0.0.1:8000"

api_client = APIClient(API_BASE_URL)


st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
)

st.title("💰 Expense Tracker")

# Initialize session
initialize_session()

# Restore user object if token exists but user is missing (post-refresh)
if is_authenticated() and get_user() is None:
    try:
        token = get_token()
        user = api_client.get_me(token)
        st.session_state["user"] = user
    except Exception:
        logout()
        st.rerun()


# =========================================================
# Authentication
# =========================================================

if not is_authenticated():

    if "auth_view" not in st.session_state:
        st.session_state["auth_view"] = "login"

    # -----------------------------------------------------
    # Login
    # -----------------------------------------------------

    if st.session_state["auth_view"] == "login":

        st.subheader("Login")

        # Show registration success message if redirected (outside form — safe)
        if st.session_state.get("register_success"):
            timed_message("success", "Registration successful! Please login.")
            st.session_state["register_success"] = False

        # Placeholder for login errors — defined BEFORE form so no form context
        login_msg = st.empty()

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input(
                "Password",
                type="password",
            )

            submitted = st.form_submit_button("Login")

            if submitted:
                if not email or not password:
                    login_msg.error("Please enter email and password.")
                else:
                    try:
                        login_data = api_client.login(
                            email=email,
                            password=password,
                        )

                        token = login_data["access_token"]
                        user = api_client.get_me(token)

                        login(token=token, user=user)
                        st.rerun()

                    except Exception as error:
                        login_msg.error(f"Login failed: {error}")

        st.markdown("---")
        if st.button("New user? Register Here"):
            st.session_state["auth_view"] = "register"
            st.rerun()

    # -----------------------------------------------------
    # Register
    # -----------------------------------------------------

    elif st.session_state["auth_view"] == "register":

        st.subheader("Create Account")

        # Placeholder for register errors — defined BEFORE form so no form context
        register_msg = st.empty()

        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input(
                "Password",
                type="password",
            )

            submitted = st.form_submit_button("Register")

            if submitted:
                if not username or not email or not password:
                    register_msg.error("Please fill in all fields.")
                elif len(password) < 8:
                    register_msg.error("Password must be at least 8 characters.")
                else:
                    try:
                        api_client.register(
                            username=username,
                            email=email,
                            password=password,
                        )

                        # Store flag, then redirect to login
                        st.session_state["register_success"] = True
                        st.session_state["auth_view"] = "login"
                        st.rerun()

                    except Exception as error:
                        register_msg.error(f"Registration failed: {error}")

        st.markdown("---")
        if st.button("Already have an account? Login Here"):
            st.session_state["auth_view"] = "login"
            st.rerun()


# =========================================================
# Logged-in application
# =========================================================

else:

    user = get_user()

    # =====================================================
    # Header
    # =====================================================

    header_col1, header_col2 = st.columns([6, 1])

    with header_col1:
        st.caption(
            f"Welcome back, {user['username']}!"
        )

    with header_col2:
        st.write("")
        st.write("")

        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

    st.divider()

    # =====================================================
    # Summary Cards
    # =====================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="💰 Wallet Balance",
            value="₹0",
        )

    with col2:
        st.metric(
            label="💸 Total Expenses",
            value="₹0",
        )

    with col3:
        st.metric(
            label="📥 Total Funds",
            value="₹0",
        )

    st.divider()

    # =====================================================
    # Main Navigation
    # =====================================================

    st.subheader("Dashboard")

    expenses_tab, funds_tab, summary_tab = st.tabs(
        [
            "💸 Expenses",
            "📥 Funds",
            "📊 Summary",
        ]
    )

    # -----------------------------------------------------
    # Expenses
    # -----------------------------------------------------

    with expenses_tab:
        st.subheader("Expenses")

        # -----------------------------------------------------
        # Add Expense
        # -----------------------------------------------------

        st.markdown("### Add Expense")

        with st.form("add_expense_form"):

            expense_date = st.date_input(
                "Date"
            )

            amount = st.number_input(
                "Amount",
                min_value=1,
                step=1,
            )

            category = st.text_input(
                "Category"
            )

            subcategory = st.text_input(
                "Subcategory"
            )

            note = st.text_area(
                "Note"
            )

            submitted = st.form_submit_button(
                "Add Expense"
            )

            if submitted:

                if not category:
                    st.error("Please enter a category.")

                else:
                    try:
                        token = get_token()

                        api_client.create_expense(
                            token=token,
                            date=expense_date.isoformat(),
                            amount=amount,
                            category=category,
                            subcategory=subcategory,
                            note=note,
                        )

                        st.success("Expense added successfully!")

                    except Exception as error:
                        st.error(
                            f"Failed to add expense: {error}"
                        )

        # -----------------------------------------------------
        # Expense Filters
        # -----------------------------------------------------

        st.markdown("### Filters")

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            start_date = st.date_input(
                "Start Date",
                value=None,
            )

        with filter_col2:
            end_date = st.date_input(
                "End Date",
                value=None,
            )

        with filter_col3:
            category_filter = st.text_input(
                "Category",
                placeholder="e.g. Food",
            )

        # -------------------------------------------------
        # Expense List (Editable Table with Delete)
        # -------------------------------------------------

        st.markdown("### Expense History")

        expenses = []

        try:
            token = get_token()

            expenses = api_client.get_expenses(
                token=token,
                start_date=start_date.isoformat() if start_date else None,
                end_date=end_date.isoformat() if end_date else None,
                category=category_filter or None,
            )

            if expenses:
                df = pd.DataFrame(expenses)
                display_df = df.copy()
                display_df = display_df.sort_values(by=["date", "id"], ascending=[False, False],).reset_index(drop=True)
                display_df["delete"] = False

                edited_df = st.data_editor(
                    display_df,
                    width="stretch",
                    hide_index=True,
                    disabled=["id"],
                    num_rows="fixed",
                    column_order=["id", "date", "amount", "category", "subcategory", "note", "delete"],
                    column_config={
                        "id": st.column_config.NumberColumn("ID"),
                        "date": st.column_config.TextColumn("Date"),
                        "amount": st.column_config.NumberColumn("Amount (₹)", min_value=1, step=1),
                        "category": st.column_config.TextColumn("Category"),
                        "subcategory": st.column_config.TextColumn("Subcategory"),
                        "note": st.column_config.TextColumn("Note"),
                        "delete": st.column_config.CheckboxColumn("🗑️", default=False),
                        "user_id": None,
                        "created_at": None,
                        "updated_at": None,
                    },
                )

                save_msg = st.empty()
                delete_msg = st.empty()

                # --- Save edits ---
                data_columns = ["date", "amount", "category", "subcategory", "note"]
                changed_rows = edited_df[data_columns].compare(display_df[data_columns])

                if not changed_rows.empty:
                    st.caption("⚠️ You have unsaved changes. Click **Save Changes** to apply.")

                    if st.button("💾 Save Changes", type="primary"):
                        try:
                            token = get_token()
                            for idx in changed_rows.index.tolist():
                                row = edited_df.iloc[idx]
                                api_client.update_expense(
                                    token=token,
                                    expense_id=int(row["id"]),
                                    date=row["date"],
                                    amount=int(row["amount"]),
                                    category=row["category"],
                                    subcategory=row["subcategory"] or "",
                                    note=row["note"] or "",
                                )
                            save_msg.success("Changes saved successfully!")
                            st.rerun()
                        except Exception as error:
                            save_msg.error(f"Failed to save changes: {error}")

                # --- Handle deletions ---
                rows_to_delete = edited_df[edited_df["delete"] == True]

                if not rows_to_delete.empty:
                    ids_to_delete = rows_to_delete["id"].tolist()
                    labels = ", ".join(
                        f"#{int(r['id'])} {r['category']} ₹{r['amount']}"
                        for _, r in rows_to_delete.iterrows()
                    )

                    st.warning(
                        f"⚠️ Marked for deletion: **{labels}**. "
                        f"This is permanent and cannot be undone."
                    )

                    confirm_col1, confirm_col2, _ = st.columns([1.2, 1, 5])

                    with confirm_col1:
                        if st.button("🗑️ Confirm Delete", type="primary"):
                            try:
                                token = get_token()
                                for expense_id in ids_to_delete:
                                    api_client.delete_expense(
                                        token=token,
                                        expense_id=int(expense_id),
                                    )
                                delete_msg.success("Expense(s) deleted successfully!")
                                st.rerun()
                            except Exception as error:
                                delete_msg.error(f"Failed to delete: {error}")

                    with confirm_col2:
                        if st.button("❌ Cancel"):
                            st.rerun()

            else:
                st.info("No expenses found for the selected filters.")

        except Exception as error:
            st.error(f"Failed to load expenses: {error}")

    # -----------------------------------------------------
    # Funds
    # -----------------------------------------------------

    with funds_tab:
        st.subheader("Funds")

        st.info(
            "Fund management will be implemented next."
        )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    with summary_tab:
        st.subheader("Summary")

        st.info(
            "Expense summaries will be implemented next."
        )