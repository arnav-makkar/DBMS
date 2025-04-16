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
        background-color: #0E1117;
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
    .custom-button {
        width: 100%;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 5px 0;
        text-align: center;
    }
    .rent-button {
        background-color: #4CAF50;
        color: white;
    }
    .rent-button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
    }
    .share-button {
        background-color: #2196F3;
        color: white;
    }
    .share-button:hover {
        background-color: #1e88e5;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
    }
    .view-button {
        background-color: #9C27B0;
        color: white;
    }
    .view-button:hover {
        background-color: #8e24aa;
        box-shadow: 0 4px 8px rgba(156, 39, 176, 0.3);
    }
    .button-container {
        display: flex;
        gap: 10px;
        padding: 10px 0;
        justify-content: space-between;
        align-items: center;
    }
    .purchase-table {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Property image database
PROPERTY_IMAGES = [
    # Apartments
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",  # Modern apartment
    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00",  # Apartment interior
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",  # Luxury apartment
    "https://images.unsplash.com/photo-1493809842364-78817add7ffb",  # Apartment building
    "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af",  # Apartment living room
    
    # Houses
    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6",  # Modern house
    "https://images.unsplash.com/photo-1518780664697-55e3ad937233",  # Classic house
    "https://images.unsplash.com/photo-1568605114967-8130f3a36994",  # Family house
    "https://images.unsplash.com/photo-1576941089067-2de3c901e126",  # House exterior
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",  # Luxury house
    
    # Condos
    "https://images.unsplash.com/photo-1515263487990-61b07816b324",  # Modern condo
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",  # Condo interior
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",  # Condo building
    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00",  # Condo living room
    "https://images.unsplash.com/photo-1493809842364-78817add7ffb",  # Condo exterior
    
    # Villas
    "https://images.unsplash.com/photo-1613977257363-707ba9348227",  # Luxury villa
    "https://images.unsplash.com/photo-1613490493576-7fde63acd811",  # Modern villa
    "https://images.unsplash.com/photo-1613977257592-4871e5fcd7c4",  # Villa exterior
    "https://images.unsplash.com/photo-1613977257363-707ba9348227",  # Villa pool
    "https://images.unsplash.com/photo-1613490493576-7fde63acd811",  # Villa garden
    
    # Rooms
    "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af",  # Modern room
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",  # Bedroom
    "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8",  # Living room
    "https://images.unsplash.com/photo-1560448204-603b3fc33ddc",  # Studio room
    "https://images.unsplash.com/photo-1560449017-7c4a12d1a8f6",  # Shared room
]

def get_property_image(property_id, property_type):
    """
    Returns a consistent image URL for a property based on its ID and type.
    This ensures the same property always gets the same image.
    """
    # Use property_id to get a consistent index
    index = (property_id * 13) % len(PROPERTY_IMAGES)  # Using prime number multiplication for better distribution
    return PROPERTY_IMAGES[index]

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
            sr.total_beds,
            sr.available_beds,
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
        st.write(f"**Owner ID:** {homeowner['owner_id']}")  # Display owner_id for debugging
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📊 Property Management", "💰 Financial Overview", "👥 Sharing Management"])
    
    with tab1:
        st.subheader("Your Properties")
        
        # Add new property
        with st.expander("➕ Add New Property"):
            with st.form("new_property_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    property_type = st.selectbox("Property Type", ["apartment", "house", "condo", "villa", "room"])
                    sale_renting = st.selectbox("Sale or Rent", ["sale", "rent"])
                    cost = st.number_input("Cost (if for sale)", min_value=0, step=1000)
                    rent = st.number_input("Monthly Rent (if for rent)", min_value=0, step=100)
                    area = st.number_input("Area (sq ft)", min_value=0.0, step=100.0)
                
                with col2:
                    building = st.text_input("Building Name")
                    street = st.text_input("Street Address")
                    city = st.text_input("City")
                    pin = st.text_input("PIN Code")
                
                # Location coordinates
                st.subheader("Location Coordinates")
                coord_col1, coord_col2 = st.columns(2)
                with coord_col1:
                    coord_X = st.number_input("Coordinate X", value=0.0)
                with coord_col2:
                    coord_Y = st.number_input("Coordinate Y", value=0.0)
                
                # Property details
                st.subheader("Property Details")
                description = st.text_area("Description")
                amenities = st.text_area("Amenities (separate by commas)")
                sharing_allowed = st.checkbox("Allow Sharing")
                
                if st.form_submit_button("Add Property"):
                    try:
                        cur = conn.cursor()
                        # Insert into Property table
                        cur.execute("""
                            INSERT INTO Property (
                                owner_id, property_type, sale_renting, cost,
                                building, street, city, pin, area, rent,
                                description, amenities, is_available, sharing_allowed,
                                coord_X, coord_Y
                            ) VALUES (
                                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?
                            )
                        """, (
                            homeowner['owner_id'], property_type, sale_renting, cost,
                            building, street, city, pin, area, rent,
                            description, amenities, sharing_allowed,
                            coord_X, coord_Y
                        ))
                        
                        # Get the ID of the newly inserted property
                        cur.execute("SELECT last_insert_rowid()")
                        property_id = cur.fetchone()[0]
                        
                        # If sharing is allowed and it's a rental property, add to SharedRoom
                        if sharing_allowed and sale_renting == 'rent':
                            try:
                                cur.execute("""
                                    INSERT INTO SharedRoom (property_id, total_beds, available_beds, monthly_rent)
                                    VALUES (?, 2, 2, ?)
                                """, (property_id, rent / 2))
                                conn.commit()
                                st.success("Property has been added to Shared Rooms! You can manage it in the Sharing Management tab.")
                            except Exception as e:
                                st.error(f"Error adding to shared rooms: {str(e)}")
                                conn.rollback()
                        else:
                            conn.commit()
                        
                        st.success("Property added successfully!")
                        
                        # Clear all form fields by forcing a page refresh
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding property: {str(e)}")
                        conn.rollback()
                        
                # Add a note about shared properties
                if sale_renting == "rent" and sharing_allowed:
                    st.info("This property will be automatically added to your shared rooms.")
        
        # Display existing properties
        try:
            # Debug information
            st.write(f"Fetching properties for owner_id: {homeowner['owner_id']}")
            
            # First check if there are any properties for this owner - simplified query
            properties = pd.read_sql_query("""
                SELECT * FROM Property WHERE owner_id = ?
            """, conn, params=(homeowner['owner_id'],))
            
            property_count = len(properties)
            st.write(f"Total properties found: {property_count}")
            
            # Display the raw properties DataFrame for debugging
            st.write("Raw properties data:")
            if not properties.empty:
                # Now get owner information - using the current homeowner's information directly
                owner_name = f"{homeowner['first_name']} {homeowner['last_name']}"
                
                # Display properties in a grid
                cols = st.columns(3)
                for idx, prop in properties.iterrows():
                    with cols[idx % 3]:
                        # Get a random image for the property type
                        property_type = str(prop.get('property_type', 'apartment')).lower()
                        if property_type == 'apartment':
                            image_url = PROPERTY_IMAGES[0]
                        elif property_type == 'house':
                            image_url = PROPERTY_IMAGES[5]
                        elif property_type == 'condo':
                            image_url = PROPERTY_IMAGES[10]
                        elif property_type == 'villa':
                            image_url = PROPERTY_IMAGES[15]
                        elif property_type == 'room':
                            image_url = PROPERTY_IMAGES[20]
                        else:
                            image_url = PROPERTY_IMAGES[0]
                        
                        # Create unique keys using both index and property_id
                        property_id = prop.get('property_id', f'prop_{idx}')
                        rent_key = f"rent_{property_id}_{idx}"
                        share_key = f"share_{property_id}_{idx}"
                        view_key = f"view_{property_id}_{idx}"
                        
                        # Safely get property values using .get()
                        street = str(prop.get('street', 'N/A'))
                        city = str(prop.get('city', 'N/A'))
                        rent = float(prop.get('rent', 0))
                        area = float(prop.get('area', 0))
                        description = str(prop.get('description', 'No description available'))
                        
                        st.markdown(f"""
                            <div style='padding: 10px; 
                                    border-radius: 10px; 
                                    background-color: #1E1E1E; 
                                    color: #FFFFFF; 
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.3); 
                                    margin-bottom: 10px;'>
                                <img src="{image_url}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 5px; margin-bottom: 10px;">
                                <h4 style='color: #FFFFFF;'>{property_type}</h4>
                                <p><strong>Location:</strong> {street}, {city}</p>
                                <p><strong>Rent:</strong> ${rent:,.2f}</p>
                                <p><strong>Owner:</strong> {owner_name}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Add buttons in a row
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("Rent Now", key=rent_key):
                                try:
                                    cur = conn.cursor()
                                    # Add to Buy_Rent table
                                    cur.execute("""
                                        INSERT INTO Buy_Rent (customer_id, property_id)
                                        VALUES (?, ?)
                                    """, (homeowner['owner_id'], property_id))
                                    
                                    # Add to Receipt table
                                    cur.execute("""
                                        INSERT INTO Receipt (property_id, customer_id, amount, payment_status, payment_date)
                                        VALUES (?, ?, ?, 'completed', DATE('now'))
                                    """, (property_id, homeowner['owner_id'], rent))
                                    
                                    # Update property availability
                                    cur.execute("""
                                        UPDATE Property 
                                        SET is_available = 0 
                                        WHERE property_id = ?
                                    """, (property_id,))
                                    
                                    conn.commit()
                                    st.success(f"You have successfully rented this property at {street}, {city}!")
                                except Exception as e:
                                    st.error(f"Error processing rental: {str(e)}")
                        
                        with col2:
                            if st.button("Share Room", key=share_key):
                                sale_renting = str(prop.get('sale_renting', 'sale'))
                                is_available = int(prop.get('is_available', 0))
                                
                                if sale_renting == 'rent' and is_available == 1:
                                    try:
                                        cur = conn.cursor()
                                        cur.execute("SELECT * FROM SharedRoom WHERE property_id = ?", (property_id,))
                                        if not cur.fetchone():
                                            cur.execute("""
                                                INSERT INTO SharedRoom (property_id, total_beds, available_beds, monthly_rent)
                                                VALUES (?, 2, 2, ?)
                                            """, (property_id, rent / 2))
                                            conn.commit()
                                            st.success(f"Room added to shared rooms! Monthly rent per bed: ${rent / 2:.2f}")
                                        else:
                                            st.info("This property is already available as a shared room.")
                                    except Exception as e:
                                        st.error(f"Error adding to shared rooms: {e}")
                                else:
                                    st.warning("This property is not available for renting. Only properties available for rent can be shared.")
                        
                        with col3:
                            show_details = st.button("View More", key=view_key)
                        
                        if show_details:
                            st.markdown(f"""
                                <div style='padding: 15px; 
                                        border-radius: 10px; 
                                        background-color: #2A2A2A; 
                                        color: #FFFFFF; 
                                        box-shadow: 0 4px 8px rgba(0,0,0,0.3); 
                                        margin: 10px 0 20px 0;
                                        border: 1px solid #444;
                                        width: 100%;'>
                                    <h3 style='color: #FFFFFF; margin-bottom: 15px; border-bottom: 1px solid #444; padding-bottom: 10px;'>
                                        Detailed Information
                                    </h3>
                                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                                        <div>
                                            <p><strong>Property ID:</strong> {property_id}</p>
                                            <p><strong>Property Type:</strong> {property_type}</p>
                                            <p><strong>Location:</strong> {street}, {city}</p>
                                        </div>
                                        <div>
                                            <p><strong>Rent:</strong> ${rent:,.2f}</p>
                                            <p><strong>Owner:</strong> {owner_name}</p>
                                            <p><strong>Area:</strong> {area:,.0f} sq ft</p>
                                        </div>
                                    </div>
                                    <div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid #444;'>
                                        <p><strong>Description:</strong></p>
                                        <p style='background-color: #1E1E1E; padding: 10px; border-radius: 5px;'>{description}</p>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("You haven't added any properties yet.")
        except Exception as e:
            st.error(f"Error fetching properties: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
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
            # Get shared rooms with all details
            shared_rooms = pd.read_sql_query("""
                SELECT DISTINCT
                    sr.room_id,
                    sr.property_id,
                    sr.total_beds,
                    sr.available_beds,
                    sr.monthly_rent,
                    p.street,
                    p.city,
                    p.rent,
                    p.property_type,
                    p.description,
                    p.building
                FROM SharedRoom sr
                JOIN Property p ON sr.property_id = p.property_id
                WHERE p.owner_id = ?
                ORDER BY sr.room_id DESC
            """, conn, params=(homeowner['owner_id'],))
            
            # Debug information
            st.write("Debug Information:")
            st.write(f"Owner ID being queried: {homeowner['owner_id']}")
            st.write(f"Number of shared rooms found: {len(shared_rooms)}")
            
            # Let's also check what properties this owner has that are sharing-enabled
            sharing_enabled_properties = pd.read_sql_query("""
                SELECT property_id, street, city, sharing_allowed
                FROM Property
                WHERE owner_id = ? AND sharing_allowed = 1
            """, conn, params=(homeowner['owner_id'],))
            
            st.write("Properties with sharing enabled:")
            st.dataframe(sharing_enabled_properties)
            
            if not shared_rooms.empty:
                st.write("Found shared rooms:")
                st.dataframe(shared_rooms)
                
                # Display shared rooms with interactive elements
                for idx, room in shared_rooms.iterrows():
                    with st.expander(f"{room['property_type']} at {room['building']}, {room['street']}, {room['city']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Room ID:** {room['room_id']}")
                            st.write(f"**Property ID:** {room['property_id']}")
                            st.write(f"**Available Beds:** {room['available_beds']}/{room['total_beds']}")
                            st.write(f"**Monthly Rent per Bed:** ${room['monthly_rent']:,.2f}")
                            st.write(f"**Total Property Rent:** ${room['rent']:,.2f}")
                        with col2:
                            st.write("**Property Description:**")
                            st.write(room['description'])
                        
                        # Show interested customers
                        st.subheader("Interested Customers")
                        interested_customers = pd.read_sql_query("""
                            SELECT 
                                c.first_name,
                                c.last_name,
                                c.email,
                                c.phone
                            FROM Interested_In_Sharing iis
                            JOIN Customer c ON iis.customer_id = c.customer_id
                            WHERE iis.room_id = ?
                        """, conn, params=(room['room_id'],))
                        
                        if not interested_customers.empty:
                            st.dataframe(interested_customers)
                        else:
                            st.info("No customers have shown interest in this room yet.")
                        
                        # Add management buttons
                        if st.button("Remove from Sharing", key=f"remove_sharing_{room['room_id']}"):
                            try:
                                cur = conn.cursor()
                                cur.execute("DELETE FROM SharedRoom WHERE room_id = ?", (room['room_id'],))
                                conn.commit()
                                st.success("Room removed from sharing!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error removing room from sharing: {str(e)}")
            else:
                st.info("You haven't added any shared rooms yet. You can add shared rooms by enabling sharing when adding a new property.")
        except Exception as e:
            st.error(f"Error fetching shared rooms: {str(e)}")
            import traceback
            st.error(traceback.format_exc())

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
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Properties for Rent", "🏢 Properties for Sale", "🏠 Shared Rooms", "📋 Recent Purchases"])

    with tab1:
        st.subheader("Available Rental Properties")
        
        # Filter options for rental properties
        col1, col2, col3 = st.columns(3)
        with col1:
            property_type = st.selectbox("Property Type", ["All", "apartment", "house", "condo", "villa", "room"], key="rental_property_type")
        with col2:
            min_rent = st.number_input("Minimum Rent", min_value=0, step=100)
        with col3:
            max_rent = st.number_input("Maximum Rent", min_value=min_rent, step=100)
        
        # Build query for rental properties
        query = """
            SELECT p.*, h.first_name || ' ' || h.last_name AS owner_name
            FROM Property p
            JOIN HomeOwner h ON p.owner_id = h.owner_id
            WHERE p.is_available = 1 AND p.sale_renting = 'rent'
        """
        params = []
        
        # Only add property type filter if a specific type is selected
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
                cols = st.columns(3)
                for idx, prop in properties.iterrows():
                    with cols[idx % 3]:
                        # Get a random image for the property type
                        property_type = prop['property_type'].lower()
                        if property_type == 'apartment':
                            image_url = PROPERTY_IMAGES[0]  # Modern apartment
                        elif property_type == 'house':
                            image_url = PROPERTY_IMAGES[5]  # Modern house
                        elif property_type == 'condo':
                            image_url = PROPERTY_IMAGES[10]  # Modern condo
                        elif property_type == 'villa':
                            image_url = PROPERTY_IMAGES[15]  # Luxury villa
                        elif property_type == 'room':
                            image_url = PROPERTY_IMAGES[20]  # Modern room
                        else:
                            # Default to first image if property type doesn't match
                            image_url = PROPERTY_IMAGES[0]
                        
                        # Create a unique key for each property's buttons
                        rent_key = f"rent_{prop['property_id']}"
                        share_key = f"share_{prop['property_id']}"
                        view_key = f"view_{prop['property_id']}"
                        
                        st.markdown(f"""
                            <div style='padding: 10px; 
                                    border-radius: 10px; 
                                    background-color: #1E1E1E; 
                                    color: #FFFFFF; 
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.3); 
                                    margin-bottom: 10px;'>
                                <img src="{image_url}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 5px; margin-bottom: 10px;">
                                <h4 style='color: #FFFFFF;'>{property_type.title()}</h4>
                                <p><strong>Location:</strong> {prop['street']}, {prop['city']}</p>
                                <p><strong>Price:</strong> ${float(prop['cost']):,.2f}</p>
                                <p><strong>Owner:</strong> {prop['owner_name']}</p>
                                <p><strong>Area:</strong> {prop['area']} sq ft</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Add buttons in a row
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("Rent Now", key=rent_key):
                                try:
                                    cur = conn.cursor()
                                    # Add to Buy_Rent table
                                    cur.execute("""
                                        INSERT INTO Buy_Rent (customer_id, property_id)
                                        VALUES (?, ?)
                                    """, (customer['customer_id'], prop['property_id']))
                                    
                                    # Add to Receipt table
                                    cur.execute("""
                                        INSERT INTO Receipt (property_id, customer_id, amount, payment_status, payment_date)
                                        VALUES (?, ?, ?, 'completed', DATE('now'))
                                    """, (prop['property_id'], customer['customer_id'], prop['rent']))
                                    
                                    # Update property availability
                                    cur.execute("""
                                        UPDATE Property 
                                        SET is_available = 0 
                                        WHERE property_id = ?
                                    """, (prop['property_id'],))
                                    
                                    conn.commit()
                                    st.success(f"You have successfully rented {prop['property_type']} at {prop['street']}, {prop['city']}!")
                                except Exception as e:
                                    st.error(f"Error processing rental: {e}")
                        
                        with col2:
                            if st.button("Share Room", key=share_key):
                                if prop['sale_renting'] == 'rent' and prop['is_available'] == 1:
                                    try:
                                        cur = conn.cursor()
                                        cur.execute("SELECT * FROM SharedRoom WHERE property_id = ?", (prop['property_id'],))
                                        if not cur.fetchone():
                                            cur.execute("""
                                                INSERT INTO SharedRoom (property_id, total_beds, available_beds, monthly_rent)
                                                VALUES (?, 2, 2, ?)
                                            """, (prop['property_id'], prop['rent'] / 2))
                                            conn.commit()
                                            st.success(f"Room added to shared rooms! Monthly rent per bed: ${prop['rent'] / 2:.2f}")
                                        else:
                                            st.info("This property is already available as a shared room.")
                                    except Exception as e:
                                        st.error(f"Error adding to shared rooms: {e}")
                                else:
                                    st.warning("This property is not available for renting. Only properties available for rent can be shared.")
                        
                        with col3:
                            show_details = st.button("View More", key=view_key)
                        
                        if show_details:
                            st.markdown(f"""
                                <div style='padding: 15px; 
                                        border-radius: 10px; 
                                        background-color: #2A2A2A; 
                                        color: #FFFFFF; 
                                        box-shadow: 0 4px 8px rgba(0,0,0,0.3); 
                                        margin: 10px 0 20px 0;
                                        border: 1px solid #444;
                                        width: 100%;'>
                                    <h3 style='color: #FFFFFF; margin-bottom: 15px; border-bottom: 1px solid #444; padding-bottom: 10px;'>
                                        Detailed Information
                                    </h3>
                                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                                        <div>
                                            <p><strong>Property ID:</strong> {prop['property_id']}</p>
                                            <p><strong>Property Type:</strong> {property_type.title()}</p>
                                            <p><strong>Location:</strong> {prop['street']}, {prop['city']}</p>
                                        </div>
                                        <div>
                                            <p><strong>Price:</strong> ${float(prop['cost']):,.2f}</p>
                                            <p><strong>Owner:</strong> {prop['owner_name']}</p>
                                            <p><strong>Area:</strong> {prop['area']} sq ft</p>
                                        </div>
                                    </div>
                                    <div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid #444;'>
                                        <p><strong>Description:</strong></p>
                                        <p style='background-color: #1E1E1E; padding: 10px; border-radius: 5px;'>{prop['description']}</p>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No rental properties match your criteria.")
        except Exception as e:
            st.error(f"Error fetching rental properties: {e}")

    with tab2:
        st.subheader("Properties for Sale")
        
        # Filter options for sale properties
        col1, col2, col3 = st.columns(3)
        with col1:
            sale_property_type = st.selectbox("Property Type", ["All", "apartment", "house", "condo", "villa", "room"], key="sale_property_type")
        with col2:
            min_price = st.number_input("Minimum Price", min_value=0, step=10000, key="min_sale_price")
        with col3:
            max_price = st.number_input("Maximum Price", min_value=min_price, step=10000, key="max_sale_price")
        
        # Build query for sale properties
        sale_query = """
            SELECT p.*, h.first_name || ' ' || h.last_name AS owner_name
            FROM Property p
            JOIN HomeOwner h ON p.owner_id = h.owner_id
            WHERE p.is_available = 1 AND p.sale_renting = 'sale'
        """
        sale_params = []
        
        if sale_property_type != "All":
            sale_query += " AND p.property_type = ?"
            sale_params.append(sale_property_type)
        
        if min_price > 0:
            sale_query += " AND p.cost >= ?"
            sale_params.append(min_price)
        
        if max_price > min_price:
            sale_query += " AND p.cost <= ?"
            sale_params.append(max_price)
        
        try:
            sale_properties = pd.read_sql_query(sale_query, conn, params=sale_params)
            if not sale_properties.empty:
                cols = st.columns(3)
                for idx, prop in sale_properties.iterrows():
                    with cols[idx % 3]:
                        # Get a random image for the property type
                        property_type = prop['property_type'].lower()
                        if property_type == 'apartment':
                            image_url = PROPERTY_IMAGES[0]  # Modern apartment
                        elif property_type == 'house':
                            image_url = PROPERTY_IMAGES[5]  # Modern house
                        elif property_type == 'condo':
                            image_url = PROPERTY_IMAGES[10]  # Modern condo
                        elif property_type == 'villa':
                            image_url = PROPERTY_IMAGES[15]  # Luxury villa
                        elif property_type == 'room':
                            image_url = PROPERTY_IMAGES[20]  # Modern room
                        else:
                            # Default to first image if property type doesn't match
                            image_url = PROPERTY_IMAGES[0]
                        
                        # Create unique keys for buttons
                        buy_key = f"buy_{prop['property_id']}"
                        view_key = f"view_sale_{prop['property_id']}"
                        
                        st.markdown(f"""
                                <div style='padding: 10px; 
                                    border-radius: 10px; 
                                    background-color: #1E1E1E; 
                                    color: #FFFFFF; 
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.3); 
                                    margin-bottom: 10px;'>
                                <img src="{image_url}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 5px; margin-bottom: 10px;">
                                <h4 style='color: #FFFFFF;'>{property_type.title()}</h4>
                                <p><strong>Location:</strong> {prop['street']}, {prop['city']}</p>
                                <p><strong>Price:</strong> ${prop['cost']:,.2f}</p>
                                <p><strong>Owner:</strong> {prop['owner_name']}</p>
                                <p><strong>Area:</strong> {prop['area']} sq ft</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Add buttons in a row
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Buy Now", key=buy_key):
                                try:
                                    cur = conn.cursor()
                                    # Add to Buy_Rent table
                                    cur.execute("""
                                        INSERT INTO Buy_Rent (customer_id, property_id)
                                        VALUES (?, ?)
                                    """, (customer['customer_id'], prop['property_id']))
                                    
                                    # Add to Receipt table
                                    cur.execute("""
                                        INSERT INTO Receipt (property_id, customer_id, amount, payment_status, payment_date)
                                        VALUES (?, ?, ?, 'completed', DATE('now'))
                                    """, (prop['property_id'], customer['customer_id'], prop['cost']))
                                    
                                    # Update property availability
                                    cur.execute("""
                                        UPDATE Property 
                                        SET is_available = 0 
                                        WHERE property_id = ?
                                    """, (prop['property_id'],))
                                    
                                    conn.commit()
                                    st.success(f"You have successfully purchased {property_type.title()} at {prop['street']}, {prop['city']}!")
                                except Exception as e:
                                    st.error(f"Error processing purchase: {e}")
                        
                        with col2:
                            if st.button("View Details", key=view_key):
                                st.markdown(f"""
                                    <div style='padding: 15px; 
                                            border-radius: 10px; 
                                            background-color: #2A2A2A; 
                                            color: #FFFFFF; 
                                            box-shadow: 0 4px 8px rgba(0,0,0,0.3); 
                                            margin: 10px 0 20px 0;
                                            border: 1px solid #444;
                                            width: 100%;'>
                                        <h3 style='color: #FFFFFF; margin-bottom: 15px; border-bottom: 1px solid #444; padding-bottom: 10px;'>
                                            Detailed Information
                                        </h3>
                                        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                                            <div>
                                                <p><strong>Property ID:</strong> {prop['property_id']}</p>
                                                <p><strong>Property Type:</strong> {property_type.title()}</p>
                                                <p><strong>Location:</strong> {prop['street']}, {prop['city']}</p>
                                            </div>
                                            <div>
                                                <p><strong>Price:</strong> ${prop['cost']:,.2f}</p>
                                                <p><strong>Owner:</strong> {prop['owner_name']}</p>
                                                <p><strong>Area:</strong> {prop['area']} sq ft</p>
                                            </div>
                                        </div>
                                        <div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid #444;'>
                                            <p><strong>Description:</strong></p>
                                            <p style='background-color: #1E1E1E; padding: 10px; border-radius: 5px;'>{prop['description']}</p>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("No properties for sale match your criteria.")
        except Exception as e:
            st.error(f"Error fetching properties for sale: {e}")

    with tab3:
        st.subheader("Available Shared Rooms")
        
        try:
            shared_rooms = pd.read_sql_query("""
                SELECT 
                    sr.*,
                    p.street,
                    p.city,
                    p.rent,
                    p.property_type,
                    p.description,
                    p.building
                FROM SharedRoom sr
                JOIN Property p ON sr.property_id = p.property_id
                WHERE sr.available_beds > 0
            """, conn)
            
            if not shared_rooms.empty:
                # Display shared rooms with interactive elements
                for idx, room in shared_rooms.iterrows():
                    with st.expander(f"Room at {room['street']}, {room['city']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Room ID:** {room['room_id']}")
                            st.write(f"**Property ID:** {room['property_id']}")
                            st.write(f"**Available Beds:** {room['available_beds']}/{room['total_beds']}")
                            st.write(f"**Monthly Rent per Bed:** ${room['monthly_rent']:,.2f}")
                            st.write(f"**Total Property Rent:** ${room['rent']:,.2f}")
                        with col2:
                            if 'description' in room:
                                st.write("**Property Description:**")
                                st.write(room['description'])
                            
                        # Show interested customers
                        st.subheader("Interested Customers")
                        interested_customers = pd.read_sql_query("""
                            SELECT 
                                c.first_name,
                                c.last_name,
                                c.email,
                                c.phone
                            FROM Interested_In_Sharing iis
                            JOIN Customer c ON iis.customer_id = c.customer_id
                            WHERE iis.room_id = ?
                        """, conn, params=(room['room_id'],))
                        
                        if not interested_customers.empty:
                            st.dataframe(interested_customers)
                        else:
                            st.info("No customers have shown interest in this room yet.")
                        
                        # Add "Apply for Room" button
                        if st.button("Apply for Room", key=f"apply_room_{room['room_id']}"):
                            apply_for_sharing(conn, customer, room['room_id'])
            else:
                st.info("No shared rooms are currently available.")
        except Exception as e:
            st.error(f"Error fetching shared rooms: {e}")
    
    with tab4:
        st.subheader("Recent Purchases")
        
        try:
            # Get all purchases (both rent and buy) for the customer with proper joins
            purchases = pd.read_sql_query("""
                SELECT DISTINCT
                    p.property_id,
                    p.property_type,
                    p.street,
                    p.city,
                    p.sale_renting,
                    CASE 
                        WHEN p.sale_renting = 'rent' THEN p.rent
                        ELSE p.cost
                    END as amount,
                    r.payment_date,
                    r.payment_status
                FROM Buy_Rent br
                JOIN Property p ON br.property_id = p.property_id
                JOIN Receipt r ON br.property_id = r.property_id 
                    AND br.customer_id = r.customer_id
                WHERE br.customer_id = ?
                ORDER BY r.payment_date DESC
            """, conn, params=(customer['customer_id'],))
            
            if not purchases.empty:
                # Display purchases in a styled table
                st.markdown("""
                    <style>
                    .purchase-table {
                        background-color: #1E1E1E;
                        border-radius: 10px;
                        padding: 20px;
                        margin: 10px 0;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                for _, purchase in purchases.iterrows():
                    st.markdown(f"""
                        <div class="purchase-table">
                            <h4>{purchase['property_type'].title()} at {purchase['street']}, {purchase['city']}</h4>
                            <p><strong>Type:</strong> {purchase['sale_renting'].title()}</p>
                            <p><strong>Amount:</strong> ${purchase['amount']:,.2f}</p>
                            <p><strong>Date:</strong> {purchase['payment_date']}</p>
                            <p><strong>Status:</strong> {purchase['payment_status'].title()}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("You haven't made any purchases yet.")
        except Exception as e:
            st.error(f"Error fetching purchases: {e}")

def apply_for_sharing(conn, customer, room_id):
    try:
        cur = conn.cursor()
        
        # First check if customer has already applied for this room
        cur.execute("""
            SELECT 1 FROM Interested_In_Sharing 
            WHERE customer_id = ? AND room_id = ?
        """, (customer['customer_id'], room_id))
        
        if cur.fetchone():
            st.warning("You have already applied for this room.")
            return
        
        # Check if room has available beds
        cur.execute("SELECT available_beds FROM SharedRoom WHERE room_id = ?", (room_id,))
        result = cur.fetchone()
        
        if result and result[0] > 0:
            # Add to Interested_In_Sharing table
            cur.execute("""
                INSERT INTO Interested_In_Sharing (customer_id, room_id)
                VALUES (?, ?)
            """, (customer['customer_id'], room_id))
            
            # Update available beds
            cur.execute("""
                UPDATE SharedRoom 
                SET available_beds = available_beds - 1 
                WHERE room_id = ?
            """, (room_id,))
            
            # Add to Receipt table
            cur.execute("""
                INSERT INTO Receipt (property_id, customer_id, amount, payment_status, payment_date)
                SELECT sr.property_id, ?, sr.monthly_rent, 'completed', DATE('now')
                FROM SharedRoom sr
                WHERE sr.room_id = ?
            """, (customer['customer_id'], room_id))
            
            conn.commit()
            st.success("Successfully applied for the shared room!")
        else:
            st.warning("Sorry, this room is already full.")
    except Exception as e:
        st.error(f"Error applying for shared room: {e}")

def sign_up(conn):
    st.title("📝 Sign Up")
    st.markdown("---")
    
    # Create tabs for different user types
    tab1, tab2 = st.tabs(["👤 Customer", "🏠 Homeowner"])
    
    with tab1:
        st.subheader("Customer Registration")
        with st.form("customer_signup_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            
            if st.form_submit_button("Sign Up as Customer"):
                if not username or not password or not confirm_password or not first_name or not last_name or not email or not phone:
                    st.error("All fields are required.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        # Check if username already exists
                        cur = conn.cursor()
                        cur.execute("SELECT username FROM Credentials WHERE username = ?", (username,))
                        if cur.fetchone():
                            st.error("Username already exists. Please choose another.")
                        else:
                            # Insert into Credentials table
                            cur.execute("INSERT INTO Credentials (username, password, user_type) VALUES (?, ?, 'customer')", 
                                      (username, password))
                            
                            # Get the customer_id (should be the same as the last row id)
                            cur.execute("SELECT last_insert_rowid()")
                            customer_id = cur.fetchone()[0]
                            
                            # Insert into Customer table
                            cur.execute("""
                                INSERT INTO Customer (customer_id, username, first_name, last_name, email, phone)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (customer_id, username, first_name, last_name, email, phone))
                            
                            conn.commit()
                            st.success("Customer account created successfully! You can now log in.")
                    except Exception as e:
                        st.error(f"Error creating account: {e}")
    
    with tab2:
        st.subheader("Homeowner Registration")
        with st.form("homeowner_signup_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            phone_number = st.text_input("Phone Number")
            
            if st.form_submit_button("Sign Up as Homeowner"):
                if not username or not password or not confirm_password or not first_name or not last_name or not email or not phone_number:
                    st.error("All fields are required.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        # Check if username already exists
                        cur = conn.cursor()
                        cur.execute("SELECT username FROM Credentials WHERE username = ?", (username,))
                        if cur.fetchone():
                            st.error("Username already exists. Please choose another.")
                        else:
                            # Insert into Credentials table
                            cur.execute("INSERT INTO Credentials (username, password, user_type) VALUES (?, ?, 'owner')", 
                                      (username, password))
                            
                            # Get the owner_id (should be the same as the last row id)
                            cur.execute("SELECT last_insert_rowid()")
                            owner_id = cur.fetchone()[0]
                            
                            # Insert into HomeOwner table
                            cur.execute("""
                                INSERT INTO HomeOwner (owner_id, username, first_name, last_name, email, phone_number, verification_status)
                                VALUES (?, ?, ?, ?, ?, ?, 'pending')
                            """, (owner_id, username, first_name, last_name, email, phone_number))
                            
                            conn.commit()
                            st.success("Homeowner account created successfully! You can now log in. Note: Your account will be pending verification by an admin.")
                    except Exception as e:
                        st.error(f"Error creating account: {e}")

# -------------------------
# 3. Main App: Login and Routing
# -------------------------
def main():
    st.title("RealEstateHub: Rent, Share, Own")

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
        # Create tabs for login and signup
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
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
        
        with tab2:
            sign_up(conn)
            
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