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

    wallet_data = None

    try:
        token = get_token()
        wallet_data = api_client.get_wallet_balance(token)
    except Exception as error:
        st.error(f"Failed to load wallet summary: {error}")

    col1, col2, col3, col4 = st.columns(4)

    if wallet_data:
        total_funds = wallet_data["total_funds"]
        total_expenses = wallet_data["total_expenses"]
        wallet_balance = wallet_data["wallet_balance"]
        wallet_status = wallet_data["status"]
        wallet_warning = wallet_data["warning"]

        if wallet_status == "healthy":
            health_label = "✅ Healthy"
            health_delta = "Good Standing"
        elif wallet_status == "low_balance":
            health_label = "⚠️ Low Balance"
            health_delta = wallet_warning or "Balance getting low"
        elif wallet_status == "overdrawn":
            health_label = "🚨 Overdrawn"
            health_delta = wallet_warning or "Balance is negative"
        else:
            health_label = "—"
            health_delta = ""

        with col1:
            st.metric(label="📥 Total Funds", value=f"₹{total_funds:,}")

        with col2:
            st.metric(label="💸 Total Expenses", value=f"₹{total_expenses:,}")

        with col3:
            st.metric(label="💰 Wallet Balance", value=f"₹{wallet_balance:,}")

        with col4:
            st.metric(label="🏦 Acc Health", value=health_label, delta=health_delta)

    else:
        with col1:
            st.metric(label="📥 Total Funds", value="₹0")

        with col2:
            st.metric(label="💸 Total Expenses", value="₹0")

        with col3:
            st.metric(label="💰 Wallet Balance", value="₹0")

        with col4:
            st.metric(label="🏦 Acc Health", value="—")


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
                        st.rerun()

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

        # -------------------------------------------------
        # Add Fund
        # -------------------------------------------------

        st.markdown("### Add Fund")

        add_fund_msg = st.empty()

        with st.form("add_fund_form"):
            fund_date = st.date_input("Date", value=date.today())
            fund_amount = st.number_input("Amount", min_value=1, step=1)
            source_type = st.selectbox(
                "Source Type",
                options=["salary", "refund", "cash", "petty", "other"],
            )
            fund_note = st.text_area("Note")
            submitted = st.form_submit_button("Add Fund")

            if submitted:
                try:
                    token = get_token()
                    api_client.create_fund(
                        token=token,
                        date=fund_date.isoformat(),
                        amount=fund_amount,
                        source_type=source_type,
                        note=fund_note,
                    )
                    add_fund_msg.success("Fund added successfully!")
                    st.rerun()
                except Exception as error:
                    add_fund_msg.error(f"Failed to add fund: {error}")

        # -------------------------------------------------
        # Fund Filters
        # -------------------------------------------------

        st.markdown("### Filters")

        fund_filter_col1, fund_filter_col2, fund_filter_col3 = st.columns(3)

        with fund_filter_col1:
            fund_start_date = st.date_input(
                "Start Date",
                value=None,
                key="fund_start_date",
            )

        with fund_filter_col2:
            fund_end_date = st.date_input(
                "End Date",
                value=None,
                key="fund_end_date",
            )

        with fund_filter_col3:
            source_type_filter = st.selectbox(
                "Source Type",
                options=["All", "salary", "refund", "cash", "petty", "other"],
                key="fund_source_type_filter",
            )

        # -------------------------------------------------
        # Fund List (Editable Table with Delete)
        # -------------------------------------------------

        st.markdown("### Fund History")

        funds = []

        try:
            token = get_token()

            funds = api_client.get_funds(
                token=token,
                start_date=fund_start_date.isoformat() if fund_start_date else None,
                end_date=fund_end_date.isoformat() if fund_end_date else None,
                source_type=source_type_filter if source_type_filter != "All" else None,
            )

            if funds:
                df = pd.DataFrame(funds)
                display_df = df.copy()
                display_df = display_df.sort_values(
                    by=["date", "id"],
                    ascending=[False, False],
                ).reset_index(drop=True)
                display_df["delete"] = False

                edited_fund_df = st.data_editor(
                    display_df,
                    width="stretch",
                    hide_index=True,
                    disabled=["id"],
                    num_rows="fixed",
                    column_order=["id", "date", "amount", "source_type", "note", "delete"],
                    column_config={
                        "id": st.column_config.NumberColumn("ID"),
                        "date": st.column_config.TextColumn("Date"),
                        "amount": st.column_config.NumberColumn("Amount (₹)", min_value=1, step=1),
                        "source_type": st.column_config.SelectboxColumn(
                            "Source Type",
                            options=["salary", "refund", "cash", "petty", "other"],
                        ),
                        "note": st.column_config.TextColumn("Note"),
                        "delete": st.column_config.CheckboxColumn("🗑️", default=False),
                        "user_id": None,
                        "created_at": None,
                        "updated_at": None,
                    },
                )

                fund_save_msg = st.empty()
                fund_delete_msg = st.empty()

                # --- Save edits ---
                fund_data_columns = ["date", "amount", "source_type", "note"]
                fund_changed_rows = edited_fund_df[fund_data_columns].compare(display_df[fund_data_columns])

                if not fund_changed_rows.empty:
                    st.caption("⚠️ You have unsaved changes. Click **Save Changes** to apply.")

                    if st.button("💾 Save Changes", type="primary", key="save_funds"):
                        try:
                            token = get_token()
                            for idx in fund_changed_rows.index.tolist():
                                row = edited_fund_df.iloc[idx]
                                api_client.update_fund(
                                    token=token,
                                    fund_id=int(row["id"]),
                                    date=row["date"],
                                    amount=int(row["amount"]),
                                    source_type=row["source_type"],
                                    note=row["note"] or "",
                                )
                            fund_save_msg.success("Changes saved successfully!")
                            st.rerun()
                        except Exception as error:
                            fund_save_msg.error(f"Failed to save changes: {error}")

                # --- Handle deletions ---
                fund_rows_to_delete = edited_fund_df[edited_fund_df["delete"] == True]

                if not fund_rows_to_delete.empty:
                    fund_ids_to_delete = fund_rows_to_delete["id"].tolist()
                    fund_labels = ", ".join(
                        f"#{int(r['id'])} {r['source_type']} ₹{r['amount']}"
                        for _, r in fund_rows_to_delete.iterrows()
                    )

                    st.warning(
                        f"⚠️ Marked for deletion: **{fund_labels}**. "
                        f"This is permanent and cannot be undone."
                    )

                    fund_confirm_col1, fund_confirm_col2, _ = st.columns([1.2, 1, 5])

                    with fund_confirm_col1:
                        if st.button("🗑️ Confirm Delete", type="primary", key="confirm_delete_funds"):
                            try:
                                token = get_token()
                                for fund_id in fund_ids_to_delete:
                                    api_client.delete_fund(
                                        token=token,
                                        fund_id=int(fund_id),
                                    )
                                fund_delete_msg.success("Fund(s) deleted successfully!")
                                st.rerun()
                            except Exception as error:
                                fund_delete_msg.error(f"Failed to delete: {error}")

                    with fund_confirm_col2:
                        if st.button("❌ Cancel", key="cancel_delete_funds"):
                            st.rerun()

            else:
                st.info("No funds found for the selected filters.")

        except Exception as error:
            st.error(f"Failed to load funds: {error}")


    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    with summary_tab:
        st.subheader("Summary")

        st.divider()
        st.subheader("📈 Funds vs Expenses Over Time")

        try:
            token = get_token()

            all_expenses = api_client.get_expenses(token=token)
            all_funds = api_client.get_all_funds(token=token)

            if all_expenses or all_funds:
                import plotly.graph_objects as go

                # --- Expenses ---
                if all_expenses:
                    exp_df = pd.DataFrame(all_expenses)
                    exp_df["date"] = pd.to_datetime(exp_df["date"])
                    exp_df = exp_df.groupby("date")["amount"].sum().reset_index()
                    exp_df = exp_df.sort_values("date")
                    exp_df["cumulative"] = exp_df["amount"].cumsum()
                else:
                    exp_df = pd.DataFrame(columns=["date", "cumulative"])

                # --- Funds ---
                if all_funds:
                    fund_df = pd.DataFrame(all_funds)
                    fund_df["date"] = pd.to_datetime(fund_df["date"])
                    fund_df = fund_df.groupby("date")["amount"].sum().reset_index()
                    fund_df = fund_df.sort_values("date")
                    fund_df["cumulative"] = fund_df["amount"].cumsum()
                else:
                    fund_df = pd.DataFrame(columns=["date", "cumulative"])

                # --- Wallet Balance over time ---
                # Merge both on date, forward fill to get balance at each point
                all_dates = pd.DataFrame(
                    {"date": pd.date_range(
                        start=min(
                            exp_df["date"].min() if not exp_df.empty else pd.Timestamp.today(),
                            fund_df["date"].min() if not fund_df.empty else pd.Timestamp.today(),
                        ),
                        end=pd.Timestamp.today(),
                        freq="D",
                    )}
                )

                exp_merged = all_dates.merge(
                    exp_df[["date", "cumulative"]].rename(columns={"cumulative": "cum_expense"}),
                    on="date", how="left"
                ).ffill().fillna(0)

                fund_merged = all_dates.merge(
                    fund_df[["date", "cumulative"]].rename(columns={"cumulative": "cum_fund"}),
                    on="date", how="left"
                ).ffill().fillna(0)

                balance = exp_merged.copy()
                balance["cum_fund"] = fund_merged["cum_fund"]
                balance["wallet"] = balance["cum_fund"] - balance["cum_expense"]

                # --- Plotly Chart ---
                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=fund_merged["date"],
                    y=fund_merged["cum_fund"],
                    name="💰 Total Funds",
                    mode="lines",
                    line=dict(color="#00b09b", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(0, 176, 155, 0.1)",
                ))

                fig.add_trace(go.Scatter(
                    x=exp_merged["date"],
                    y=exp_merged["cum_expense"],
                    name="💸 Total Expenses",
                    mode="lines",
                    line=dict(color="#ff4b4b", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(255, 75, 75, 0.1)",
                ))

                fig.add_trace(go.Scatter(
                    x=balance["date"],
                    y=balance["wallet"],
                    name="🏦 Wallet Balance",
                    mode="lines",
                    line=dict(color="#f9a825", width=2, dash="dot"),
                ))

                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Amount (₹)",
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    height=450,
                    margin=dict(l=0, r=0, t=40, b=0),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)"),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(128,128,128,0.2)",
                        dtick=5000,
                        tickformat="₹,.0f",
                    ),
                )

                fig.update_traces(
                    hovertemplate="₹%{y:,.0f}",
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("No data available to plot.")

        except Exception as error:
            st.error(f"Failed to load chart: {error}")


        st.subheader("📊 Expense Overview")

        try:
            token = get_token()

            summary_data = api_client.get_expense_summary(token)

            total_expenses = summary_data.get("total_expenses", 0)
            num_transactions = summary_data.get("total_transactions", 0)

            if num_transactions > 0:
                average_expense = total_expenses / num_transactions
            else:
                average_expense = 0

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label="💸 Total Expenses",
                    value=f"₹{total_expenses:,}",
                )

            with col2:
                st.metric(
                    label="🧾 Transactions",
                    value=f"{num_transactions:,}",
                )

            with col3:
                st.metric(
                    label="📈 Average Expense",
                    value=f"₹{average_expense:,.2f}",
                )

        except Exception as error:
            st.error(f"Failed to load expense summary: {error}")

        st.divider()
        st.subheader("🏷️ Category-wise Expenses")

        try:
            token = get_token()
            summary_data = api_client.get_expense_summary(token)
            by_category = summary_data.get("by_category", {})

            if by_category:
                category_data = []

                for category, data in by_category.items():
                    category_data.append(
                        {
                            "Category": category,
                            "Total": data.get("total", 0),
                            "Transactions": data.get("transactions", 0),
                        }
                    )

                category_df = pd.DataFrame(category_data)

                category_df["Total"] = category_df["Total"].apply(
                    lambda value: f"₹{value:,.2f}"
                )

                st.dataframe(
                    category_df,
                    width="stretch",
                    hide_index=True,
                )
            else:
                st.info("No expense data available.")

        except Exception as error:
            st.error(f"Failed to load category summary: {error}")


        st.divider()
        st.subheader("📅 Monthly Expenses")

        try:
            token = get_token()

            # Get available years from expenses
            available_years = api_client.get_expense_years(token)

            if available_years:
                selected_year = st.selectbox(
                    "Select Year",
                    options=available_years,
                    index=0,
                    key="monthly_summary_year",
                )

                monthly_data = api_client.get_monthly_expense_summary(
                    token=token,
                    year=selected_year,
                )

                entries = monthly_data.get("entries", [])

                if entries:
                    MONTH_NAMES = {
                        1: "January", 2: "February", 3: "March",
                        4: "April", 5: "May", 6: "June",
                        7: "July", 8: "August", 9: "September",
                        10: "October", 11: "November", 12: "December",
                    }

                    monthly_df = pd.DataFrame(entries)
                    monthly_df["Month"] = monthly_df["month"].map(MONTH_NAMES)
                    monthly_df["Total Expenses"] = monthly_df["total_expenses"].apply(
                        lambda v: f"₹{v:,}"
                    )
                    monthly_df["Transactions"] = monthly_df["total_transactions"]
                    monthly_df = monthly_df[["Month", "Total Expenses", "Transactions"]]
                    monthly_df = monthly_df.sort_values(
                        "Month",
                        key=lambda col: col.map({v: k for k, v in MONTH_NAMES.items()}),
                        ascending=False,
                    )

                    st.dataframe(
                        monthly_df,
                        width="stretch",
                        hide_index=True,
                    )
                else:
                    st.info(f"No expense data for {selected_year}.")

            else:
                st.info("No expenses found to show monthly summary.")

        except Exception as error:
            st.error(f"Failed to load monthly summary: {error}")