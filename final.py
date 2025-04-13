import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Real Estate App", layout="wide")

# Custom CSS for better aesthetics
st.markdown("""
    <style>
    .main {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        background-color: #262730;
        color: #FFFFFF;
        border-radius: 5px;
    }
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #FFFFFF;
    }
    .stSuccess {
        background-color: #1B4332;
        color: #FFFFFF;
        border-radius: 5px;
        padding: 10px;
    }
    .stError {
        background-color: #7F1D1D;
        color: #FFFFFF;
        border-radius: 5px;
        padding: 10px;
    }
    .stExpander {
        background-color: #0e1117;
        color: #FFFFFF;
    }
    .stMetric {
        background-color: #0e1117;
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# Helper: Styled Table Display
# -------------------------
def display_styled_table(df):
    if df is not None and not df.empty:
        st.dataframe(
            df.style.set_properties(**{
                'text-align': 'center',
                'background-color': '#000000',
                'color': '#FFFFFF',
                'border': '1px solid #333333',
                'padding': '8px'
            })
            .set_table_styles([
                {'selector': 'th', 'props': [
                    ('text-align', 'center'),
                    ('background-color', '#1A1A1A'),
                    ('color', '#FFFFFF'),
                    ('font-weight', 'bold'),
                    ('padding', '12px'),
                    ('border-bottom', '2px solid #333333')
                ]},
                {'selector': 'tr:hover', 'props': [('background-color', '#1A1A1A')]},
                {'selector': 'td', 'props': [
                    ('color', '#FFFFFF'),
                    ('text-align', 'center'),
                    ('padding', '8px')
                ]},
                {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#0D0D0D')]},
                {'selector': 'tr:nth-child(odd)', 'props': [('background-color', '#000000')]}
            ])
        )
    else:
        st.info("No records found.")

# -------------------------
# Helper: Data Visualization
# -------------------------
def create_property_distribution_chart(df):
    if df is not None and not df.empty:
        fig = px.pie(df, names='property_type', title='Property Type Distribution')
        st.plotly_chart(fig, use_container_width=True)

def create_rent_distribution_chart(df):
    if df is not None and not df.empty:
        fig = px.histogram(df, x='rent', title='Rent Distribution', nbins=20)
        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 1. Database Connection and Helpers
# -------------------------
def create_connection(db_file="real_estate.db"):
    """Create and return a database connection."""
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def check_credentials(conn, username, password):
    """
    Check the given username and password against the Credentials table.
    Returns a tuple (True, user_type) if valid or (False, None) if not.
    """
    if not username or not password:
        return (False, None)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_type 
            FROM Credentials 
            WHERE username = ? AND password = ?
        """, (username, password))
        result = cur.fetchone()
        if result:
            return (True, result["user_type"])
        else:
            return (False, None)
    except Exception as e:
        st.error(f"Error checking credentials: {e}")
        return (False, None)

# -------------------------
# 2a. Admin View
# -------------------------
def admin_view(conn):
    st.title("🏢 Admin Dashboard")
    st.markdown("---")
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 User Management", "🏠 Property Management", "📈 Reports"])
    
    with tab1:
        st.subheader("System Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_users = pd.read_sql_query("SELECT COUNT(*) as count FROM Credentials", conn)['count'][0]
            st.metric("Total Users", total_users)
        
        with col2:
            total_properties = pd.read_sql_query("SELECT COUNT(*) as count FROM Property", conn)['count'][0]
            st.metric("Total Properties", total_properties)
        
        with col3:
            available_properties = pd.read_sql_query("SELECT COUNT(*) as count FROM Property WHERE is_available = 1", conn)['count'][0]
            st.metric("Available Properties", available_properties)
        
        # Property Type Distribution Chart
        st.subheader("Property Type Distribution")
        property_types = pd.read_sql_query("SELECT property_type, COUNT(*) as count FROM Property GROUP BY property_type", conn)
        create_property_distribution_chart(property_types)
    
    with tab2:
        st.subheader("User Management")
        
        # User Type Distribution
        user_types = pd.read_sql_query("SELECT user_type, COUNT(*) as count FROM Credentials GROUP BY user_type", conn)
        fig = px.pie(user_types, values='count', names='user_type', title='User Type Distribution')
        st.plotly_chart(fig, use_container_width=True)
        
        # User Tables
        st.write("### All Users")
        try:
            df = pd.read_sql_query("SELECT username, user_type FROM Credentials", conn)
            display_styled_table(df)
        except Exception as e:
            st.error(f"Error retrieving credentials: {e}")
        
        # Homeowner Management
        st.write("### Homeowner Management")
        try:
            df_homeowners = pd.read_sql_query("""
                SELECT owner_id, username, first_name, last_name, email, phone_number, verification_status
                FROM HomeOwner
            """, conn)
            display_styled_table(df_homeowners)
            
            # Verification Status Update
            st.markdown("#### Update Verification Status")
            homeowners_df = pd.read_sql_query("""
                SELECT owner_id, username, first_name, last_name, verification_status 
                FROM HomeOwner
            """, conn)
            
            owner_options = {f"{row['owner_id']} - {row['first_name']} {row['last_name']} ({row['verification_status']})": row["owner_id"]
                            for row in homeowners_df.to_dict("records")}
            selected_owner = st.selectbox("Select Homeowner to update", list(owner_options.keys()))
            new_status = st.selectbox("New Verification Status", options=["pending", "verified", "rejected"])
            
            if st.button("Update Status", key="update_status"):
                owner_id = owner_options[selected_owner]
                cur = conn.cursor()
                cur.execute("UPDATE HomeOwner SET verification_status = ? WHERE owner_id = ?", (new_status, owner_id))
                conn.commit()
                st.success("Verification status updated successfully!")
        except Exception as e:
            st.error(f"Error in homeowner management: {e}")
    
    with tab3:
        st.subheader("Property Management")
        
        # Property Statistics
        col1, col2 = st.columns(2)
        with col1:
            avg_rent = pd.read_sql_query("SELECT AVG(rent) as avg_rent FROM Property WHERE sale_renting = 'rent'", conn)['avg_rent'][0]
            st.metric("Average Rent", f"${avg_rent:.2f}")
        
        with col2:
            total_available = pd.read_sql_query("SELECT COUNT(*) as count FROM Property WHERE is_available = 1", conn)['count'][0]
            st.metric("Available Properties", total_available)
        
        # Property List
        st.write("### All Properties")
        try:
            df_properties = pd.read_sql_query("""
                SELECT p.*, h.first_name || ' ' || h.last_name AS owner_name
                FROM Property p
                JOIN HomeOwner h ON p.owner_id = h.owner_id
            """, conn)
            display_styled_table(df_properties)
            
            # Property Availability Update
            st.markdown("#### Update Property Availability")
            properties = pd.read_sql_query("SELECT property_id, street, city FROM Property", conn)
            prop_options = {f"{row['property_id']} - {row['street']}, {row['city']}": row["property_id"] 
                          for row in properties.to_dict("records")}
            selected_prop = st.selectbox("Select Property", list(prop_options.keys()))
            new_status = st.selectbox("New Availability Status", options=["Available", "Unavailable"])
            
            if st.button("Update Status", key="update_property"):
                prop_id = prop_options[selected_prop]
                cur = conn.cursor()
                cur.execute("UPDATE Property SET is_available = ? WHERE property_id = ?", 
                          (1 if new_status == "Available" else 0, prop_id))
                conn.commit()
                st.success("Property status updated successfully!")
        except Exception as e:
            st.error(f"Error in property management: {e}")
    
    with tab4:
        st.subheader("Analytics & Reports")
        admin_reports(conn)

def admin_reports(conn):
    st.markdown("## Admin Reports and Actions")

    # 1. List All Available Properties for Rent
    with st.expander("1. List All Available Properties for Rent"):
        query = """
        SELECT 
            p.property_id,
            p.property_type,
            p.city,
            p.street,
            p.cost,
            p.rent,
            p.is_available,
            h.first_name || ' ' || h.last_name AS owner_name
        FROM Property p
        JOIN HomeOwner h ON p.owner_id = h.owner_id
        WHERE p.sale_renting = 'rent' AND p.is_available = 1;
        """
        try:
            df = pd.read_sql_query(query, conn)
            display_styled_table(df)
        except Exception as e:
            st.error(f"Error fetching available rental properties: {e}")

    # 2. List Verified Homeowners
    with st.expander("2. List Verified Homeowners"):
        query = """
        SELECT 
            owner_id,
            first_name,
            last_name,
            email,
            phone_number
        FROM HomeOwner
        WHERE verification_status = 'verified';
        """
        try:
            df = pd.read_sql_query(query, conn)
            display_styled_table(df)
        except Exception as e:
            st.error(f"Error fetching verified homeowners: {e}")

    # 3. Get All Shared Rooms with Available Beds
    with st.expander("3. Get All Shared Rooms with Available Beds"):
        query = """
        SELECT 
            sr.room_id,
            sr.property_id,
            sr.available_beds,
            sr.total_beds,
            sr.monthly_rent,
            p.city,
            p.street
        FROM SharedRoom sr
        JOIN Property p ON sr.property_id = p.property_id
        WHERE sr.available_beds > 0;
        """
        try:
            df = pd.read_sql_query(query, conn)
            display_styled_table(df)
        except Exception as e:
            st.error(f"Error fetching shared rooms with available beds: {e}")

    # 4. Show All Customers Interested in Sharing a Particular Room
    with st.expander("4. Show All Customers Interested in Sharing a Particular Room"):
        room_id = st.number_input("Enter Room ID", min_value=1, step=1)
        if st.button("Show Interested Customers", key="show_interested_customers"):
            query = """
            SELECT 
                c.customer_id,
                c.first_name,
                c.last_name,
                c.email
            FROM Interested_In_Sharing iis
            JOIN Customer c ON iis.customer_id = c.customer_id
            WHERE iis.room_id = ?
            """
            try:
                df = pd.read_sql_query(query, conn, params=(room_id,))
                display_styled_table(df)
            except Exception as e:
                st.error(f"Error fetching interested customers: {e}")

    # 6. Verify a Homeowner (Handled above in update section)
    # 7. Mark a Property as Unavailable
    with st.expander("7. Mark a Property as Unavailable"):
        try:
            properties = pd.read_sql_query("SELECT property_id, street, city FROM Property WHERE is_available = 1", conn)
            if not properties.empty:
                prop_options = {f"{row['property_id']} - {row['street']}, {row['city']}": row["property_id"] for row in properties.to_dict("records")}
                selected_prop = st.selectbox("Select Property to Mark as Unavailable", list(prop_options.keys()))
                if st.button("Mark as Unavailable", key="mark_property"):
                    prop_id = prop_options[selected_prop]
                    cur = conn.cursor()
                    cur.execute("UPDATE Property SET is_available = 0 WHERE property_id = ?", (prop_id,))
                    conn.commit()
                    st.success("Property marked as unavailable!")
            else:
                st.write("No available properties found.")
        except Exception as e:
            st.error(f"Error marking property as unavailable: {e}")

    # 8. Decrease Available Beds in Shared Room (When a Customer Joins)
    with st.expander("8. Decrease Available Beds in Shared Room"):
        room_id_decrement = st.number_input("Enter Room ID to Decrease Available Beds", min_value=1, step=1, key="room_id_decrement")
        if st.button("Decrease Available Beds", key="decrease_beds"):
            try:
                cur = conn.cursor()
                cur.execute("UPDATE SharedRoom SET available_beds = available_beds - 1 WHERE room_id = ? AND available_beds > 0", (room_id_decrement,))
                conn.commit()
                st.success("Available beds decreased!")
            except Exception as e:
                st.error(f"Error decreasing available beds: {e}")

    # 10. Delete a Customer and Cascade Delete Related Records
    with st.expander("10. Delete a Customer"):
        try:
            customers = pd.read_sql_query("SELECT customer_id, username, first_name, last_name FROM Customer", conn)
            if not customers.empty:
                cust_options = {f"{row['customer_id']} - {row['first_name']} {row['last_name']}": row["customer_id"] for row in customers.to_dict("records")}
                selected_cust = st.selectbox("Select Customer to Delete", list(cust_options.keys()))
                if st.button("Delete Customer", key="delete_customer"):
                    cust_id = cust_options[selected_cust]
                    cur = conn.cursor()
                    cur.execute("DELETE FROM Customer WHERE customer_id = ?", (cust_id,))
                    conn.commit()
                    st.success("Customer deleted!")
            else:
                st.write("No customers found.")
        except Exception as e:
            st.error(f"Error deleting customer: {e}")

    # 11. Delete a Property
    with st.expander("11. Delete a Property"):
        try:
            properties_all = pd.read_sql_query("SELECT property_id, street, city FROM Property", conn)
            if not properties_all.empty:
                prop_options_all = {f"{row['property_id']} - {row['street']}, {row['city']}": row["property_id"] for row in properties_all.to_dict("records")}
                selected_prop_del = st.selectbox("Select Property to Delete", list(prop_options_all.keys()))
                if st.button("Delete Property", key="delete_property"):
                    prop_id = prop_options_all[selected_prop_del]
                    cur = conn.cursor()
                    cur.execute("DELETE FROM Property WHERE property_id = ?", (prop_id,))
                    conn.commit()
                    st.success("Property deleted!")
            else:
                st.write("No properties found.")
        except Exception as e:
            st.error(f"Error deleting property: {e}")

    # 12. List Properties That Have Shared Rooms Fully Occupied
    with st.expander("12. Properties with Fully Occupied Shared Rooms"):
        query = """
        SELECT 
            p.property_id,
            p.property_type,
            p.city
        FROM Property p
        JOIN SharedRoom sr ON p.property_id = sr.property_id
        WHERE sr.available_beds = 0;
        """
        try:
            df = pd.read_sql_query(query, conn)
            display_styled_table(df)
        except Exception as e:
            st.error(f"Error fetching fully occupied shared rooms: {e}")

    # 13. Count of Properties Per City
    with st.expander("13. Count of Properties Per City"):
        query = """
        SELECT 
            city,
            COUNT(property_id) AS total_properties
        FROM Property
        GROUP BY city;
        """
        try:
            df = pd.read_sql_query(query, conn)
            display_styled_table(df)
        except Exception as e:
            st.error(f"Error counting properties per city: {e}")

    # 14. Find Customers Participating in Room Sharing with Their Details
    with st.expander("14. Customers Participating in Room Sharing"):
        query = """
        SELECT 
            c.customer_id,
            c.first_name,
            c.last_name,
            sr.room_id,
            p.city,
            p.street
        FROM Participates pr
        JOIN Customer c ON pr.customer_id = c.customer_id
        JOIN SharedRoom sr ON pr.room_id = sr.room_id
        JOIN Property p ON sr.property_id = p.property_id;
        """
        try:
            df = pd.read_sql_query(query, conn)
            display_styled_table(df)
        except Exception as e:
            st.error(f"Error fetching participating customers: {e}")

    # 15. Top 5 Cities with Most Properties Available for Rent
    with st.expander("15. Top 5 Cities with Most Properties Available for Rent"):
        query = """
        SELECT 
            city,
            COUNT(property_id) AS available_properties
        FROM Property
        WHERE sale_renting = 'rent' AND is_available = 1
        GROUP BY city
        ORDER BY available_properties DESC
        LIMIT 5;
        """
        try:
            df = pd.read_sql_query(query, conn)
            display_styled_table(df)
        except Exception as e:
            st.error(f"Error fetching top cities: {e}")

    # 16. Revenue Generated From Property Sales/Rent (Completed Payments Only)
    with st.expander("16. Total Revenue from Completed Payments"):
        query = """
        SELECT 
            SUM(amount) AS total_revenue
        FROM Receipt
        WHERE payment_status = 'completed';
        """
        try:
            df = pd.read_sql_query(query, conn)
            display_styled_table(df)
        except Exception as e:
            st.error(f"Error calculating revenue: {e}")

    # 17. Find Homeowners Who Own Properties That Are All Unavailable
    with st.expander("17. Homeowners with All Properties Unavailable"):
        query = """
        SELECT 
            h.owner_id,
            h.first_name,
            h.last_name
        FROM HomeOwner h
        WHERE NOT EXISTS (
            SELECT 1
            FROM Property p
            WHERE p.owner_id = h.owner_id AND p.is_available = 1
        );
        """
        try:
            df = pd.read_sql_query(query, conn)
            display_styled_table(df)
        except Exception as e:
            st.error(f"Error fetching homeowners with all properties unavailable: {e}")

# -------------------------
# 2b. Homeowner View
# -------------------------
def homeowner_view(conn, username):
    st.title("🏠 Welcome, Homeowner!")
    st.markdown("---")
    
    # Get homeowner details
    homeowner = pd.read_sql_query("""
        SELECT * FROM HomeOwner WHERE username = ?
    """, conn, params=(username,)).iloc[0]
    
    # Display homeowner profile
    st.subheader("Your Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {homeowner['first_name']} {homeowner['last_name']}")
        st.write(f"**Email:** {homeowner['email']}")
    with col2:
        st.write(f"**Phone:** {homeowner['phone_number']}")
        st.write(f"**Verification Status:** {homeowner['verification_status']}")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📊 Property Management", "💰 Financial Overview", "👥 Sharing Management"])
    
    with tab1:
        st.subheader("Your Properties")
        
        # Add new property
        with st.expander("➕ Add New Property"):
            with st.form("new_property_form"):
                property_type = st.selectbox("Property Type", ["Apartment", "House", "Condo", "Townhouse"])
                street = st.text_input("Street Address")
                city = st.text_input("City")
                state = st.text_input("State")
                zip_code = st.text_input("ZIP Code")
                area = st.number_input("Area (sq ft)", min_value=0.0, step=100.0)
                cost = st.number_input("Cost", min_value=0, step=1000)
                rent = st.number_input("Rent", min_value=0, step=100)
                sale_renting = st.selectbox("Sale or Rent", ["sale", "rent"])
                description = st.text_area("Description")
                
                if st.form_submit_button("Add Property"):
                    try:
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO Property (owner_id, property_type, street, city, state, zip_code, 
                                                area, cost, rent, sale_renting, description, is_available)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (homeowner['owner_id'], property_type, street, city, state, zip_code, 
                             area, cost, rent, sale_renting, description))
                        conn.commit()
                        st.success("Property added successfully!")
                    except Exception as e:
                        st.error(f"Error adding property: {e}")
        
        # Display existing properties
        try:
            properties = pd.read_sql_query("""
                SELECT * FROM Property WHERE owner_id = ?
            """, conn, params=(homeowner['owner_id'],))
            
            if not properties.empty:
                # Display properties in a grid
                cols = st.columns(3)
                for idx, prop in properties.iterrows():
                    with cols[idx % 3]:
                        st.markdown(f"""
                            <div style='padding: 10px; border-radius: 10px; background-color: #0e1117; color: #FFFFFF; box-shadow: 0 2px 4px rgba(0,0,0,0.3); margin-bottom: 20px;'>
                                <h4 style='color: #FFFFFF;'>{prop['property_type']}</h4>
                                <p><strong>Location:</strong> {prop['street']}, {prop['city']}</p>
                                <p><strong>Status:</strong> {'Available' if prop['is_available'] else 'Unavailable'}</p>
                                <p><strong>Rent:</strong> ${prop['rent']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Property management options
                        with st.expander("Manage Property"):
                            if st.button("Toggle Availability", key=f"toggle_{prop['property_id']}"):
                                try:
                                    cur = conn.cursor()
                                    cur.execute("""
                                        UPDATE Property 
                                        SET is_available = ? 
                                        WHERE property_id = ?
                                    """, (0 if prop['is_available'] else 1, prop['property_id']))
                                    conn.commit()
                                    st.success("Property availability updated!")
                                except Exception as e:
                                    st.error(f"Error updating property: {e}")
            else:
                st.info("You haven't added any properties yet.")
        except Exception as e:
            st.error(f"Error fetching properties: {e}")
    
    with tab2:
        st.subheader("Financial Overview")
        
        try:
            # Total properties value
            total_value = pd.read_sql_query("""
                SELECT SUM(cost) as total_value FROM Property WHERE owner_id = ?
            """, conn, params=(homeowner['owner_id'],))['total_value'][0]

            total_value = total_value if total_value is not None else 0
            
            # Monthly rental income
            monthly_income = pd.read_sql_query("""
                SELECT SUM(rent) as monthly_income 
                FROM Property 
                WHERE owner_id = ? AND sale_renting = 'rent' AND is_available = 1
            """, conn, params=(homeowner['owner_id'],))['monthly_income'][0]

            monthly_income = monthly_income if monthly_income is not None else 0

            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Property Value", f"${total_value:,.2f}")
            with col2:
                st.metric("Monthly Rental Income", f"${monthly_income:,.2f}")
            
            # Rental income by property type
            income_by_type = pd.read_sql_query("""
                SELECT property_type, SUM(rent) as total_rent
                FROM Property
                WHERE owner_id = ? AND sale_renting = 'rent' AND is_available = 1
                GROUP BY property_type
            """, conn, params=(homeowner['owner_id'],))
            
            if not income_by_type.empty:
                fig = px.pie(income_by_type, values='total_rent', names='property_type', 
                           title='Rental Income by Property Type')
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            print(f"Error fetching financial data: {e}")
    
    with tab3:
        st.subheader("Shared Room Management")
        
        try:
            shared_rooms = pd.read_sql_query("""
                SELECT sr.*, p.street, p.city
                FROM SharedRoom sr
                JOIN Property p ON sr.property_id = p.property_id
                WHERE p.owner_id = ?
            """, conn, params=(homeowner['owner_id'],))
            
            if not shared_rooms.empty:
                for _, room in shared_rooms.iterrows():
                    with st.expander(f"Room {room['room_id']} - {room['street']}, {room['city']}"):
                        st.write(f"**Total Beds:** {room['total_beds']}")
                        st.write(f"**Available Beds:** {room['available_beds']}")
                        st.write(f"**Monthly Rent per Bed:** ${room['monthly_rent']}")
                        
                        # Show interested customers
                        interested_customers = pd.read_sql_query("""
                            SELECT c.first_name, c.last_name, c.email, c.phone
                            FROM Interested_In_Sharing iis
                            JOIN Customer c ON iis.customer_id = c.customer_id
                            WHERE iis.room_id = ?
                        """, conn, params=(room['room_id'],))
                        
                        if not interested_customers.empty:
                            st.write("**Interested Customers:**")
                            display_styled_table(interested_customers)
                        else:
                            st.info("No interested customers yet.")
            else:
                st.info("You haven't added any shared rooms yet.")
        except Exception as e:
            st.error(f"Error fetching shared rooms: {e}")

# -------------------------
# 2c. Customer View
# -------------------------
def customer_view(conn, username):
    st.title("👋 Welcome, Customer!")
    st.markdown("---")
    
    # Get customer details
    customer = pd.read_sql_query("""
        SELECT * FROM Customer WHERE username = ?
    """, conn, params=(username,)).iloc[0]
    
    # Display customer profile
    st.subheader("Your Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {customer['first_name']} {customer['last_name']}")
        st.write(f"**Email:** {customer['email']}")
    with col2:
        st.write(f"**Phone:** {customer['phone']}")
        st.write(f"**Username:** {customer['username']}")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["🏠 Browse Properties", "🤝 Shared Rooms", "📋 Your Applications"])
    
    with tab1:
        st.subheader("Available Properties")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            property_type = st.selectbox("Property Type", ["All"] + list(pd.read_sql_query("SELECT DISTINCT property_type FROM Property", conn)['property_type']))
        with col2:
            min_rent = st.number_input("Minimum Rent", min_value=0, step=100)
        with col3:
            max_rent = st.number_input("Maximum Rent", min_value=min_rent, step=100)
        
        # Build query based on filters
        query = """
            SELECT p.*, h.first_name || ' ' || h.last_name AS owner_name
            FROM Property p
            JOIN HomeOwner h ON p.owner_id = h.owner_id
            WHERE p.is_available = 1
        """
        params = []
        
        if property_type != "All":
            query += " AND p.property_type = ?"
            params.append(property_type)
        
        if min_rent > 0:
            query += " AND p.rent >= ?"
            params.append(min_rent)
        
        if max_rent > min_rent:
            query += " AND p.rent <= ?"
            params.append(max_rent)
        
        try:
            properties = pd.read_sql_query(query, conn, params=params)
            if not properties.empty:
                # Display properties in a grid
                cols = st.columns(3)
                for idx, prop in properties.iterrows():
                    with cols[idx % 3]:
                        st.markdown(f"""
                            <div style='padding: 10px; border-radius: 10px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;'>
                                <h4>{prop['property_type']}</h4>
                                <p><strong>Location:</strong> {prop['street']}, {prop['city']}</p>
                                <p><strong>Rent:</strong> ${prop['rent']}</p>
                                <p><strong>Owner:</strong> {prop['owner_name']}</p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No properties match your criteria.")
        except Exception as e:
            st.error(f"Error fetching properties: {e}")
    
    with tab2:
        st.subheader("Available Shared Rooms")
        
        try:
            shared_rooms = pd.read_sql_query("""
                SELECT sr.*, p.street, p.city, p.rent
                FROM SharedRoom sr
                JOIN Property p ON sr.property_id = p.property_id
                WHERE sr.available_beds > 0
            """, conn)
            
            if not shared_rooms.empty:
                # Display shared rooms with interactive elements
                for _, room in shared_rooms.iterrows():
                    with st.expander(f"Room {room['room_id']} - {room['street']}, {room['city']}"):
                        st.write(f"**Available Beds:** {room['available_beds']}/{room['total_beds']}")
                        st.write(f"**Monthly Rent per Bed:** ${room['monthly_rent']}")
                        st.write(f"**Property Rent:** ${room['rent']}")
                        
                        if st.button("Apply for this Room", key=f"apply_room_{room['room_id']}"):
                            apply_for_sharing(conn, customer, room['room_id'])
            else:
                st.info("No shared rooms available at the moment.")
        except Exception as e:
            st.error(f"Error fetching shared rooms: {e}")
    
    with tab3:
        st.subheader("Your Applications")
        
        try:
            applications = pd.read_sql_query("""
                SELECT iis.*, p.street, p.city
                FROM Interested_In_Sharing iis
                JOIN SharedRoom sr ON iis.room_id = sr.room_id
                JOIN Property p ON sr.property_id = p.property_id
                WHERE iis.customer_id = ?
            """, conn, params=(customer['customer_id'],))
            
            if not applications.empty:
                display_styled_table(applications)
            else:
                st.info("You haven't applied for any shared rooms yet.")
        except Exception as e:
            st.error(f"Error fetching applications: {e}")

def apply_for_sharing(conn, customer, room_id):
    st.markdown("### Apply for Sharing")
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Interested_In_Sharing WHERE customer_id = ? AND room_id = ?", (customer["customer_id"], room_id))
        exists = cur.fetchone()
        if exists:
            st.warning("You have already applied for this room.")
        else:
            cur.execute("INSERT INTO Interested_In_Sharing (customer_id, room_id) VALUES (?, ?)", (customer["customer_id"], room_id))
            conn.commit()
            st.success("Application for sharing submitted!")
    except Exception as e:
        st.error(f"Error in applying for sharing: {e}")

# -------------------------
# 3. Main App: Login and Routing
# -------------------------
def main():
    st.title("Airbnb-like Real Estate App")

    conn = create_connection()
    if not conn:
        st.error("Could not connect to the database.")
        st.stop()
    
    # Display sample credentials on the login sidebar
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_type = None

    if not st.session_state.logged_in:
        st.sidebar.header("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            valid, user_type = check_credentials(conn, username, password)
            if valid:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_type = user_type
                st.success(f"Logged in as {user_type}!")
                st.rerun()  # Apply login state immediately
            else:
                st.error("Invalid username or password.")

        st.sidebar.markdown("#### Sample Credentials")
        st.sidebar.markdown(
            """
            **Admin:**  
            - Username: admin.alex  
            - Password: admin001  

            **Customer:**  
            - Username: john.doe  
            - Password: pass123  

            **Homeowner:**  
            - Username: owner.tom  
            - Password: owner001  
            """
        )
        st.stop()
    else:
        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

        if st.session_state.user_type == "admin":
            admin_view(conn)
        elif st.session_state.user_type == "owner":
            homeowner_view(conn, st.session_state.username)
        elif st.session_state.user_type == "customer":
            customer_view(conn, st.session_state.username)
        else:
            st.error("Unknown user type.")
    
    conn.close()

if __name__ == "__main__":
    main()